import pytest
import uuid
from fe.test.gen_book_data import GenBook
from fe.access.new_buyer import register_new_buyer
import time


class Test_cancel_orders:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.buyer_id = "test_auto_cancel_orders_buyer_{}".format(str(uuid.uuid1()))
        self.seller_id = "test_auto_cancel_orders_seller_{}".format(str(uuid.uuid1()))
        self.store_id = "test_auto_cancel_orders_store_id_{}".format(str(uuid.uuid1()))
        self.password = self.buyer_id
        self.buyer = register_new_buyer(self.buyer_id, self.password)
        self.gen_book = GenBook(self.seller_id, self.store_id)
        ok, buy_book_id_list = self.gen_book.gen(non_exist_book_id=False, low_stock_level=False)

        # 充足够的钱
        code = self.buyer.add_funds(10000000)
        assert code == 200

        code, self.order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        assert code == 200
        yield

    def test_pay_ok(self):
        code = self.buyer.payment(self.order_id)
        assert code == 200

    def test_pay_fail(self):
        time.sleep(60)
        code = self.buyer.payment(self.order_id)
        assert code != 200
