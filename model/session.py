import sqlalchemy
from sqlalchemy import  create_engine
from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
from sqlalchemy import or_
from sqlalchemy import Column,Integer,String

class ORMsession:
    def __init__(self):
        engine = create_engine('postgresql+psycopg2://postgres:yyj0010YYJ@localhost/bookstore', encoding="utf-8",
                               echo=True)
        Session=sessionmaker(engine)
        self.db_session = Session()

    def user_id_exist(self, user_id):
        cursor = self.conn.execute("SELECT user_id FROM user WHERE user_id = ?;", (user_id,))
        row = cursor.fetchone()
        if row is None:
            return False
        else:
            return True

    def book_id_exist(self, store_id, book_id):
        cursor = self.conn.execute("SELECT book_id FROM store WHERE store_id = ? AND book_id = ?;", (store_id, book_id))
        row = cursor.fetchone()
        if row is None:
            return False
        else:
            return True

    def store_id_exist(self, store_id):
        cursor = self.conn.execute("SELECT store_id FROM user_store WHERE store_id = ?;", (store_id,))
        row = cursor.fetchone()
        if row is None:
            return False
        else:
            return True
