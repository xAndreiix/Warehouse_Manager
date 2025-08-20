import datetime
import uuid
from abc import ABC, abstractmethod


class Product(ABC):
    def __init__(self, name, price, quantity, description):

        if not isinstance(name, str):
            raise TypeError("Name must be a string type.")
        if not isinstance(price, (int, float)):
            raise TypeError("Price must be numeric (int or float).")
        if not isinstance(quantity, int):
            raise TypeError("Quantity must be an integer.")
        if not isinstance(description, str):
            raise TypeError("Description must be a string type.")

        if not name.strip():
            raise ValueError("Name field cannot be empty.")
        if price <= 0:
            raise ValueError("Price must be a positive value.")
        if quantity < 0:
            raise ValueError("Quantity cannot be a negative value.")

        self.name = name
        self.price = float(price)
        self.base_price =float(price)
        self.quantity = quantity
        self.description = description.strip()
        self.bar_code = str(uuid.uuid4())

    def __repr__(self):
        return (f"<Product {self.name} | Price: {self.price}, "
                f"Quantity: {self.quantity}, Description: {self.description}, "
                f"Bar Code: {self.bar_code}>")

    def __str__(self):
        return f"{self.name} ({self.quantity} pcs @ {self.price:.2f} each)"

    @abstractmethod
    def get_total_value(self):
        pass


class FoodProduct(Product):
    def __init__(self, name, price, quantity, description, expiration_date):
        super().__init__(name, price, quantity, description)

        if isinstance(expiration_date, str):
            try:
                expiration_date = datetime.datetime.strptime(expiration_date, "%Y-%m-%d").date()
            except ValueError:
                raise ValueError("Invalid date format. Use YYYY-MM-DD string.")
        elif isinstance(expiration_date, datetime.datetime):
            expiration_date = expiration_date.date()
        elif not isinstance(expiration_date, datetime.date):
            raise TypeError("expiration_date must be str (YYYY-MM-DD), datetime.date, or datetime.datetime.")

        self.expiration_date = expiration_date

        if self.expiration_date < datetime.date.today():
            raise ValueError(f"Expiration date {self.expiration_date} is in the past.")

    def get_total_value(self):
        return self.price * self.quantity

    def is_expired(self):
        return datetime.date.today() > self.expiration_date

    def __repr__(self):
        return (f"<FoodProduct {self.name} | Price: {self.price}, Quantity: {self.quantity}, "
                f"Expires: {self.expiration_date}, Description: {self.description}, "
                f"Bar Code: {self.bar_code}>")

    def __str__(self):
        return f"{self.name} ({self.quantity} pcs, exp: {self.expiration_date})"


class ElectronicProduct(Product):
    def __init__(self, name, price, quantity, description, warranty_date):
        super().__init__(name, price, quantity, description)

        if isinstance(warranty_date, str):
            try:
                warranty_date = datetime.datetime.strptime(warranty_date, "%Y-%m-%d").date()
            except ValueError:
                raise ValueError("Invalid warranty_date format. Use YYYY-MM-DD string.")
        elif isinstance(warranty_date, datetime.datetime):
            warranty_date = warranty_date.date()
        elif not isinstance(warranty_date, datetime.date):
            raise TypeError("warranty_date must be str (YYYY-MM-DD), datetime.date, or datetime.datetime.")

        self.warranty_date = warranty_date

        if self.warranty_date < datetime.date.today():
            raise ValueError(f"Warranty date {self.warranty_date} is already out of warranty.")

    def get_total_value(self):
        return self.price * self.quantity

    def is_under_warranty(self):
        return datetime.date.today() <= self.warranty_date

    def __repr__(self):
        return (f"<ElectronicProduct {self.name} | Price: {self.price}, Quantity: {self.quantity}, "
                f"Warranty until: {self.warranty_date}, Description: {self.description}, "
                f"Bar Code: {self.bar_code}>")

    def __str__(self):
        return f"{self.name} ({self.quantity} pcs, warranty: {self.warranty_date})"


class ClothingProduct(Product):
    def __init__(self, name, price, quantity, description, size, color, material=None):
        super().__init__(name, price, quantity, description)

        if not size.strip():
            raise ValueError("Size cannot be empty.")
        if not color.strip():
            raise ValueError("Color cannot be empty.")

        self.size = size
        self.color = color
        self.material = material if material else "Unknown"

    def get_total_value(self):
        return self.price * self.quantity

    def __repr__(self):
        return (f"<ClothingProduct {self.name} | Price: {self.price}, Quantity: {self.quantity}, "
                f"Size: {self.size}, Color: {self.color}, Material: {self.material}, "
                f"Description: {self.description}, Bar Code: {self.bar_code}>")

    def __str__(self):
        return f"{self.name} ({self.size}, {self.color}, {self.quantity} pcs)"
