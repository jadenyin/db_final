from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, TEXT
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('postgresql+psycopg2://postgres:postgres@localhost/postgres', encoding='utf-8', echo=True)
base = declarative_base()


class User(base):
    __tablename__ = 'user'
    user_id = Column('user_id', TEXT, primary_key=True)
    password = Column('password', TEXT, nullable=False)
    balance = Column('balance', Integer, nullable=False)
    token = Column('token', TEXT)
    terminal = Column('terminal', TEXT)


class User_store(base):
    __tablename__ = 'user_store'
    user_id = Column('user_id', TEXT, primary_key=True)
    store_id = Column('store_id', TEXT, primary_key=True)


class Store(base):
    __tablename__ = 'store'
    store_id = Column('store_id', TEXT, primary_key=True)
    book_id = Column('book_id', TEXT, primary_key=True)
    book_info = Column('book_info', TEXT)
    stock_level = Column('stock_level', Integer)


class New_order(base):
    __tablename__ = 'new_order'
    order_id = Column('order_id', TEXT, primary_key=True)
    user_id = Column('user_id', TEXT)
    store_id = Column('store_id', TEXT)
    state = Column('state', Integer)


class New_order_detail(base):
    __tablename__ = 'new_order_detail'
    order_id = Column('order_id', TEXT, primary_key=True)
    book_id = Column('book_id', TEXT, primary_key=True)
    count = Column('count', Integer)
    price = Column('price', Integer)

class Book(base):
    __tablename__ = 'book'
    book_id = Column('book_id', TEXT, primary_key=True)
    store_id = Column('store_id', TEXT)
    title = Column('title', TEXT)
    publisher = Column('publisher', TEXT)
    original_title = Column('original_title', TEXT)
    translator = Column('translator', TEXT)
    pub_year = Column('pub_year', TEXT)
    pages = Column('pages', Integer)
    price = Column('price', Integer)
    binding = Column('binding', TEXT)
    isbn = Column('isbn', TEXT)
    author_intro = Column('author_intro', TEXT)
    book_intro = Column('book_intro', TEXT)
    content = Column('content', TEXT)
    tag1 = Column('tag1', TEXT)
    tag2 = Column('tag2', TEXT)
    tag3 = Column('tag3', TEXT)


base.metadata.create_all(engine)  # 创建表结构
