from flask import Blueprint
from flask import request
from flask import jsonify
from be.model import buyer as Buyer

bp_buyer = Blueprint("buyer", __name__, url_prefix="/buyer")


@bp_buyer.route("/new_order", methods=["POST"])
def new_order():
    # get request's information
    user_id = request.json.get("user_id")
    store_id = request.json.get("store_id")
    books: [] = request.json.get("books")
    # get all book_id and it's count
    bookid_and_count = []
    for book in books:
        bookid_and_count.append((book.get("id"), book.get("count")))
    bu = Buyer.buyer_functions()
    # pass these data to buyer_function and get return
    code, message, order_id = bu.new_order(user_id=user_id, store_id=store_id, bookid_and_count=bookid_and_count)
    return jsonify({"message": message, "order_id": order_id}), code


@bp_buyer.route("/payment", methods=["POST"])
def payment():
    user_id = request.json.get("user_id")
    order_id = request.json.get("order_id")
    password = request.json.get("password")
    bu = Buyer.buyer_functions()
    code, message = bu.payment(user_id, password, order_id)
    return jsonify({"message": message}), code


@bp_buyer.route("/add_funds", methods=["POST"])
def add_fund():
    user_id = request.json.get("user_id")
    password = request.json.get("password")
    add_value = request.json.get("add_value")
    bu = Buyer.buyer_functions()
    code, message = bu.add_money(user_id, password, add_value)
    return jsonify({"message": message}), code


@bp_buyer.route("/deliver_goods", methods=["POST"])
def deliver_goods():
    user_id = request.json.get("user_id")
    order_id = request.json.get("order_id")
    password = request.json.get("password")
    bu = Buyer.buyer_functions()
    code, message = bu.deliver_goods(user_id, password, order_id)
    return jsonify({"message": message}), code


@bp_buyer.route("/receive_goods", methods=["POST"])
def receive_goods():
    user_id = request.json.get("user_id")
    order_id = request.json.get("order_id")
    password = request.json.get("password")
    bu = Buyer.buyer_functions()
    code, message = bu.receive_goods(user_id, password, order_id)
    return jsonify({"message": message}), code


@bp_buyer.route("/browse_orders", methods=["POST"])
def browser_orders():
    user_id = request.json.get("user_id")
    mode = request.json.get("mode")
    bu = Buyer.buyer_functions()
    # mode 0表示查看所有订单
    if int(mode) == 0:
        code, message = bu.browser_all_orders(user_id)
    # mode 1表示查看历史订单
    else:
        code, message = bu.browser_history_orders(user_id)
    return jsonify({"message": message}), code


@bp_buyer.route("/cancel_orders", methods=["POST"])
def cancel_orders():
    user_id = request.json.get("user_id")
    order_id = request.json.get("order_id")
    bu = Buyer.buyer_functions()
    code, message = bu.cancel_order(user_id, order_id)
    return jsonify({"message": message}), code


@bp_buyer.route("/retrieve", methods=["POST"])
def retrieve():
    key_word = request.json.get("key_word", "")
    term = request.json.get("term", "")
    store_id = request.json.get("store_id", "")
    b = Buyer.buyer_functions()
    code, message, id_and_stock = b.retrieve(key_word=key_word, term=term, store_id=store_id)
    return jsonify({"message": message, "book": id_and_stock}), code
