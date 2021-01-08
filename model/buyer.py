import sqlite3 as sqlite
import uuid
import psycopg2
import json
import logging
import judge
import link
import error
conn = link.conn
cursor = link.cursor
def new_order(user_id,store_id,bookid_and_count):
    order_id = ""
    try:
        if(not judge.judge_user_id(user_id)):
            return error.error_non_exist_user_id(user_id) + (order_id, )
        if (not judge.judge_store_id(store_id)):
            return error.error_non_exist_store_id(store_id) + (order_id, )
        uid = "{}_{}_{}".format(user_id, store_id, str(uuid.uuid1()))
        for book_id, count in bookid_and_count:
            #get book's information
            cursor.execute(
                "SELECT book_id, stock_level, book_info FROM store "
                "WHERE store_id = %s AND book_id = %s;",
                (store_id, book_id))
            row = cursor.fetchone()

            # row is NOne means book don't exist
            if row is None:
                return error.error_non_exist_book_id(book_id) + (order_id, )
            stock_level = row[1]
            book_info = row[2]
            book_info_json = json.loads(book_info)
            price = book_info_json.get("price")
            #try to update store, failure means stock level is lowew than input count.
            cursor.execute(
                "UPDATE store set stock_level = stock_level - %s "
                "WHERE store_id = %s and book_id = %s and stock_level >= %s; ",
                (count, store_id, book_id, count))
            if cursor.rowcount == 0:
                return error.error_stock_level_low(book_id) + (order_id,)

            #insert new order detail
            cursor.execute(
                "INSERT INTO new_order_detail(order_id, book_id, count, price) "
                "VALUES(%s, %s, %s, %s);",
                (uid, book_id, count, price))
        #insert new order
        cursor.execute(
            "INSERT INTO new_order(order_id, user_id,store_id, state) "
            "VALUES(%s, %s, %s, %s);",
            (uid, user_id, store_id,0))
        conn.commit()
        order_id = uid
    except psycopg2.Error as e:
        logging.info("528, {}".format(str(e)))
        return 528, "{}".format(str(e)), ""
    except BaseException as e:
        logging.info("530, {}".format(str(e)))
        return 530, "{}".format(str(e)), ""

    return 200, "ok", order_id
def add_money(user_id,password,add_value):
    try:
        cursor.execute("SELECT password  from \"user\" where user_id=%s", (user_id,))
        row = cursor.fetchone()

        #authorization process
        if row is None:
            return error.error_authorization_fail()
        if row[0] != password:
            return error.error_authorization_fail()

        #update new balance
        cursor.execute(
            "UPDATE \"user\" SET balance = balance + %s WHERE user_id = %s",
            (add_value, user_id))
        if cursor.rowcount == 0:
            return error.error_non_exist_user_id(user_id)
        conn.commit()
    except psycopg2.Error as e:
        return 528, "{}".format(str(e))
    except BaseException as e:
        return 530, "{}".format(str(e))
    return 200, "ok"
def payment(user_id,password,order_id):
    try:
        conn = link.conn
        cursor = link.cursor
        #determine whether order_id is correct
        cursor.execute("SELECT order_id, user_id, store_id "
                              "FROM new_order WHERE order_id = %s", (order_id,))
        row = cursor.fetchone()
        if row is None:
            return error.error_invalid_order_id(order_id)

        #get order's information
        order_id = row[0]
        buyer_id = row[1]
        store_id = row[2]

        #judge whether input buyer_id is correct
        if buyer_id != user_id:
            return error.error_authorization_fail()

        #get buyer's password and judge its validity
        cursor.execute("SELECT balance, password FROM \"user\" WHERE user_id = %s;", (buyer_id,))
        row = cursor.fetchone()
        if row is None:
            return error.error_non_exist_user_id(buyer_id)
        balance = row[0]
        if password != row[1]:
            return error.error_authorization_fail()

        #get seller's id
        cursor.execute("SELECT store_id, user_id FROM user_store WHERE store_id = %s;", (store_id,))
        row = cursor.fetchone()
        if row is None:
            return error.error_non_exist_store_id(store_id)
        seller_id = row[1]

        #determine whether seller's id is exist
        if not judge.judge_user_id(seller_id):
            return error.error_non_exist_user_id(seller_id)

        #get book's price in this order
        cursor.execute("SELECT book_id, count, price FROM new_order_detail WHERE order_id = %s;", (order_id,))
        total_price = 0
        for row in cursor:
            count = row[1]
            price = row[2]
            total_price = total_price + price * count

        #try to update buyer's information. failure means balance is not enough
        cursor.execute("UPDATE \"user\" set balance = balance - %s"
                              "WHERE user_id = %s AND balance >= %s",
                              (total_price, buyer_id, total_price))
        if cursor.rowcount == 0:
            return error.error_not_sufficient_funds(order_id)

        #then update seller's information
        cursor.execute("UPDATE \"user\" set balance = balance + %s"
                              "WHERE user_id = %s",
                              (total_price, seller_id))
        row=cursor.execute("SELECT state FROM new_order WHERE order_id = %s;", (order_id,))
        state=row[0]
        # then update order's state
        if(state!=0):
            return 520, "order_operation error"
        cursor.execute("UPDATE new_order set state = 1"
                       "WHERE order_id = %s",
                       (order_id,))
        conn.commit()

    except psycopg2.Error as e:
        return 528, "{}".format(str(e))

    except BaseException as e:
        return 530, "{}".format(str(e))
    return 200, "ok"
