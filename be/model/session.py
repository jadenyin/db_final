from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from be.model import create_table as ct


class ORMsession:
    def __init__(self):
        engine = create_engine('postgresql+psycopg2://postgres:yyj0010YYJ@localhost/bookstore', encoding='utf-8',
                               echo=True)
        Session = sessionmaker(engine)
        self.db_session = Session()

    def user_id_exist(self, user_id):
        row=self.db_session.query(ct.User).filter(ct.User.user_id==user_id).first()
        if row is None:
            return False
        else:
            return True

    def book_id_exist(self, store_id, book_id):
        row = self.db_session.query(ct.Store).filter(ct.Store.store_id==store_id, ct.Store.book_id==book_id).first()
        if row is None:
            return False
        else:
            return True

    def store_id_exist(self, store_id):
        row = self.db_session.query(ct.User_store).filter(ct.User_store.store_id==store_id).first()
        if row is None:
            return False
        else:
            return True

    def order_id_exist(self, user_id, order_id):
        row = self.db_session.query(ct.New_order).filter(ct.New_order.order_id == order_id,
                                                         ct.New_order.user_id == user_id).first()
        if row is None:
            return False
        else:
            return True

