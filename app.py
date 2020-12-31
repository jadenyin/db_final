from flask import Flask

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/')
def hello_world():
    return 1

@app.route('/')
def hello_world():
    return 1

if __name__ == '__main__':
    app.run()
