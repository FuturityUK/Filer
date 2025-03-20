from flask import Flask
from flask import render_template

app = Flask(__name__)
app.config["DEBUG"] = True


@app.route('/')
def home():
    message = "Hello World!"
    return render_template('index.html',
                           message=message)

@app.route('/about')
def about():
    return render_template('about.html', name='Wibble Wobble')

@app.errorhandler(404)
def not_found(error):
    return "404 Error: Page not found", 404

if __name__ == '__main__':
    app.run()