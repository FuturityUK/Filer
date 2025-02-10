
from collections.abc import Iterable
import gooey
from gooey import GooeyParser
from gooey.gui import seeder as gooey_seeder
import gooey.gui.components.widgets as gooey_widgets
import json
import subprocess
import sys


# --------------------------------------------------------------------------- #

GOOEY_SEED_UI = "gooey-seed-ui"
GOOEY_IGNORE = "--ignore-gooey"


# --------------------------------------------------------------------------- #

def Gooey(**kwargs):
    """Gooey decorator with forcibly enabled dynamic updates"""
    _kwargs = kwargs.copy()
    _kwargs.pop("poll_external_updates", None)
    return gooey.Gooey(**_kwargs, poll_external_updates=True)


# --------------------------------------------------------------------------- #

def gooey_stdout():
    """Helper to get "real stdout while seeding"""
    return __stdout

def gooey_id(action):
    """Helper to get Gooey Widget Id from parser action"""
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
    _ = gooey_widgets.dropdown._
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
        _self.widget.SetItems([_('select_option')] + get(options, []))
    elif isinstance(options, dict):
        if "items" in options:
            with _self.retainSelection():
                _self.widget.Clear()
                _self.widget.SetItems([_('select_option')] + get(options["items"], []))
        if "value" in options:
            value = get(options["value"], default)
            if value is None:
                _self.widget.SetSelection(0)
            else:
                _self.setValue(value)
setattr(gooey_widgets.dropdown.Dropdown, "setOptions", __setDropdownOptions)

# Listbox widget
def __setListboxOptions(_self, options):
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
