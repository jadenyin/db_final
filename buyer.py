from flask import Blueprint
from flask import request
from flask import jsonify
import buyer_function as Buyer

bp_buyer = Blueprint("buyer", __name__, url_prefix="/buyer")

@bp_buyer.route("/new_order", methods=["POST"])
def new_order():
    #get request's information
    user_id: str = request.json.get("user_id")
    store_id: str= request.json.get("store_id")
    books: [] = request.json.get("books")

    #get all book_id and it's count
    bookid_and_count = []
    for book in books:
        bookid_and_count.append((book.get("id"), book.get("count")))

    #pass these data to buyer_function and get return
    message,order_id=Buyer.new_order(user_id,store_id,bookid_and_count)
    return jsonify({"message": message, "order_id": order_id})
