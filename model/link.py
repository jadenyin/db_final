import logging
import os
import sqlite3 as sqlite
import psycopg2
conn = psycopg2.connect(database="postgres", user="postgres", password="postgres", host="localhost", port="5432")
cursor = conn.cursor()
def init_database():
    try:
        cursor.execute("CREATE TABLE IF NOT EXISTS users("
            "user_id TEXT PRIMARY KEY, password TEXT NOT NULL, "
            "balance INTEGER NOT NULL, token TEXT, terminal TEXT);"
        )

        cursor.execute(
            "CREATE TABLE IF NOT EXISTS user_store("
            "user_id TEXT, store_id TEXT, PRIMARY KEY(user_id, store_id));"
        )

        cursor.execute(
            "CREATE TABLE IF NOT EXISTS store( "
            "store_id TEXT, book_id TEXT, book_info TEXT, stock_level INTEGER,"
            " PRIMARY KEY(store_id, book_id))"
        )

        cursor.execute(
            "CREATE TABLE IF NOT EXISTS new_order( "
            "order_id TEXT PRIMARY KEY, user_id TEXT, store_id TEXT)"
        )

        cursor.execute(
            "CREATE TABLE IF NOT EXISTS new_order_detail( "
            "order_id TEXT, book_id TEXT, count INTEGER, price INTEGER,  "
            "PRIMARY KEY(order_id, book_id))"
        )

        conn.commit()
    except psycopg2.Error as e:
        logging.error(e)
        conn.rollback()
init_database()