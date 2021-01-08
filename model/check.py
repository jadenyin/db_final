from model import create_table as ct
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker


db_session_class = scoped_session(sessionmaker(bind=ct.engine))
session = db_session_class()


def user_id_exist(user_id):
    row = session.query(ct.User).filter(ct.User.user_id == user_id).first()
    if row is None:
        return False
    else:
        return True


def book_id_exist(store_id, book_id):
    row = session.query(ct.Store).filter(ct.Store.store_id == store_id, ct.Store.book_id == book_id).first()
    if row is None:
        return False
    else:
        return True


def store_id_exist(store_id):
    row = session.query(ct.User_store).filter(ct.User_store.store_id == store_id).first()
    if row is None:
        return False
    else:
        return True


def order_id_exist(user_id, order_id):
    row = session.query(ct.New_order).filter(ct.New_order.order_id==order_id, ct.New_order.user_id==user_id)
    if row is None:
        return False
    else:
        return True
