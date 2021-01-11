from be.model import create_table as ct
from be.model import session
from be.model import error
import json
from sqlalchemy.sql import func
import jieba


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
            book_info = json.loads(book_json_str)
            lst = ["id", "title", "publisher", "original_title", "translator", "pub_year", "pages", "price", "binding", "isbn", "author_intro", "book_intro", "content", "tags"]
            for x in lst:
                if x not in book_info:
                    book_info[x] = ""
            row = self.db_session.query(ct.Book).filter(ct.Book.book_id == book_info["id"]).first()
            if not row:
                segment1=''
                if book_info["content"]!="":
                    seg_list=list(jieba.cut(book_info["content"],cut_all=True))
                    segment1=' '.join(seg_list)
                segment2 = ''
                if book_info["title"] != "":
                    seg_list = list(jieba.cut(book_info["title"], cut_all=True))
                    segment2 = ' '.join(seg_list)
                book_obj = ct.Book(book_id=book_info["id"], title=book_info["title"],
                                   publisher=book_info["publisher"],
                                   original_title=book_info["original_title"], translator=book_info["translator"],
                                   pub_year=book_info["pub_year"], pages=book_info["pages"], price=book_info["price"],
                                   binding=book_info["binding"], isbn=book_info["isbn"],
                                   author_intro=book_info["author_intro"], book_intro=book_info["book_intro"],
                                   content=book_info["content"],tsv_content=segment1,tsv_title=segment2,tags=book_info["tags"])
                self.db_session.add(book_obj)
                if book_info["tags"]!='':
                    for tag in book_info["tags"]:
                        num = self.db_session.query(func.max(ct.Tag_index.search_id)).filter(ct.Tag_index.tag==tag).one()
                        max_num=num[0]
                        if max_num==None:
                            max_num=0
                        else:
                            max_num+=1
                        tag_obj=ct.Tag_index(tag=tag,search_id=max_num,book_id=book_info["id"])
                        self.db_session.add(tag_obj)
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
