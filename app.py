from flask import Flask
import buyer
from flask import Blueprint
from flask import request
from flask import jsonify
import buyer_function as Buyer
app = Flask(__name__)
@app.route('/', methods=["POST"])
def hello_world():
    print("1")
    return jsonify({"message": 'hello', "code": 200})

if __name__ == '__main__':
    app = Flask(__name__)
    app.register_blueprint(buyer.bp_buyer)
    app.run()
