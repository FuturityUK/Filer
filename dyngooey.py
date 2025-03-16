
from collections.abc import Iterable
import gooey
from gooey import GooeyParser # Even though this is greyed out as unused, its actually imported indirectly by the GUI application
from gooey.gui import seeder as gooey_seeder
import gooey.gui.components.widgets as gooey_widgets
import json
import subprocess
import sys
import logging

import os
import re
#import wx.lib.agw.multidirdialog as MDD
from gooey.gui.components.widgets.core import MultiDirChooser as gooey_MultiDirChooser

# --------------------------------------------------------------------------- #

GOOEY_SEED_UI = "gooey-seed-ui"
GOOEY_IGNORE = "--ignore-gooey"

logging.getLogger(__name__).disabled = True
logger = logging.getLogger(__name__)
# --------------------------------------------------------------------------- #

def Gooey(**kwargs):
    logger.debug(f"### Dyngooey.Gooey() ###")
    """Gooey decorator with forcibly enabled dynamic updates"""
    _kwargs = kwargs.copy()
    _kwargs.pop("poll_external_updates", None)
    return gooey.Gooey(**_kwargs, poll_external_updates=True)

# --------------------------------------------------------------------------- #

def gooey_stdout():
    logger.debug(f"### Dyngooey.gooey_stdout() ###")
    """Helper to get "real stdout while seeding"""
    return __stdout

def gooey_id(action):
    logger.debug(f"### Dyngooey.gooey_id() ###")
    """Helper to get Gooey Widget Id from parser action"""
    # Matches against the first defined option, as in '-h' if both '-h' & '--help' provided
    # Falls back to dest for non optional parameters
    if action.option_strings:
        return action.option_strings[0]
    else:
        return action.dest

# --------------------------------------------------------------------------- #

# NOTE: Dynamic updates are experimental and rely on the correct JSON output of
#       this program when it is called with a single argument 'gooey-seed-ui'!
#       Therefore it save the standard output stream to "stdout". The standard
#       output stream will then be redirected to standard error and ONLY the
#       JSON answer for Gooey will be returned via standard output!

__stdout = sys.__stdout__ if GOOEY_SEED_UI in sys.argv else None
if __stdout: sys.stdout = sys.stderr


# --------------------------------------------------------------------------- #

# NOTE: Below we will monkey patch Gooey's dynamic update function to
#       supplement it with proper error feedback
def __fetchDynamicProperties(target, encoding):
    logger.info(f"### Dyngooey.__fetchDynamicProperties() ###")
    cmd = '{} {}'.format(target, " ".join([GOOEY_SEED_UI, GOOEY_IGNORE]))
    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
    )
    if proc.returncode != 0:
        out, err = proc.communicate()
        out = out.decode(encoding)
        err = err.decode(encoding)
        try:
            return json.loads(out)
        except Exception as e:
            msg = f"Error during dynamic update:"
            print(f"{msg} - {type(e).__name__}: {e}\n{out}\n{err}")
            return {}
    else:
        return {}
gooey_seeder.fetchDynamicProperties = __fetchDynamicProperties


# --------------------------------------------------------------------------- #

# NOTE: Here we will monkey patch Gooey widgets to support dynamic updates
#       of both items *AND* values

# TextContainer widget
def __setTextContainerOptions(_self, options):
    logger.info(f"### Dyngooey.__setTextContainerOptions() ###")
    default = _self._options.get("initial_value", "")
    if isinstance(options, str) or not isinstance(options, Iterable):
        value = options
        _self.setValue(default if value is None else value)
    elif isinstance(options, dict):
        if "value" in options:
            value = options["value"]
            _self.setValue(default if value is None else value)
setattr(gooey_widgets.bases.TextContainer, "setOptions", __setTextContainerOptions)

# CheckBox widget
def __setCheckBoxOptions(_self, options):
    logger.info(f"### Dyngooey.__setCheckBoxOptions() ###")
    default = _self._options.get("initial_value", bool(_self._meta["default"]))
    if isinstance(options, str) or not isinstance(options, Iterable):
        value = options
        _self.setValue(default if value is None else value)
    elif isinstance(options, dict):
        if "value" in options:
            value = options["value"]
            _self.setValue(default if value is None else value)