def deliver_goods(user_id,password,order_id):
    try:
        conn = link.conn
        cursor = link.cursor
        # determine whether order_id is correct
        cursor.execute("SELECT order_id, store_id,state "
                       "FROM new_order WHERE order_id = %s", (order_id,))
        row = cursor.fetchone()
        if row is None:
            return 518, "invalid order id " + (order_id)
        #get store_id
        store_id = row[1]
        state = row[2]
         #get seller's id
        cursor.execute("SELECT store_id, user_id FROM user_store WHERE store_id = %s;", (store_id,))
        row = cursor.fetchone()
        if row is None:
            return 513, "non exist store id "+store_id
        seller_id = row[1]
        #determine whether seller's id is exist
        if not judge.judge_user_id(seller_id):
            return 511,"non exist user id "+(seller_id)
        #determine whether user_id and password are correct
        cursor.execute("SELECT password FROM \"user\" WHERE user_id = %s;", (user_id,))
        row = cursor.fetchone()
        if row is None:
            return 511, "non exist user id " + (user_id)
        pwd=row[0]
        if(seller_id!=user_id or password!=pwd):
            return 401, "authorization fail."
        #determine state is correct
        if(state!=1):
            return 520,  "order_operation error"
        # then update order's state
        cursor.execute("UPDATE new_order set state = 2"
                       "WHERE order_id = %s",
                       (order_id,))
        conn.commit()
    except psycopg2.Error as e:
        return 528, "{}".format(str(e))
    except BaseException as e:
        return 530, "{}".format(str(e))
    return 200, "ok"
def receive_goods(user_id,password,order_id):
    try:
        conn = link.conn
        cursor = link.cursor
        # determine whether order_id is correct
        cursor.execute("SELECT user_id, store_id,state "
                       "FROM new_order WHERE order_id = %s", (order_id,))
        row = cursor.fetchone()
        if row is None:
            return 518, "invalid order id " + (order_id)
        #get store_id and order's state
        buyer_id=row[0]
        store_id = row[1]
        state = row[2]
        #determine whether buyer's id is exist
        if not judge.judge_user_id(buyer_id):
            return 511,"non exist user id "+(buyer_id)
        #determine whether buyer_id equals to user_id
        if(buyer_id!=user_id):
            return 401, "authorization fail."
        #determine whether password are correct
        cursor.execute("SELECT password FROM \"user\" WHERE user_id = %s;", (user_id,))
        row = cursor.fetchone()
        if row is None:
            return 511, "non exist user id " + (user_id)
        pwd=row[0]
        if(password!=pwd):
            return 401, "authorization fail."
        #determine state is correct
        if(state!=2):
            return 520,  "order_operation error"
        # then update order's state
        cursor.execute("UPDATE new_order set state = 3"
                       "WHERE order_id = %s",
                       (order_id,))
        conn.commit()
    except psycopg2.Error as e:
        return 528, "{}".format(str(e))
    except BaseException as e:
        return 530, "{}".format(str(e))
    return 200, "ok"
#print(receive_goods('22','22','22_store1_90224c9e-500c-11eb-a7c4-505bc265c302'))