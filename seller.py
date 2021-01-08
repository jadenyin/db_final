from model import check as ch
from model import create_table as ct
from model import error
import json


def create_store(user_id, store_id):
    try:
        if not ch.user_id_exist(user_id):
            return error.error_non_exist_user_id(user_id)
        if ch.store_id_exist(store_id):
            return error.error_exist_store_id(store_id)
        user_store_obj = ct.User_store(user_id, store_id)
        ch.session.add(user_store_obj)
        ch.session.commit()
    except BaseException as e:
        ch.session.rollback()
        return 530, "{}".format(str(e))
    return 200, "ok"


def add_book(user_id: str, store_id: str, book_id: str, book_json_str: str, stock_level: int):
    try:
        if not ch.user_id_exist(user_id):
            return error.error_non_exist_user_id(user_id)
        if not ch.store_id_exist(store_id):
            return error.error_non_exist_store_id(store_id)
        if ch.book_id_exist(store_id, book_id):
            return error.error_exist_book_id(book_id)
        store_obj = ct.Store(store_id, book_id, book_json_str, stock_level)
        ch.session.add(store_obj)

        # 在book表中添加书本信息
        book_info = json.loads(book_json_str)
        row = ch.session.query(ct.Book).filter(ct.Book.book_id == book_info["book_id"]).first()
        if not row:
            book_obj = ct.Book(book_info["book_id"], book_info["title"], book_info['publisher'],
                               book_info["original_title"], book_info["translator"], book_info["pub_year"],
                               book_info["pages"], book_info["price"], book_info["binding"], book_info["isbn"],
                               book_info["author_intro"], book_info["book_intro"], book_info["content"],
                               book_info["tags"][0], book_info["tags"][1], book_info["tags"][2])
            ch.session.add(book_obj)
        ch.session.commit()
    except BaseException as e:
        ch.session.rollback()
        return 530, "{}".format(str(e))
    return 200, "ok"


def add_stock_level(self, user_id: str, store_id: str, book_id: str, add_level: int):
    try:
        if not self.user_id_exist(user_id):
            return error.error_non_exist_user_id(user_id)
        if not self.store_id_exist(store_id):
            return error.error_non_exist_store_id(store_id)
        if not self.book_id_exist(store_id, book_id):
            return error.error_non_exist_book_id(book_id)
        ch.session.query(ct.Store).filter(ct.Store.store_id == store_id, ct.Store.book_id == book_id).update(
            {ct.Store.stock_level: ct.Store.stock_level + add_level})
        ch.session.commit()
    except BaseException as e:
        ch.session.rollback()
        return 530, "{}".format(str(e))
    return 200, "ok"