setattr(gooey_widgets.checkbox.CheckBox, "setOptions", __setCheckBoxOptions)

# Dropdown widget
def __setDropdownOptions(_self, options):
    logger.info(f"### Dyngooey.__setDropdownOptions() ###")
    logger.info("")
    logger.info(f"_self: {_self.__dict__['info']['id']}")
    logger.info(f"options: {options}")
    logger.info(f"_self._options: {_self._options}")
    logger.info("")

    _ = gooey_widgets.dropdown._
    #logger.info(f"_('select_option'): {_('select_option')}")

    get = lambda v,n: n if v is None else v
    default = _self._options.get("initial_value", None)
    """
    if isinstance(options, str) or not isinstance(options, Iterable):
        value = get(options, default)
        if value is None:
            _self.widget.SetSelection(0)
        else:
            _self.setValue(value)
    el
    """
    if isinstance(options, list):
        logger.info("list")
        _self.widget.Clear()
        #_self.widget.SetItems([_('select_option')] + get(options, []))
        _self.widget.SetItems(get(options, []))
    elif isinstance(options, dict):
        logger.info("dict")
        items_array = []
        if "items" in options:
            logger.info("dict-items")
            #with _self.retainSelection():
            _self.widget.Clear()
            #items_array = [_('select_option')] + get(options["items"], [])
            items_array = get(options["items"], [])
            _self.widget.SetItems(items_array)
        if "value" in options:
            logger.info("dict-value")
            value = get(options["value"], default)
            logger.info("dict-value: " + str(value) + "")
            logger.info(f"_self.widget: {_self.widget.__dict__}")
            _self.widget.SetSelection(1)
            for i in range(len(items_array)):
                if items_array[i] == value:
                    _self.widget.SetSelection(i)
                    break
            """
            if value is None:
                _self.widget.SetSelection(0)
            else:
                _self.setValue(value)
            """
    # Moved from the start of the IF statement to the bottom, because you can't set the
    # DROPDOWN / CHOICE default, if the ITEMS / CHOICES haven't been populated yet.
    elif isinstance(options, str) or not isinstance(options, Iterable):
        logger.info("str or not Iterable")
        value = get(options, default)
        if value is None:
            _self.widget.SetSelection(0)
        else:
            _self.setValue(value)
    logger.info(f"### Dyngooey.__setDropdownOptions() - END ###")

setattr(gooey_widgets.dropdown.Dropdown, "setOptions", __setDropdownOptions)

# Listbox widget
def __setListboxOptions(_self, options):
    logger.info(f"### Dyngooey.__setListboxOptions() ###")
    get = lambda v,n: n if v is None else v
    default = _self._options.get("initial_value", None)
    if isinstance(options, str) or not isinstance(options, Iterable):
        value = get(options, default)
        if value is None:
            _self.widget.SetSelection(0)
        else:
            _self.setValue(value)
    elif isinstance(options, list):
        _self.widget.Clear()
        for option in get(options, []):
            _self.widget.Append(option)
    elif isinstance(options, dict):
        if "items" in options:
            _self.widget.Clear()
            for option in get(options["items"], []):
                _self.widget.Append(option)
        if "value" in options:
            value = get(options["value"], default)
            if value is None:
                _self.widget.SetSelection(0)
            else:
                _self.setValue(value)
setattr(gooey_widgets.listbox.Listbox, "setOptions", __setListboxOptions)

# --------------------------------------------------------------------------- #
# Neil's fix to the MultiDirChooser

def __getResult(self, dialog):
    print(f"### Dyngooey.MultiDirChooser.getResult() ###")
    paths = dialog.GetPaths()
    # Remove volume labels from Windows paths
    if 'nt' == os.name:
        print(f"os.name: {os.name}")
        for i, path in enumerate(paths):
            print(f"path: {path}")
            if path:
                parts = path.split(os.sep)
                print(f"parts: {parts}")
                vol = parts[0]
                print(f"vol: {vol}")
                drives = re.match(r'.*\((?P<drive>\w:)\)', vol)
                print(f"drives: {drives}")
                if drives is not None:
                    paths[i] = os.sep.join([drives.group('drive')] + parts[1:])
    return os.pathsep.join(paths)
gooey_MultiDirChooser.getResult = __getResult

