import sqlite3 as sqlite
import uuid
import json
import logging
import judge
import link
conn = link.conn
cursor = link.cursor
def new_order(user_id,store_id,bookid_and_count):
    try:
        if not judge.judge_user_id(user_id):
            return 511, "non exist user id "+user_id
        if not judge.judge_store_id(store_id):
            return 513, "non exist store id "+store_id
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
                return  515, "non exist book id "+book_id
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
                return 517, "stock level low, book id "+book_id

            #insert new order
            cursor.execute(
                "INSERT INTO new_order_detail(order_id, book_id, count, price) "
                "VALUES(%s, %s, %s, %s);",
                (uid, book_id, count, price))
            cursor.execute(
                "INSERT INTO new_order(order_id, user_id,store_id) "
                "VALUES(%s, %s, %s);",
                (uid, user_id, store_id))
        conn.commit()
        order_id = uid
    except sqlite.Error as e:
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
            return 401, "authorization fail."
        if row[0] != password:
            return 401, "authorization fail."

        #update new balance
        cursor.execute(
            "UPDATE \"user\" SET balance = balance + %s WHERE user_id = %s",
            (add_value, user_id))
        if cursor.rowcount == 0:
            return error.error_non_exist_user_id(user_id)
        conn.commit()
    except sqlite.Error as e:
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
            return 518, "invalid order id "+(order_id)

        #get order's information
        order_id = row[0]
        buyer_id = row[1]
        store_id = row[2]

        #judge whether input buyer_id is correct
        if buyer_id != user_id:
            return 401, "authorization fail."

        #get buyer's password and judge its validity
        cursor.execute("SELECT balance, password FROM \"user\" WHERE user_id = %s;", (buyer_id,))
        row = cursor.fetchone()
        if row is None:
            return 511,"non exist user id "+(buyer_id)
        balance = row[0]
        if password != row[1]:
            return 401, "authorization fail."

        #get seller's id
        cursor.execute("SELECT store_id, user_id FROM user_store WHERE store_id = %s;", (store_id,))
        row = cursor.fetchone()
        if row is None:
            return error.error_non_exist_store_id(store_id)
        seller_id = row[1]

        #determine whether seller's id is exist
        if not judge.judge_user_id(seller_id):
            return 511,"non exist user id "+(seller_id)

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
            return 519,"not sufficient funds, order id "+(order_id)

        #then update seller's information
        cursor.execute("UPDATE \"user\" set balance = balance + %s"
                              "WHERE user_id = %s",
                              (total_price, seller_id))
        # delete finished order
        cursor.execute("DELETE FROM new_order WHERE order_id = %s", (order_id,))
        cursor.execute("DELETE FROM new_order_detail where order_id = %s", (order_id,))
        conn.commit()

    except sqlite.Error as e:
        return 528, "{}".format(str(e))

    except BaseException as e:
        return 530, "{}".format(str(e))
    return 200, "ok"
print(payment('333','10','333_lm_b8ab1c00-4cc3-11eb-8a4f-d8c4975d8efb'))