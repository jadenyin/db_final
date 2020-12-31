import sqlite3 as sqlite
import uuid
import json
import logging

def new_order(user_id,store_id,bookid_and_count):
    try:
