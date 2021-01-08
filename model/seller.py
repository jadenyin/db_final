from be.model import create_table as ct
from be.model import session
from be.model import error
import json


class Seller(session.ORMsession):
    def __init__(self):
        session.ORMsession.__init__(self)

    def create_store(self, user_id: str, store_id: str) -> (int, str):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if self.store_id_exist(store_id):
                return error.error_exist_store_id(store_id)
            user_store_obj = ct.User_store(user_id=user_id, store_id=store_id)
            self.db_session.add(user_store_obj)
            self.db_session.commit()
        except BaseException as e:
            self.db_session.rollback()
            return 530, "{}".format(str(e))
        return 200, "ok"

    def add_book(self, user_id: str, store_id: str, book_id: str, book_json_str: str, stock_level: int):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if self.book_id_exist(store_id, book_id):
                return error.error_exist_book_id(book_id)
            store_obj = ct.Store(store_id=store_id, book_id=book_id, book_info=book_json_str, stock_level=stock_level)
            self.db_session.add(store_obj)

            # 在book表中添加书本信息
            book_info = json.loads(book_json_str)
            row = self.db_session.query(ct.Book).filter(ct.Book.book_id == book_info["book_id"]).first()
            if not row:
                book_obj = ct.Book(book_info["book_id"], book_info["title"], book_info['publisher'],
                                   book_info["original_title"], book_info["translator"], book_info["pub_year"],
                                   book_info["pages"], book_info["price"], book_info["binding"], book_info["isbn"],
                                   book_info["author_intro"], book_info["book_intro"], book_info["content"],
                                   book_info["tags"][0], book_info["tags"][1], book_info["tags"][2])
                self.db_session.add(book_obj)
            self.db_session.commit()
        except BaseException as e:
            self.db_session.rollback()
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
            self.db_session.query(ct.Store).filter(ct.Store.store_id == store_id, ct.Store.book_id == book_id).update(
                {ct.Store.stock_level: ct.Store.stock_level + add_level})
            self.db_session.commit()
        except BaseException as e:
            self.db_session.rollback()
            return 530, "{}".format(str(e))
        return 200, "ok"
