from model.create_table import Store
from model.create_table import Book
import logging
from model import session
from sqlalchemy import or_
from model import error
import random
import string
import jwt
import time


def page_split(id_and_stock, split_num):
    result = []
    num = len(id_and_stock)
    pages = int((num + split_num-1) / split_num)
    for index in range(pages):
        start = split_num * index
        if (start + split_num) >= num:
            break
        page = id_and_stock[start:start + split_num]
        result.append(page)
    result.append(id_and_stock[split_num * (pages - 1):])
    return result

class Buyer(session.ORMsession):

    def __init__(self):
        session.ORMsession.__init__(self)

    def retrieve(self,key_word:str,term:str,store_id:str) -> (int,str,list):
        id_and_stock=[]
        if store_id!='' and not self.store_id_exist(store_id):
            return error.error_non_exist_store_id(store_id)
        if term=='title':
            book_id=self.db_session.query(Book.book_id).filter(Book.title.like('%'+key_word+'%')).all()
            print(book_id)
        elif term=='tag':
            book_id=self.db_session.query(Book.book_id)\
            .filter(or_(Book.tag1==key_word,Book.tag2==key_word,Book.tag3==key_word)).all()
        elif term=='content':
            book_id=self.db_session.query(Book.book_id).filter(Book.content.like('%'+key_word+'%')).all()
        #店铺搜索
        if not len(book_id):
            return error.error_no_book_found()
        if store_id!='':
            for id in book_id:
                id_stock=self.db_session.query(Store.store_id,Store.book_id,Store.stock_level)\
                .filter(Store.book_id==id,Store.store_id==store_id).all()
                if not len(id_stock):
                    return 200, "ok", id_and_stock
                for i in range(len(id_stock)):
                    id_and_stock.append(id_stock[i])
        else:
            for id in book_id:
                id_stock=self.db_session.query(Store.store_id,Store.book_id,Store.stock_level)\
                .filter(Store.book_id==id).all()
                if not len(id_stock):
                    return 200, "ok", id_and_stock
                for i in range(len(id_stock)):
                    print(id_stock[i])
                    id_and_stock.append(id_stock[i])
        if not len(id_and_stock):
            return error.error_no_book_found()
        #分页处理,每页书本数=k
        result=page_split(id_and_stock,10)
        return 200,"ok",result
