#!/usr/bin/env python3
from sqlalchemy import create_engine

from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, TEXT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

username='postgres'
password='yyj0010YYJ'
database='bookstore'
engine = create_engine('postgresql+psycopg2://'+username+':'+password+'@localhost/'+database,encoding="utf-8",echo=True)
base = declarative_base()

class User(base):
    __tablename__ = 'users'
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
    tsv_content=Column('tsv_content',TEXT)
    tsv_title=Column('tsv_title',TEXT)
    tags=Column('tags',TEXT)

class Tag_index(base):
    __tablename__='tag_index'
    tag=Column('tag',TEXT,primary_key=True)
    search_id=Column('search_id',Integer,primary_key=True)
    book_id=Column('book_id',TEXT,ForeignKey(Book.book_id),nullable=False)
    book_tag=relationship('Book',cascade='delete')

base.metadata.drop_all(engine)
base.metadata.create_all(engine)  # 创建表结构

#with engine.connect() as conn:
    #conn.execute("create index fulltext_content on book using gin(to_tsvector('english',tsv_content))")
    #conn.execute("create index fulltext_title on book using gin(to_tsvector('english',tsv_title))")
    # conn.execute("delete from users")
    # conn.execute("delete from user_store")
    # conn.execute("delete from store")
    # conn.execute("delete from new_order")
    # conn.execute("delete from new_order_detail")
    # conn.execute("delete from book cascade")
