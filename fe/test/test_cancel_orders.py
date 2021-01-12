import pytest
import uuid
from fe.test.gen_book_data import GenBook
from fe.access.new_buyer import register_new_buyer


class Test_cancel_orders:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.buyer_id = "test_cancel_orders_buyer_{}".format(str(uuid.uuid1()))
        self.seller_id = "test_cancel_orders_seller_{}".format(str(uuid.uuid1()))
        self.store_id = "test_cancel_orders_store_id_{}".format(str(uuid.uuid1()))
        self.password = self.buyer_id
        self.buyer = register_new_buyer(self.buyer_id, self.password)
        self.gen_book = GenBook(self.seller_id, self.store_id)
        ok, buy_book_id_list = self.gen_book.gen(non_exist_book_id=False, low_stock_level=False)

        # 充足够的钱
        code = self.buyer.add_funds(10000000)
        assert code == 200

        # 需测试买家发货后能否取消订单
        self.seller = self.gen_book.seller
        code, self.order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        assert code == 200
        yield

    # 测试取消未支付订单
    def test_unpaid_ok(self):
        code = self.buyer.cancel_orders(self.buyer_id, self.order_id)
        assert code == 200

    # 测试取消代发货订单（已付款）
    def test_paid_ok(self):
        code = self.buyer.payment(self.order_id)
        assert code == 200
        code = self.buyer.cancel_orders(self.buyer_id, self.order_id)
        assert code == 200

    def test_non_exist_user_id(self):
        code = self.buyer.cancel_orders(self.buyer_id + '_x', self.order_id)
        assert code == 511

    def test_non_exist_order_id(self):
        code = self.buyer.cancel_orders(self.buyer_id, self.order_id + '_x')
        assert code == 522

    # 测试取消已发货订单
    def test_sent_fail(self):
        code = self.buyer.payment(self.order_id)
        assert code == 200
        code = self.buyer.deliver_goods(self.seller_id, self.order_id, self.seller.password)
        assert code == 200
        code = self.buyer.cancel_orders(self.buyer_id, self.order_id)
        assert code == 523

    # 测试取消已收货订单
    def test_received_fail(self):
        code = self.buyer.payment(self.order_id)
        assert code == 200
        code = self.buyer.deliver_goods(self.seller_id, self.order_id, self.seller.password)
        assert code == 200
        code = self.buyer.receive_goods(self.buyer_id, self.order_id, self.password)
        assert code == 200
        code = self.buyer.cancel_orders(self.buyer_id, self.order_id)
        assert code == 523
