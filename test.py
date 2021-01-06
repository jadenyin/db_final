import unittest
import requests
from flask import Blueprint
from flask import request
from flask import jsonify
import buyer_function as Buyer
url0=" http://127.0.0.1:5000/buyer/add_fund"
data0={"user_id":'22','password':'22','add_value':100}
url1=" http://127.0.0.1:5000/buyer/new_order"
data1_1 = {"user_id":'22',"store_id":'22','books':[{'id' :"oldmen",'count':1},{'id' :"oldmen1",'count':1}]}
url1=" http://127.0.0.1:5000/buyer/new_order"
data1_2 = {"user_id":'22',"store_id":'store1','books':[{'id' :"oldmen",'count':1},{'id' :"oldmen1",'count':1}]}
url2=" http://127.0.0.1:5000/buyer/payment"
data2 = {"user_id":'22',"password":'22','order_id':'22_store1_6ae75918-5016-11eb-bb21-505bc265c302'}
url3=" http://127.0.0.1:5000/buyer/deliver_goods"
data3 = {"user_id":'11',"password":'22','order_id':'22_store1_6ae75918-5016-11eb-bb21-505bc265c302'}
url4=" http://127.0.0.1:5000/buyer/receive_goods"
data4 = {"user_id":'22',"password":'22','order_id':'22_store1_6ae75918-5016-11eb-bb21-505bc265c302'}

s = requests.session()
#print(s.post(url0,json=data0).json())
#print(s.post(url1,json=data1_2).json())
#print(s.post(url2,json=data2).json())
#print(s.post(url3,json=data3).json())
print(s.post(url4,json=data4).json())