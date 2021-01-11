from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, TEXT
from sqlalchemy.ext.declarative import declarative_base
from be.model.create_table import User
import logging
from be.model import session
from be.model import error
import random
import string
import jwt
import time

def random_str(len):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for x in range(len))

def jwt_encode(user_id, terminal):
    encoded = jwt.encode(
        {"user_id": user_id, "terminal": terminal, "timestamp": time.time()},
        key=user_id,
        algorithm='HS256',
    )
    return encoded

def jwt_decode(encoded_token, user_id):
    decoded = jwt.decode(encoded_token, key=user_id, algorithms="HS256")
    return decoded

#Users类,包括注册登录
class Users(session.ORMsession):
    token_lifetime: int = 3600

    def __init__(self):
        session.ORMsession.__init__(self)

    def register(self,user_id:str,password:str) -> (int,str):
        try:
            if self.user_id_exist(user_id):
                return error.error_exist_user_id(user_id)
            terminal = random_str(20)
            token=jwt_encode(user_id,terminal)
            user=User(user_id=user_id,password=password,balance=0,token=token,terminal=terminal)
            self.db_session.add(user)
            self.db_session.commit()
        except BaseException as e:
            self.db_session.rollback()
            return 530, "{}".format(str(e))
        return 200,"ok"

    def unregister(self, user_id: str, password: str) -> (int, str):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            code, message = self.check_password(user_id, password)
            if code != 200:
                return code, message
            user = self.db_session.query(User).filter(User.user_id==user_id).first()
            self.db_session.delete(user)
            self.db_session.commit()
        except BaseException as e:
            self.db_session.rollback()
            return 530, "{}".format(str(e))
        return 200, "ok"

    def check_password(self, user_id: str, password: str) -> (int, str):
        user = self.db_session.query(User).filter(User.user_id==user_id).first()
        if user is None:
            return error.error_non_exist_user_id(user_id)
        if password != user.password:
            return error.error_authorization_fail()
        return 200, "ok"

    def login(self, user_id: str, password: str, terminal: str) -> (int, str, str):
        try:
            if not self.user_id_exist(user_id):
                return error.error_authorization_fail()+("",)
            code, message = self.check_password(user_id, password)
            if code != 200:
                return code, message, ""
            #登陆时需要更新token
            token = jwt_encode(user_id, terminal)
            self.db_session.query(User).filter(User.user_id== user_id).update({'token':token,'terminal':terminal})
            self.db_session.commit()
        except BaseException as e:
            return 530, "{}".format(str(e)), ""
        return 200, "ok", token

    def change_password(self, user_id: str, old_password: str, new_password: str) -> (int,str):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            code, message = self.check_password(user_id, old_password)
            if code != 200:
                return code, message
            terminal = random_str(20)
            #修改密码需要更新token
            token = jwt_encode(user_id, terminal)
            self.db_session.query(User).filter(User.user_id== user_id)\
                .update({'password': new_password,'token': token,'terminal':terminal})
            self.db_session.commit()
        except BaseException as e:
            self.db_session.rollback()
            return 530, "{}".format(str(e))
        return 200, "ok"

    def logout(self, user_id: str, token: str) -> (int,str):
        try:
            if not self.user_id_exist(user_id):
                return error.error_authorization_fail()
            #登陆后的任何操作前都需要进行check_token
            code, message = self.check_token(user_id, token)
            if code != 200:
                return code, message
            terminal = random_str(20)
            new_token = jwt_encode(user_id, terminal)
            self.db_session.query(User).filter(User.user_id== user_id) \
                .update({'terminal': terminal, 'token': new_token})
            self.db_session.commit()
        except BaseException as e:
            self.db_session.rollback()
            return 530, "{}".format(str(e))
        return 200, "ok"

    def check_token(self,user_id:str,token:str) -> (int,str):
        user = self.db_session.query(User).filter(User.user_id==user_id).first()
        if user is None:
            return error.error_non_exist_user_id(user_id)
        if not self.compare_token(user_id,user.token,token):
            return error.error_authorization_fail()
        return 200, "ok"

    def compare_token(self,user_id:str,db_token:str,token:str) -> bool:
        try:
            #比较浏览器的token和数据库中的token是否相同
            if db_token!=token:
                return False
            token_decoded=jwt_decode(token,user_id)
            timestamp=token_decoded["timestamp"]
            now=time.time()
            if self.token_lifetime>now-timestamp:
                return True
            else:
                return False
        except jwt.exceptions.InvalidSignatureError as e:
            logging.error(str(e))
            return False
