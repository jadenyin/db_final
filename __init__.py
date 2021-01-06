import sqlalchemy
from sqlalchemy import  create_engine
from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy import Column,Integer,String #区分大小写

engine = create_engine('postgresql+psycopg2://postgres:yyj0010YYJ@localhost/bookstore',encoding="utf-8",echo=True)
metadata=MetaData()
metadata.create_all(engine)
