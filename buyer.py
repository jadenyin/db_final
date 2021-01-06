from flask import Blueprint
from flask import request
from flask import jsonify
import buyer_function as Buyer

bp_buyer = Blueprint("buyer", __name__, url_prefix="/buyer")

@bp_buyer.route("/new_order", methods=["POST"])
def new_order():
    #get request's information
    user_id= request.json.get("user_id")
    store_id= request.json.get("store_id")
    books= request.json.get("books")
    #get all book_id and it's count
    bookid_and_count = []
    for book in books:
        bookid_and_count.append((book.get("id"), book.get("count")))

    #pass these data to buyer_function and get return
    code,message,order_id=Buyer.new_order(user_id,store_id,bookid_and_count)
    return jsonify({"message": message, "order_id": order_id}),code

@bp_buyer.route("/payment", methods=["POST"])
def payment():
    user_id = request.json.get("user_id")
    order_id  = request.json.get("order_id")
    password = request.json.get("password")
    code,message = Buyer.payment(user_id, password, order_id)
    return jsonify({"message": message}), code


@bp_buyer.route("/add_fund", methods=["POST"])
def add_fund():
    user_id = request.json.get("user_id")
    password = request.json.get("password")
    add_value = request.json.get("add_value")
    code, message = Buyer.add_money(user_id, password, add_value)
    return jsonify({"message": message}), code

#deliver goods interface,:
#user_id:string, seller's id
#password:string, seller's password
#order_id:string, order's id
@bp_buyer.route("/deliver_goods", methods=["POST"])
def deliver_goods():
    user_id = request.json.get("user_id")
    order_id = request.json.get("order_id")
    password = request.json.get("password")
    code, message = Buyer.deliver_goods(user_id, password, order_id)
    return jsonify({"message": message}), code

#receive goods interface,:
#user_id:string, buyer's id
#password:string, buyer's password
#order_id:string, order's id
@bp_buyer.route("/receive_goods", methods=["POST"])
def receive_goods():
    user_id = request.json.get("user_id")
    order_id = request.json.get("order_id")
    password = request.json.get("password")
    code, message = Buyer.receive_goods(user_id, password, order_id)
    return jsonify({"message": message}), code