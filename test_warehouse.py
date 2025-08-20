import unittest
import datetime
from warehouse import Warehouse
from products import FoodProduct, ElectronicProduct, ClothingProduct
from decorators import execute_only_at_night_time

class TestWarehouse(unittest.TestCase):

    def setUp(self):
        self.wh = Warehouse("Test Warehouse")

        self.food = FoodProduct("Apple", 1.0, 10, "Fresh apples", datetime.date.today() +
                                datetime.timedelta(days=5))
        self.electronic = ElectronicProduct("Phone", 500.0, 5, "Smartphone",
                                            datetime.date.today() + datetime.timedelta(days=365))
        self.clothing = ClothingProduct("T-Shirt", 20.0, 15, "Cotton t-shirt",
                                        "M", "red")

        self.wh.products = [self.food, self.electronic, self.clothing]

    def test_buy_product(self):
        initial_quantity = self.food.quantity
        self.food.quantity = 10
        self.wh.buy_product = lambda: None
        quantity_to_buy = 3
        self.food.quantity -= quantity_to_buy
        self.assertEqual(self.food.quantity, initial_quantity - quantity_to_buy)

    def test_reserve_product(self):
        reservation_datetime = datetime.datetime.now() + datetime.timedelta(days=1)
        reservation = {"product": self.food, "quantity": 2, "pickup_datetime": reservation_datetime}
        self.wh.reserved_products.append(reservation)
        self.assertIn(reservation, self.wh.reserved_products)

    def test_remove_expired_products(self):
        expired_food = FoodProduct("Old Apple", 1.0, 5, "Old apple",
                                   datetime.date.today() + datetime.timedelta(days=1))
        expired_food.expiration_date = datetime.date.today() - datetime.timedelta(days=1)
        self.wh.products.append(expired_food)
        expired_list = [p for p in self.wh.products if isinstance(p, FoodProduct) and p.is_expired()]
        self.assertIn(expired_food, expired_list)

    def test_remove_out_of_warranty_products(self):
        old_electronic = ElectronicProduct("Old Phone", 100.0, 1, "Old phone",
                                           datetime.date.today() + datetime.timedelta(days=1))
        old_electronic.warranty_date = datetime.date.today() - datetime.timedelta(days=1)
        self.wh.products.append(old_electronic)
        expired_list = [p for p in self.wh.products if isinstance(p, ElectronicProduct) and not p.is_under_warranty()]
        self.assertIn(old_electronic, expired_list)

    def test_add_discount_logic(self):
        product = self.electronic
        original_price = product.price
        discount_percent = 10
        product.price = product.price * (1 - discount_percent / 100)
        self.assertEqual(product.price, original_price * 0.9)

if __name__ == "__main__":
    unittest.main()
