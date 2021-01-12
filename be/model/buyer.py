import uuid
import json
import logging
from be.model import error
from be.model import create_table as ct
from be.model import session
import threading
import time
from sqlalchemy import or_
from sqlalchemy import text

ticksPerWheel = 60
import time


# 分页
def page_split(id_and_stock, split_num):
    result = []
    num = len(id_and_stock)
    pages = int((num + split_num - 1) / split_num)
    for index in range(pages):
        start = split_num * index
        if (start + split_num) >= num:
            break
        page = id_and_stock[start:start + split_num]
        result.append(page)
    result.append(id_and_stock[split_num * (pages - 1):])
    return result


# 定时ticksPerWheel自动删除订单
# 维护一个包含ticksPerWheel个slot的环形队列
to_be_remove = []
for i in range(ticksPerWheel):
    to_be_remove.append([])
index = 0


def remove_list_append(ind, value):  # 对to_be_remove进行操作
    global to_be_remove
    to_be_remove[ind].append(value)


class buyer_functions(session.ORMsession):
    def __init__(self):
        session.ORMsession.__init__(self)

    def browser_all_orders(self, user_id):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            orders = self.db_session.query(ct.New_order_detail).join(ct.New_order,
                                                                     ct.New_order_detail.order_id == ct.New_order.order_id, ).filter(
                ct.New_order.user_id == user_id).all()
            for order in orders:
                print('order_id:{} book_id:{} count:{} price:{}'.format(order.order_id, order.book_id,
                                                                        order.count, order.price))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def browser_history_orders(self, user_id):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            orders = self.db_session.query(ct.New_order_detail).join(ct.New_order,
                                                                     ct.New_order_detail.order_id == ct.New_order.order_id). \
                filter(ct.New_order.user_id == user_id, ct.New_order.state == 4).all()
            for order in orders:
                print('order_id:{} book_id:{} count:{} price:{}'.format(order.order_id, order.book_id,
                                                                        order.count, order.price))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def cancel_order(self, user_id, order_id):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.order_id_exist(user_id, order_id):
                return error.error_not_exist_order(user_id, order_id)
            store_id = self.db_session.query(ct.New_order).filter(ct.New_order.order_id == order_id).first().store_id
            row = self.db_session.query(ct.New_order).filter(ct.New_order.order_id == order_id).first()
            state = row.state
            rows = self.db_session.query(ct.New_order_detail).filter(ct.New_order_detail.order_id == order_id).all()
            if state == 0 or state == 1:
                self.db_session.query(ct.New_order).filter(ct.New_order.order_id == order_id).delete()
                self.db_session.query(ct.New_order_detail).filter(ct.New_order_detail.order_id == order_id).delete()
                for row in rows:
                    book_id = row.book_id
                    count = row.count
                    self.db_session.query(ct.Store).filter(ct.Store.store_id == store_id,
                                                           ct.Store.book_id == book_id).update(
                        {ct.Store.stock_level: ct.Store.stock_level + count})
                    if state == 1:
                        money = row.price * count
                        seller_id = self.db_session.query(ct.User_store).filter(
                            ct.User_store.store_id == store_id).first().user_id
                        # 卖家减钱
                        self.db_session.query(ct.User).filter(ct.User.user_id == seller_id).update(
                            {ct.User.balance: ct.User.balance - money}
                        )
                        # 买家加钱
                        self.db_session.query(ct.User).filter(ct.User.user_id == user_id).update(
                            {ct.User.balance: ct.User.balance + money})
                self.db_session.commit()
            else:
                self.db_session.rollback()
                return error.error_cancel_fail(order_id)
        except BaseException as e:
            self.db_session.rollback()
            return 530, "{}".format(str(e))
        return 200, "ok"

    def new_order(self, user_id, store_id, bookid_and_count):
        global index
        order_id = ""
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id) + (order_id,)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id) + (order_id,)
            uid = "{}_{}_{}".format(user_id, store_id, str(uuid.uuid1()))
            for book_id, count in bookid_and_count:
                # get book's information
                row = self.db_session.query(ct.Store).filter(ct.Store.store_id == store_id,
                                                             ct.Store.book_id == book_id).first()

                # row is None means book don't exist
                if row is None:
                    return error.error_non_exist_book_id(book_id) + (order_id,)
                stock_level = row.stock_level
                book_info = row.book_info
                book_info_json = json.loads(book_info)
                price = book_info_json.get("price")

                # try to update store, failure means stock level is lower than input count.
                if stock_level >= count:
                    self.db_session.query(ct.Store).filter(ct.Store.store_id == store_id,
                                                           ct.Store.book_id == book_id).update(
                        {ct.Store.stock_level: ct.Store.stock_level - count})
                else:
                    return 522, "stock level low, book id:" + book_id, order_id

                # insert new order
                new_order_detail_obj = ct.New_order_detail(order_id=uid, book_id=book_id, count=count, price=price)
                self.db_session.add(new_order_detail_obj)
            new_order_obj = ct.New_order(order_id=uid, user_id=user_id, store_id=store_id, state=0)
            self.db_session.add(new_order_obj)
            remove_list_append((index - 1) % ticksPerWheel, uid)
            self.db_session.commit()
            order_id = uid
        except BaseException as e:
            logging.info("530, {}".format(str(e)))
            self.db_session.rollback()
            return 530, "{}".format(str(e)), ""
        return 200, "ok", order_id

    def add_money(self, user_id, password, add_value):
        try:
            row = self.db_session.query(ct.User).filter(ct.User.user_id == user_id).first()
            # authorization process
            if row is None:
                return error.error_authorization_fail()
            if row.password != password:
                return error.error_authorization_fail()

            # update new balance
            self.db_session.query(ct.User).filter(ct.User.user_id == user_id).update(
                {ct.User.balance: ct.User.balance + add_value})
            self.db_session.commit()
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def payment(self, user_id, password, order_id):
        try:
            # determine whether order_id is correct
            row = self.db_session.query(ct.New_order).filter(ct.New_order.order_id == order_id).first()
            if row is None:
                return error.error_invalid_order_id(order_id)

            # get order's information
            order_id = row.order_id
            buyer_id = row.user_id
            store_id = row.store_id

            # judge whether input buyer_id is correct
            if buyer_id != user_id:
                return error.error_authorization_fail()

            # get buyer's password and judge its validity
            row = self.db_session.query(ct.User).filter(ct.User.user_id == buyer_id).first()
            if row is None:
                return error.error_non_exist_user_id(buyer_id)
            balance = row.balance
            if password != row.password:
                return error.error_authorization_fail()

            # get seller's id
            row = self.db_session.query(ct.User_store).filter(ct.User_store.store_id == store_id).first()
            if row is None:
                return error.error_non_exist_store_id(store_id)
            seller_id = row.user_id

            # determine whether seller's id is exist
            if not self.user_id_exist(seller_id):
                return error.error_non_exist_user_id(seller_id)

            # get book's price in this order
            rows = self.db_session.query(ct.New_order_detail).filter(ct.New_order_detail.order_id == order_id).all()
            total_price = 0
            for row in rows:
                count = row.count
                price = row.price
                total_price = total_price + price * count

            # try to update buyer's information. failure means balance is not enough
            if balance >= total_price:
                self.db_session.query(ct.User).filter(ct.User.user_id == buyer_id).update(
                    {ct.User.balance: ct.User.balance - total_price})
                self.db_session.query(ct.User).filter(ct.User.user_id == seller_id).update(
                    {ct.User.balance: ct.User.balance + total_price})
            else:
                return error.error_not_sufficient_funds(order_id)
            row = self.db_session.query(ct.New_order).filter(ct.New_order.order_id == order_id).first()
            # then update order's state
            state = row.state
            if state != 0:
                return 520, "order_operation error"
            self.db_session.query(ct.New_order).filter(ct.New_order.order_id == order_id).update(
                {ct.New_order.state: 1})
            self.db_session.commit()
        except BaseException as e:
            self.db_session.rollback()
            print(e)
            return 530, "{}".format(str(e))
        return 200, "ok"

    def deliver_goods(self, user_id, password, order_id):
        try:
            # determine whether order_id is correct
            row = self.db_session.query(ct.New_order).filter(ct.New_order.order_id == order_id).first()
            if row is None:
                return 518, "invalid order id " + order_id
            # get store_id
            store_id = row.store_id
            state = row.state
            # get seller's id
            row = self.db_session.query(ct.User_store).filter(ct.User_store.store_id == store_id).first()
            if row is None:
                return 513, "non exist store id " + store_id
            seller_id = row.user_id
            # determine whether seller's id is exist
            if not self.user_id_exist(seller_id):
                return 511, "non exist user id " + seller_id
            # determine whether user_id and password are correct
            row = self.db_session.query(ct.User).filter(ct.User.user_id == user_id).first()
            if row is None:
                return 511, "non exist user id " + user_id
            pwd = row.password
            if seller_id != user_id or password != pwd:
                return 401, "authorization fail."
            # determine state is correct
            if state != 1:
                return 524, "order_operation error"
            # then update order's state
            self.db_session.query(ct.New_order).filter(ct.New_order.order_id == order_id).update(
                {ct.New_order.state: 2})
            self.db_session.commit()
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def receive_goods(self, user_id, password, order_id):
        try:
            # determine whether order_id is correct
            row = self.db_session.query(ct.New_order).filter(ct.New_order.order_id == order_id).first()
            if row is None:
                return 518, "invalid order id " + order_id
            # get store_id and order's state
            buyer_id = row.user_id
            store_id = row.store_id
            state = row.state
            # determine whether buyer's id is exist
            if not self.user_id_exist(buyer_id):
                return 511, "non exist user id " + buyer_id
            # determine whether buyer_id equals to user_id
            if buyer_id != user_id:
                return 401, "authorization fail."
            # determine whether password are correct
            row = self.db_session.query(ct.User).filter(ct.User.user_id == user_id).first()
            if row is None:
                return 511, "non exist user id " + user_id
            pwd = row.password
            if password != pwd:
                return 401, "authorization fail."
            # determine state is correct
            if state != 2:
                return 524, "order_operation error"
            # then update order's state
            self.db_session.query(ct.New_order).filter(ct.New_order.order_id == order_id).update(
                {ct.New_order.state: 3})
            self.db_session.commit()
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def retrieve(self, key_word: str, term: str, store_id: str,page_num:int) -> (int, str, list):
        try:
            id_and_stock = []
            book_id = []
            if store_id != '' and not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id) + ([],)
            if term == 'title':
                book_id = self.db_session.query(ct.Book.book_id). \
                    filter(text("to_tsvector('english',tsv_title) @@ plainto_tsquery('english',:search_string)")). \
                    params(search_string=key_word).all()
            # 标签搜索必须精准
            elif term == 'tag':
                book_id = self.db_session.query(ct.Tag_index.book_id) \
                    .filter(ct.Tag_index.tag==key_word).all()
            elif term == 'content':
                book_id=self.db_session.query(ct.Book.book_id).\
                    filter(text("to_tsvector('english',tsv_content) @@ plainto_tsquery('english',:search_string)")).\
                    params(search_string=key_word).all()
                #book_id = self.db_session.query(ct.Book.book_id).filter(ct.Book.content.like('%' + key_word + '%')).all()
            # 店铺搜索
            if not len(book_id):
                return error.error_no_book_found()
            # 全局搜索
            if store_id != '':
                for id in book_id:
                    id_stock = self.db_session.query(ct.Store.store_id, ct.Store.book_id, ct.Store.stock_level) \
                        .filter(ct.Store.book_id == id, ct.Store.store_id == store_id).all()
                    if len(id_stock):
                        for i in range(len(id_stock)):
                            id_and_stock.append(id_stock[i])
            else:
                for id in book_id:
                    id_stock = self.db_session.query(ct.Store.store_id, ct.Store.book_id, ct.Store.stock_level) \
                        .filter(ct.Store.book_id == id).all()
                    if len(id_stock):
                        for i in range(len(id_stock)):
                            id_and_stock.append(id_stock[i])
            if not len(id_and_stock):
                return error.error_no_book_found()
            # 分页处理,每页书本数=k
            splited_result = page_split(id_and_stock, 10)
            if len(splited_result) < page_num:
                return error.error_page_overflow() + ([],)
            self.db_session.commit()
        except BaseException as e:
            buyer_functions().db_session.rollback()
            logging.info("530, {}".format(str(e)))
            return 530, "{}".format(str(e)), ""
        return 200, "ok", splited_result[page_num-1]

    def auto_cancel(self, ind):
        global to_be_remove
        remove_list = to_be_remove[ind]
        try:
            for order in remove_list:
                row = self.db_session.query(ct.New_order).filter(
                    ct.New_order.order_id == order).first()
                print(row)
                user_id = row.user_id
                state = row.state
                if state == 0:
                    buyer_functions().cancel_order(user_id, order)
            self.db_session.commit()
            to_be_remove[ind].clear()
        except BaseException as e:
            buyer_functions().db_session.rollback()
            logging.info("530, {}".format(str(e)))
            return 530, "{}".format(str(e)), ""
        return 200, "ok"


class Timer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self._running = True

    def terminate(self):
        self._running = False

    def run(self):
        global index
        while self._running:
            buyer_functions().auto_cancel(index)
            time.sleep(1)
            index = (index + 1) % ticksPerWheel


t = Timer()
t.start()


def terminate_auto_cancel():
    global t
    t.terminate()
