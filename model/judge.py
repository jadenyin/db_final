import link
conn=link.conn
cursor=link.cursor
def judge_user_id(user_id):
    cursor.execute("SELECT user_id FROM \"user\" WHERE user_id = %s;", (user_id,))
    row = cursor.fetchone()
    if row is None:
        return False
    else:
        return True
def judge_book_id(store_id,book_id):
    cursor.execute("SELECT book_id FROM store WHERE store_id = %s AND book_id = %s;", (store_id, book_id))
    row = cursor.fetchone()
    if row is None:
        return False
    else:
        return True
def judge_store_id(store_id):
    cursor.execute("SELECT store_id FROM user_store WHERE store_id = %s;", (store_id,))
    row = cursor.fetchone()
    if row is None:
        return False
    else:
        return True