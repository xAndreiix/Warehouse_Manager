import datetime
import pickle
from decorators import execute_only_at_night_time
from products import FoodProduct, ElectronicProduct, ClothingProduct, Product


class Warehouse:
    def __init__(self, name):
        self.name = name
        self.products = []
        self.reserved_products = []

    @execute_only_at_night_time
    def add_product(self):
        print("/=== Enter the details to add a new product ===/")

        product_type = input("Enter product type (food / electronic / clothing): ").strip().lower()
        if product_type not in ["food", "electronic", "clothing"]:
            print("Invalid product type.\n")
            return

        product_name = input("Enter product name: ").strip()
        if not product_name:
            print("Product name cannot be empty.\n")
            return

        while True:
            try:
                product_price = float(input("Enter product price: "))
                if product_price <= 0:
                    print("Price must be positive.")
                    continue
                break
            except ValueError:
                print("Invalid price. Enter a number.")

        while True:
            try:
                product_quantity = int(input("Enter product quantity: "))
                if product_quantity < 0:
                    print("Quantity cannot be negative.")
                    continue
                break
            except ValueError:
                print("Invalid quantity. Enter a number.")

        product_description = input("Enter product description: ").strip()

        if product_type == "food":
            while True:
                expiration_input = input("Enter product expiration date (YYYY-MM-DD): ")
                try:
                    expiration_date = datetime.datetime.strptime(expiration_input, "%Y-%m-%d").date()
                    break
                except ValueError:
                    print("Invalid date format. Use YYYY-MM-DD.")
            new_product = FoodProduct(product_name, product_price, product_quantity, product_description,
                                      expiration_date)

        elif product_type == "electronic":
            while True:
                warranty_input = input("Enter product warranty date (YYYY-MM-DD): ")
                try:
                    warranty_date = datetime.datetime.strptime(warranty_input, "%Y-%m-%d").date()
                    break
                except ValueError:
                    print("Invalid date format. Use YYYY-MM-DD.")
            new_product = ElectronicProduct(product_name, product_price, product_quantity, product_description,
                                            warranty_date)

        else:
            new_product = ClothingProduct(product_name, product_price, product_quantity, product_description)

        self.products.append(new_product)
        print(f"/=== {product_type.capitalize()} product {product_name} added successfully! ===/\n")

    @execute_only_at_night_time
    def update_products(self):
        bar_code_input = input("Enter the bar code of the product you want to update: ").strip()
        if not bar_code_input:
            print("/=== No bar code entered. Operation cancelled ===/\n")
            return

        for product in self.products:
            if product.bar_code == bar_code_input:
                print(f"Found product: {product.name} | Current price: {product.price}, Quantity: {product.quantity}")

                while True:
                    new_price_input = input("Enter the new price (or leave empty to keep current): ").strip()
                    if new_price_input == "":
                        break
                    try:
                        new_price = float(new_price_input)
                        if new_price <= 0:
                            print("Price must be positive.")
                            continue
                        product.price = new_price
                        product.base_price = new_price
                        break
                    except ValueError:
                        print("Invalid input. Enter a valid number.")

                while True:
                    new_quantity_input = input("Enter the quantity to add (or leave empty to keep current): ").strip()
                    if new_quantity_input == "":
                        break
                    try:
                        added_quantity = int(new_quantity_input)
                        if added_quantity < 0:
                            print("Quantity to add cannot be negative.")
                            continue
                        product.quantity += added_quantity
                        break
                    except ValueError:
                        print("Invalid input. Enter a valid integer.")

                print(f"/=== Product {product.name} successfully updated! New price: {product.price}, "
                      f"Warehouse stock quantity: {product.quantity} ===/\n")
                return

        print("/=== No product found with that bar code! ===/\n")

    def save_products(self, filename="warehouse_products.pickle"):
        try:
            with open(filename, "wb") as data_file:
                pickle.dump(self.products, data_file)
            print(f"/=== Products successfully saved to '{filename}'! ===/\n")
        except (OSError, pickle.PickleError) as e:
            print(f"Error saving products: {e}")

    def print_products(self):
        print("/=== Available Products ===/\n")
        self._print_products_table(self.products, show_reserved=False)

        if self.reserved_products:
            print("/=== Reserved Products ===/\n")
            self._print_products_table(self.reserved_products, show_reserved=True)
        else:
            print("/=== No reserved products at the moment ===/\n")

    def _print_products_table(self, products_list, show_reserved=False):
        if not products_list:
            print("/=== No products found ===/\n")
            return

        headers = ["Type", "Name", "Price", "Quantity", "Description", "Bar Code", "Exp/Warranty Date",
                   "Reservation Date/Time"]
        widths = [12, 20, 10, 10, 30, 36, 20, 20]

        line_sep = "+" + "+".join(["-" * w for w in widths]) + "+"
        header_row = "|" + "|".join([h.ljust(w) for h, w in zip(headers, widths)]) + "|"

        print(line_sep)
        print(header_row)
        print(line_sep)

        for item in products_list:
            if show_reserved:
                product = item["product"]
                quantity = item["quantity"]
                reservation_dt = item["pickup_datetime"].strftime("%Y-%m-%d %H:%M")
            else:
                product = item
                quantity = product.quantity
                reservation_dt = ""

            if isinstance(product, FoodProduct):
                type_name = "Food"
                exp_warranty = str(product.expiration_date)
            elif isinstance(product, ElectronicProduct):
                type_name = "Electronic"
                exp_warranty = str(product.warranty_date)
            else:
                type_name = "Clothing"
                exp_warranty = "-"

            row = [
                type_name.ljust(widths[0]),
                product.name.ljust(widths[1]),
                f"{product.price:.2f}".rjust(widths[2]),
                str(quantity).rjust(widths[3]),
                product.description.ljust(widths[4]),
                product.bar_code.ljust(widths[5]),
                exp_warranty.ljust(widths[6]),
                reservation_dt.ljust(widths[7])
            ]
            print("|" + "|".join(row) + "|")
        print(line_sep + "\n")

    def load_products(self, filename="warehouse_products.pickle"):
        try:
            with open(filename, "rb") as data_file:
                self.products = pickle.load(data_file)
            print(f"/=== Products successfully loaded from '{filename}'! ===/\n")
        except FileNotFoundError:
            print(f"/=== File '{filename}' not found. No products loaded. ===/\n")
        except (OSError, pickle.PickleError) as e:
            print(f"/=== Error loading products: {e} ===/\n")

    @execute_only_at_night_time
    def remove_expired_products(self):
        removed_any = False
        for product in self.products[:]:
            if isinstance(product, FoodProduct) and product.is_expired():
                self.products.remove(product)
                print(f"/=== The {product.name} has been removed from the Main Warehouse ===/\n")
                removed_any = True
        if not removed_any:
            print("/=== There are no expired products to be removed ===/\n")

    @execute_only_at_night_time
    def remove_out_of_warranty_products(self):
        removed_any = False
        for product in self.products[:]:
            if isinstance(product, ElectronicProduct) and not product.is_under_warranty():
                self.products.remove(product)
                print(f"/=== The {product.name} has been removed from the Main Warehouse ===/\n")
                removed_any = True
        if not removed_any:
            print("/=== There are no out of warranty products to be removed ===/\n")

    @execute_only_at_night_time
    def delete_product(self):
        bar_code_input = input("Please enter the bar code of the product you want to delete: ").strip()
        if not bar_code_input:
            print("/=== No bar code entered. Operation cancelled ===/\n")
            return

        for product in self.products:
            if product.bar_code == bar_code_input:
                reserved_count = sum(
                    r["quantity"] for r in self.reserved_products if r["product"].bar_code == bar_code_input
                )
                if reserved_count > 0:
                    print(f"/=== Warning: {reserved_count} unit(s) of this product are currently reserved. "
                          f"Only warehouse stock will be deleted. ===/")

                self.products.remove(product)
                print(f"/=== Product {product.name} has been successfully deleted from the warehouse ===/\n")
                return

        print("/=== No product found with that bar code! ===/\n")

    @execute_only_at_night_time
    def add_discount(self):
        bar_code_input = input("Please enter the bar code of the product you want to discount: ").strip()
        if not bar_code_input:
            print("/=== No bar code entered. Operation cancelled ===/\n")
            return

        try:
            discount_percent = int(input("Add the discount percentage you want to apply (1 - 100): "))
        except ValueError:
            print("Invalid discount. Please enter a number.\n")
            return

        if not (1 <= discount_percent <= 100):
            print("This is not a valid discount percentage. Please enter a value between 1 and 100.\n")
            return

        for product in self.products:
            if bar_code_input == product.bar_code:
                old_price = product.pricez
                product.price = product.base_price * (1 - discount_percent / 100)
                print(f"/=== Discount of {discount_percent}% applied successfully to product {product.name}. "
                      f"Old price: {old_price:.2f}, New price: {product.price:.2f} ===/\n")
                return

        print("/=== No product found with that bar code! ===/\n")

    def reserve_product(self):
        now = datetime.datetime.now()
        for reservation in self.reserved_products[:]:
            if reservation["pickup_datetime"] <= now:
                print(
                    f"/=== Reservation for {reservation['quantity']} {reservation['product'].name} has expired and is removed ===/")
                self.reserved_products.remove(reservation)

        product_name_input = input("Please enter the product name: ").strip()
        found_product = None
        for product in self.products:
            if product.name == product_name_input:
                found_product = product
                break

        if not found_product:
            print("No product found with this name.\n")
            return

        if isinstance(found_product, FoodProduct) and found_product.expiration_date <= now:
            print(f"Cannot reserve {found_product.name}: product has expired.\n")
            return
        if isinstance(found_product, ElectronicProduct) and found_product.warranty_date <= now:
            print(f"Cannot reserve {found_product.name}: product is out of warranty.\n")
            return

        while True:
            try:
                product_quantity_input = int(input("Please enter the quantity you want to reserve: "))
                if product_quantity_input <= 0:
                    print("Invalid quantity. Enter a positive number.")
                    continue
                if product_quantity_input > found_product.quantity:
                    print(f"Not enough in stock. Available: {found_product.quantity}")
                    continue
                break
            except ValueError:
                print("Invalid quantity. Please enter a number.")

        while True:
            product_reservation_input = input(
                "Please enter the date and time you want to reserve the product (YYYY-MM-DD HH:MM): ")
            try:
                product_reservation_datetime = datetime.datetime.strptime(product_reservation_input, "%Y-%m-%d %H:%M")
                if product_reservation_datetime <= datetime.datetime.now():
                    print("Cannot reserve for a past date/time. Please choose a future date/time.")
                    continue
                break
            except ValueError:
                print("Invalid date/time format. Use YYYY-MM-DD HH:MM.")

        found_product.quantity -= product_quantity_input

        reservation = {
            "product": found_product,
            "quantity": product_quantity_input,
            "pickup_datetime": product_reservation_datetime
        }
        self.reserved_products.append(reservation)

        print(
            f"/=== {product_quantity_input} {found_product.name} reserved successfully for {product_reservation_datetime} ===/\n")

    def save_reservation(self):
        if not hasattr(self, 'reserved_products') or not self.reserved_products:
            print("/=== No reserved products to save ===/\n")
            return

        try:
            with open("reserved_products.pickle", "wb") as file:
                pickle.dump(self.reserved_products, file)
            print("/=== Reserved products successfully saved! ===/\n")
        except Exception as e:
            print(f"/=== Something went wrong while saving reserved products: {e} ===/\n")

    def load_reservation(self):
        try:
            with open("reserved_products.pickle", "rb") as file:
                self.reserved_products = pickle.load(file)
            print("/=== Reserved products successfully loaded! ===/\n")
        except FileNotFoundError:
            print("/=== No reserved products file found. ===/\n")
            self.reserved_products = []
        except Exception as e:
            print(f"/=== Something went wrong while loading reserved products: {e} ===/\n")
            self.reserved_products = []

    def buy_product(self):
        product_name_input = input("Please enter the product name: ").strip()
        found_product = None
        for product in self.products:
            if product.name == product_name_input:
                found_product = product
                break

        if not found_product:
            print("No product found with this name.\n")
            return

        now = datetime.datetime.now()
        if isinstance(found_product, FoodProduct) and found_product.expiration_date <= now:
            print(f"Cannot buy {found_product.name}: product has expired.\n")
            return
        if isinstance(found_product, ElectronicProduct) and found_product.warranty_date <= now:
            print(f"Cannot buy {found_product.name}: product is out of warranty.\n")
            return

        while True:
            try:
                product_quantity_input = int(input("Please enter the quantity you want to buy: "))
                if product_quantity_input <= 0:
                    print("Invalid quantity. Enter a positive number.")
                    continue
                if product_quantity_input > found_product.quantity:
                    print(f"Not enough in stock. Available: {found_product.quantity}")
                    continue
                break
            except ValueError:
                print("Invalid quantity. Please enter a number.")

        total_amount_to_pay = product_quantity_input * found_product.price
        found_product.quantity -= product_quantity_input

        print(f"/=== You have successfully bought {product_quantity_input} {found_product.name}. "
              f"Total to pay: {total_amount_to_pay:.2f} ===/\n")
