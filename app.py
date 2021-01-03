from flask import Flask
from View import auth
app = Flask(__name__)

app.register_blueprint(auth.bp_auth)

if __name__ == '__main__':
    app.run()
