from flask import Flask
from View import auth
import buyer
from flask import Blueprint
from flask import request
from flask import jsonify
from View import buyer
app = Flask(__name__)
@app.route('/', methods=["POST"])
def hello_world():
    return jsonify({"message": 'hello', "code": 200})
app = Flask(__name__)

app.register_blueprint(auth.bp_auth)
app.register_blueprint(buyer.bp_buyer)
if __name__ == '__main__':
    app = Flask(__name__)
    app.run()
