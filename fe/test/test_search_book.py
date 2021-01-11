import pytest
import uuid
from fe.access.new_seller import register_new_seller
from fe.access.new_buyer import register_new_buyer
from fe.access import book


class TestSearchBook:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        # before test
        self.seller_id = "test_search_book_seller_id_{}".format(str(uuid.uuid1()))
        self.store_id_1 = "test_search_book_store1_id_{}".format(str(uuid.uuid1()))
        self.store_id_2 = "test_search_book_store2_id_{}".format(str(uuid.uuid1()))
        self.password_seller = self.seller_id
        self.seller = register_new_seller(self.seller_id, self.password_seller)
        code = self.seller.create_store(self.store_id_1)
        assert code == 200
        code = self.seller.create_store(self.store_id_2)
        assert code == 200
        book_db = book.BookDB()
        self.books = book_db.get_book_info(0, 50)
        self.content = '中'
        self.title = self.books[0].title
        self.tag = self.books[0].tags[0]
        for b in self.books:
            code = self.seller.add_book(self.store_id_1, 1, b)
            assert code == 200
        for b in self.books:
            code = self.seller.add_book(self.store_id_2, 1, b)
            assert code == 200
        self.buyer_id = "test_search_book_buyer_id_{}".format(str(uuid.uuid1()))
        self.password_buyer = self.buyer_id
        self.buyer = register_new_buyer(self.buyer_id, self.password_buyer)

        # yield
        # do after test

    def test_ok_whole_content(self):
        # 全局搜索书籍(内容)
        code = self.buyer.search_book(store_id="", key_word=self.content, term="content")
        assert code == 200

    def test_ok_whole_title(self):
        # 全局搜索书籍(内容)
        code = self.buyer.search_book(store_id="", key_word=self.content, term="title")
        assert code == 200

    def test_ok_whole_tag(self):
        # 全局搜索书籍(内容)
        code = self.buyer.search_book(store_id="", key_word=self.tag, term="tag")
        assert code == 200

    def test_ok_single_content(self):
        # 全局搜索书籍(内容)
        code = self.buyer.search_book(store_id=self.store_id_1, key_word=self.content, term="content")
        assert code == 200

    def test_ok_single_title(self):
        # 全局搜索书籍(内容)
        code = self.buyer.search_book(store_id=self.store_id_1, key_word=self.title, term="title")
        assert code == 200

    def test_ok_single_tag(self):
        # 全局搜索书籍(内容)
        code = self.buyer.search_book(store_id=self.store_id_1, key_word=self.tag, term="tag")
        assert code == 200

    def test_error_none_exist_store_id(self):
        code = self.buyer.search_book(store_id=self.store_id_1 + "x", key_word=self.tag, term="tag")
        assert code == 513

    def test_error_no_book_found(self):
        code = self.buyer.search_book(store_id=self.store_id_1, key_word=self.tag + "x", term="tag")
        assert code == 520

    def test_key_word_search_content(self):
        code = self.buyer.search_book(store_id=self.store_id_1, key_word=self.content[:-1], term="content")
        assert code == 200

    def test_key_word_search_title(self):
        code = self.buyer.search_book(store_id=self.store_id_1, key_word=self.title[:-1], term="title")
        assert code == 200

    def test_split_page(self):
        code = self.buyer.search_book(store_id=self.store_id_1, key_word='第一', term="content")
        assert code == 200
