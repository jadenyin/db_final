from flask import Blueprint
from flask import request
from flask import jsonify
from model import user
from model import buyer

bp_auth = Blueprint("auth", __name__, url_prefix="/auth")


@bp_auth.route("/register", methods=["POST"])
def register():
    user_id = request.form.get("user_id", "")
    password = request.form.get("password", "")
    u = user.Users()
    code, message = u.register(user_id=user_id, password=password)
    return jsonify({"message": message}), code


@bp_auth.route("/unregister", methods=["POST"])
def unregister():
    user_id = request.form.get("user_id", "")
    password = request.form.get("password", "")
    u = user.Users()
    code, message = u.unregister(user_id=user_id, password=password)
    return jsonify({"message": message}), code


@bp_auth.route("/login", methods=["POST"])
def login():
    user_id = request.form.get("user_id", "")
    password = request.form.get("password", "")
    terminal = request.form.get("terminal", "")
    u = user.Users()
    code, message, token = u.login(user_id=user_id, password=password, terminal=terminal)
    return jsonify({"message": message, "token": token}), code


@bp_auth.route("/updatePWD", methods=["POST"])
def updatePWD():
    user_id = request.form.get("user_id", "")
    old_password = request.form.get("oldPassword", "")
    new_password = request.form.get("newPassword", "")
    u = user.Users()
    code, message = u.change_password(user_id=user_id, old_password=old_password, new_password=new_password)
    return jsonify({"message": message}), code


@bp_auth.route("/logout", methods=["POST"])
def logout():
    user_id = request.form.get("user_id", "")
    token = request.headers.get("token")
    u = user.Users()
    code, message = u.logout(user_id=user_id, token=token)
    return jsonify({"message": message}), code


@bp_auth.route("/retrieve", methods=["POST"])
def retrieve():
    key_word = request.form.get("key_word", "")
    term = request.form.get("term", "")
    store_id = request.form.get("store_id", "")
    b = buyer.Buyer()
    code, message,id_and_stock= b.retrieve(key_word=key_word, term=term, store_id=store_id)
    print(id_and_stock)
    return jsonify({"message": message, "book": id_and_stock}), code
