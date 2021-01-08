from flask import Flask
from view import auth
from view import seller
app = Flask(__name__)

app.register_blueprint(auth.bp_auth)
app.register_blueprint(seller.bp_seller)

if __name__ == '__main__':
    app.run()
