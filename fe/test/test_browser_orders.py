import uuid
import pytest
import random
from fe.test.gen_book_data import GenBook
from fe.access.new_buyer import register_new_buyer


class Test_browser_orders:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.buyer_id = "test_search_order__buyer_{}".format(str(uuid.uuid1()))
        self.password = self.buyer_id
        b = register_new_buyer(self.buyer_id, self.password)
        self.buyer = b
        yield

    def test_ok(self):
        # 先充钱
        code = self.buyer.add_funds(10000000)
        assert code == 200
        # 测试3次，每次买书付款后查看订单
        times = 3
        for i in range(times):
            self.seller_id = "test_search_order_seller_{}".format(str(uuid.uuid1()))
            self.store_id = "test_search_order_store_id_{}".format(str(uuid.uuid1()))
            self.gen_book = GenBook(self.seller_id, self.store_id)
            self.seller = self.gen_book.seller
            ok, buy_book_id_list = self.gen_book.gen(non_exist_book_id=False, low_stock_level=False, max_book_count=5)
            self.buy_book_info_list = self.gen_book.buy_book_info_list
            assert ok
            self.total_price = 0
            for item in self.buy_book_info_list:
                book = item[0]
                num = item[1]
                self.total_price = self.total_price + book.price * num
            code, self.order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
            assert code == 200
            code = self.buyer.payment(self.order_id)
            assert code == 200
            # 随机选择模式0/1
            # 0为访问该用户所有订单
            # 1为访问历史订单
            flag = random.randint(0, 1)
            code = self.buyer.browse_orders(self.buyer_id, flag)
            assert code == 200

    def test_non_exist_user_id(self):
        code = self.buyer.browse_orders(self.buyer_id + '_x', 0)
        assert code != 200
