import sys
import datetime
from typing import List, Optional

from PyQt6.QtCore import Qt, QDateTime
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox,
    QDialog, QFormLayout, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit,
    QDateEdit, QDateTimeEdit, QCheckBox
)

from warehouse import Warehouse
from products import FoodProduct, ElectronicProduct, ClothingProduct, Product

def is_manager_hours(now: Optional[datetime.datetime] = None) -> bool:
    """ Operații de manager doar între 23:00 și 06:00. """
    if now is None:
        now = datetime.datetime.now()
    t = now.time()
    start = datetime.time(23, 0)
    end = datetime.time(6, 0)
    return (t >= start) or (t <= end)


def show_error(parent, text: str):
    QMessageBox.critical(parent, "Error", text)


def show_info(parent, text: str):
    QMessageBox.information(parent, "Info", text)


def product_type_name(p: Product) -> str:
    if isinstance(p, FoodProduct):
        return "Food"
    if isinstance(p, ElectronicProduct):
        return "Electronic"
    if isinstance(p, ClothingProduct):
        return "Clothing"
    return "Product"


def product_exp_warranty_str(p: Product) -> str:
    if isinstance(p, FoodProduct):
        return str(p.expiration_date)
    if isinstance(p, ElectronicProduct):
        return str(p.warranty_date)
    return "-"


def is_product_valid_for_sale_or_reservation(p: Product, now: Optional[datetime.datetime] = None) -> bool:
    if now is None:
        now = datetime.datetime.now()
    if isinstance(p, FoodProduct):
        return p.expiration_date > now.date()
    if isinstance(p, ElectronicProduct):
        return p.warranty_date >= now.date()
    return True

class AddProductDialog(QDialog):
    def __init__(self, parent, warehouse: Warehouse):
        super().__init__(parent)
        self.setWindowTitle("Add a new product")
        self.warehouse = warehouse

        if not is_manager_hours():
            self._blocked_ui("Adding products is allowed only between 23:00 and 06:00.")
            return

        form = QFormLayout(self)

        self.type_cb = QComboBox()
        self.type_cb.addItems(["Food", "Electronic", "Clothing"])
        form.addRow("Type:", self.type_cb)

        self.name_le = QLineEdit()
        form.addRow("Name:", self.name_le)

        self.price_sb = QDoubleSpinBox()
        self.price_sb.setRange(0.01, 1_000_000_000)
        self.price_sb.setDecimals(2)
        self.price_sb.setValue(1.00)
        form.addRow("Price:", self.price_sb)

        self.qty_sb = QSpinBox()
        self.qty_sb.setRange(0, 1_000_000_000)
        form.addRow("Quantity:", self.qty_sb)

        self.desc_le = QLineEdit()
        form.addRow("Description:", self.desc_le)

        self.exp_date = QDateEdit()
        self.exp_date.setCalendarPopup(True)
        self.exp_date.setDate(datetime.date.today())
        self.warranty_date = QDateEdit()
        self.warranty_date.setCalendarPopup(True)
        self.warranty_date.setDate(datetime.date.today())

        self.size_le = QLineEdit()
        self.color_le = QLineEdit()
        self.material_le = QLineEdit()

        self.food_row = ("Expiration date:", self.exp_date)
        self.elec_row = ("Warranty date:", self.warranty_date)
        self.clo_row1 = ("Size:", self.size_le)
        self.clo_row2 = ("Color:", self.color_le)
        self.clo_row3 = ("Material (optional):", self.material_le)

        form.addRow(*self.food_row)

        btns = QHBoxLayout()
        self.ok_btn = QPushButton("Add")
        self.cancel_btn = QPushButton("Cancel")
        btns.addWidget(self.ok_btn)
        btns.addWidget(self.cancel_btn)
        form.addRow(btns)

        self.type_cb.currentTextChanged.connect(lambda _: self._on_type_change(form))
        self.ok_btn.clicked.connect(self._on_submit)
        self.cancel_btn.clicked.connect(self.reject)

        self._form = form

    def _blocked_ui(self, msg: str):
        layout = QVBoxLayout(self)
        label = QLabel(msg)
        layout.addWidget(label)
        close_btn = QPushButton("Close")
        layout.addWidget(close_btn)
        close_btn.clicked.connect(self.reject)

    def _on_type_change(self, form: QFormLayout):
        for i in reversed(range(form.rowCount() - 1)):
            label_item = form.itemAt(i, QFormLayout.ItemRole.LabelRole)
            field_item = form.itemAt(i, QFormLayout.ItemRole.FieldRole)
            if label_item and field_item:
                widget_label = label_item.widget()
                widget_field = field_item.widget()
                if widget_label and widget_label.text() in ["Type:", "Name:", "Price:", "Quantity:", "Description:"]:
                    continue
                try:
                    form.removeRow(i)
                except Exception:
                    pass

        t = self.type_cb.currentText()
        if t == "Food":
            form.insertRow(5, *self.food_row)
        elif t == "Electronic":
            form.insertRow(5, *self.elec_row)
        else:
            form.insertRow(5, *self.clo_row1)
            form.insertRow(6, *self.clo_row2)
            form.insertRow(7, *self.clo_row3)

    def _on_submit(self):
        t = self.type_cb.currentText()
        name = self.name_le.text().strip()
        desc = self.desc_le.text().strip()
        price = float(self.price_sb.value())
        qty = int(self.qty_sb.value())

        if not name:
            show_error(self, "Name cannot be empty.")
            return
        if price <= 0:
            show_error(self, "Price must be positive.")
            return
        if qty < 0:
            show_error(self, "Quantity cannot be negative.")
            return

        try:
            if t == "Food":
                exp = self.exp_date.date().toPyDate()
                p = FoodProduct(name, price, qty, desc, exp)
            elif t == "Electronic":
                war = self.warranty_date.date().toPyDate()
                p = ElectronicProduct(name, price, qty, desc, war)
            else:
                size = self.size_le.text().strip()
                color = self.color_le.text().strip()
                material = self.material_le.text().strip() or None
                if not size:
                    show_error(self, "Size cannot be empty.")
                    return
                if not color:
                    show_error(self, "Color cannot be empty.")
                    return
                p = ClothingProduct(name, price, qty, desc, size, color, material)
        except Exception as e:
            show_error(self, f"Validation error: {e}")
            return

        self.warehouse.products.append(p)
        show_info(self, f"Product '{name}' added successfully!")
        self.accept()


class UpdateProductDialog(QDialog):
    def __init__(self, parent, warehouse: Warehouse):
        super().__init__(parent)
        self.setWindowTitle("Update price/quantity by bar code")
        self.warehouse = warehouse

        if not is_manager_hours():
            self._blocked_ui("Updating products is allowed only between 23:00 and 06:00.")
            return

        form = QFormLayout(self)

        self.barcode_le = QLineEdit()
        form.addRow("Bar Code:", self.barcode_le)

        self.new_price_le = QLineEdit()
        self.new_price_le.setPlaceholderText("Leave empty to keep current")
        form.addRow("New price:", self.new_price_le)

        self.add_qty_le = QLineEdit()
        self.add_qty_le.setPlaceholderText("Leave empty to keep current")
        form.addRow("Quantity to add:", self.add_qty_le)

        btns = QHBoxLayout()
        self.ok_btn = QPushButton("Update")
        self.cancel_btn = QPushButton("Cancel")
        btns.addWidget(self.ok_btn)
        btns.addWidget(self.cancel_btn)
        form.addRow(btns)

        self.ok_btn.clicked.connect(self._on_submit)
        self.cancel_btn.clicked.connect(self.reject)

    def _blocked_ui(self, msg: str):
        layout = QVBoxLayout(self)
        label = QLabel(msg)
        layout.addWidget(label)
        close_btn = QPushButton("Close")
        layout.addWidget(close_btn)
        close_btn.clicked.connect(self.reject)

    def _find_by_barcode(self, code: str) -> Optional[Product]:
        for p in self.warehouse.products:
            if p.bar_code == code:
                return p
        return None

    def _on_submit(self):
        code = self.barcode_le.text().strip()
        if not code:
            show_error(self, "Please enter a bar code.")
            return

        p = self._find_by_barcode(code)
        if p is None:
            show_error(self, "No product found with that bar code.")
            return

        new_price_str = self.new_price_le.text().strip()
        if new_price_str:
            try:
                new_price = float(new_price_str)
                if new_price <= 0:
                    show_error(self, "Price must be positive.")
                    return
                p.price = new_price
                if hasattr(p, "base_price"):
                    p.base_price = new_price
            except ValueError:
                show_error(self, "Invalid price. Enter a valid number.")
                return

        add_qty_str = self.add_qty_le.text().strip()
        if add_qty_str:
            try:
                add_qty = int(add_qty_str)
                if add_qty < 0:
                    show_error(self, "Quantity to add cannot be negative.")
                    return
                p.quantity += add_qty
            except ValueError:
                show_error(self, "Invalid quantity. Enter a valid integer.")
                return

        show_info(self, f"Product '{p.name}' updated successfully.")
        self.accept()


class RemoveExpiredDialog(QDialog):
    def __init__(self, parent, warehouse: Warehouse):
        super().__init__(parent)
        self.setWindowTitle("Remove expired food products")
        self.warehouse = warehouse

        if not is_manager_hours():
            self._blocked_ui("Removing expired products is allowed only between 23:00 and 06:00.")
            return

        removed_any = False
        for product in self.warehouse.products[:]:
            if isinstance(product, FoodProduct) and product.is_expired():
                self.warehouse.products.remove(product)
                removed_any = True

        layout = QVBoxLayout(self)
        if removed_any:
            layout.addWidget(QLabel("Expired products removed."))
        else:
            layout.addWidget(QLabel("No expired products found."))
        btn = QPushButton("OK")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)

    def _blocked_ui(self, msg: str):
        layout = QVBoxLayout(self)
        label = QLabel(msg)
        layout.addWidget(label)
        close_btn = QPushButton("Close")
        layout.addWidget(close_btn)
        close_btn.clicked.connect(self.reject)


class RemoveOutOfWarrantyDialog(QDialog):
    def __init__(self, parent, warehouse: Warehouse):
        super().__init__(parent)
        self.setWindowTitle("Remove out of warranty electronic products")
        self.warehouse = warehouse

        if not is_manager_hours():
            self._blocked_ui("Removing out-of-warranty products is allowed only between 23:00 and 06:00.")
            return

        removed_any = False
        today = datetime.date.today()
        for product in self.warehouse.products[:]:
            if isinstance(product, ElectronicProduct) and not product.is_under_warranty():
                self.warehouse.products.remove(product)
                removed_any = True

        layout = QVBoxLayout(self)
        if removed_any:
            layout.addWidget(QLabel("Out-of-warranty products removed."))
        else:
            layout.addWidget(QLabel("No out-of-warranty products found."))
        btn = QPushButton("OK")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)

    def _blocked_ui(self, msg: str):
        layout = QVBoxLayout(self)
        label = QLabel(msg)
        layout.addWidget(label)
        close_btn = QPushButton("Close")
        layout.addWidget(close_btn)
        close_btn.clicked.connect(self.reject)


class DeleteProductDialog(QDialog):
    def __init__(self, parent, warehouse: Warehouse):
        super().__init__(parent)
        self.setWindowTitle("Delete product by bar code")
        self.warehouse = warehouse

        if not is_manager_hours():
            self._blocked_ui("Deleting products is allowed only between 23:00 and 06:00.")
            return

        form = QFormLayout(self)
        self.barcode_le = QLineEdit()
        form.addRow("Bar Code:", self.barcode_le)

        self.ok_btn = QPushButton("Delete")
        self.cancel_btn = QPushButton("Cancel")
        h = QHBoxLayout()
        h.addWidget(self.ok_btn)
        h.addWidget(self.cancel_btn)
        form.addRow(h)

        self.ok_btn.clicked.connect(self._on_submit)
        self.cancel_btn.clicked.connect(self.reject)

    def _blocked_ui(self, msg: str):
        layout = QVBoxLayout(self)
        label = QLabel(msg)
        layout.addWidget(label)
        close_btn = QPushButton("Close")
        layout.addWidget(close_btn)
        close_btn.clicked.connect(self.reject)

    def _find_by_barcode(self, code: str) -> Optional[Product]:
        for p in self.warehouse.products:
            if p.bar_code == code:
                return p
        return None

    def _on_submit(self):
        code = self.barcode_le.text().strip()
        if not code:
            show_error(self, "Please enter a bar code.")
            return

        p = self._find_by_barcode(code)
        if p is None:
            show_error(self, "No product found with that bar code.")
            return

        reserved_count = sum(r["quantity"] for r in self.warehouse.reserved_products
                             if r["product"].bar_code == code)
        if reserved_count > 0:
            QMessageBox.warning(
                self,
                "Warning",
                f"There are {reserved_count} reserved unit(s) of this product. Only warehouse stock will be deleted."
            )

        self.warehouse.products.remove(p)
        show_info(self, f"Product '{p.name}' deleted from warehouse stock.")
        self.accept()


class AddDiscountDialog(QDialog):
    def __init__(self, parent, warehouse: Warehouse):
        super().__init__(parent)
        self.setWindowTitle("Add discount by bar code")
        self.warehouse = warehouse

        if not is_manager_hours():
            self._blocked_ui("Adding discount is allowed only between 23:00 and 06:00.")
            return

        form = QFormLayout(self)
        self.barcode_le = QLineEdit()
        form.addRow("Bar Code:", self.barcode_le)

        self.percent_sb = QSpinBox()
        self.percent_sb.setRange(1, 100)
        form.addRow("Discount percent (1-100):", self.percent_sb)

        h = QHBoxLayout()
        self.ok_btn = QPushButton("Apply")
        self.cancel_btn = QPushButton("Cancel")
        h.addWidget(self.ok_btn)
        h.addWidget(self.cancel_btn)
        form.addRow(h)

        self.ok_btn.clicked.connect(self._on_submit)
        self.cancel_btn.clicked.connect(self.reject)

    def _blocked_ui(self, msg: str):
        layout = QVBoxLayout(self)
        label = QLabel(msg)
        layout.addWidget(label)
        close_btn = QPushButton("Close")
        layout.addWidget(close_btn)
        close_btn.clicked.connect(self.reject)

    def _find_by_barcode(self, code: str) -> Optional[Product]:
        for p in self.warehouse.products:
            if p.bar_code == code:
                return p
        return None

    def _on_submit(self):
        code = self.barcode_le.text().strip()
        if not code:
            show_error(self, "Please enter a bar code.")
            return

        p = self._find_by_barcode(code)
        if p is None:
            show_error(self, "No product found with that bar code.")
            return

        percent = int(self.percent_sb.value())
        try:
            old_price = p.price
            base = getattr(p, "base_price", p.price)
            p.price = base * (1 - percent / 100)
            show_info(self, f"Discount applied. Old price: {old_price:.2f}, New price: {p.price:.2f}")
            self.accept()
        except Exception as e:
            show_error(self, f"Error applying discount: {e}")


class ReserveProductDialog(QDialog):
    def __init__(self, parent, warehouse: Warehouse):
        super().__init__(parent)
        self.setWindowTitle("Reserve a product")
        self.warehouse = warehouse

        form = QFormLayout(self)

        self.name_cb = QComboBox()
        names = sorted({p.name for p in self.warehouse.products if p.quantity > 0})
        self.name_cb.addItems(names)
        form.addRow("Product name:", self.name_cb)

        self.qty_sb = QSpinBox()
        self.qty_sb.setRange(1, 1_000_000_000)
        form.addRow("Quantity:", self.qty_sb)

        self.dt_res = QDateTimeEdit()
        self.dt_res.setCalendarPopup(True)
        self.dt_res.setDateTime(QDateTime.currentDateTime().addSecs(3600))
        form.addRow("Pickup date/time:", self.dt_res)

        h = QHBoxLayout()
        self.ok_btn = QPushButton("Reserve")
        self.cancel_btn = QPushButton("Cancel")
        h.addWidget(self.ok_btn)
        h.addWidget(self.cancel_btn)
        form.addRow(h)

        self.ok_btn.clicked.connect(self._on_submit)
        self.cancel_btn.clicked.connect(self.reject)

    def _find_by_name(self, name: str) -> Optional[Product]:
        for p in self.warehouse.products:
            if p.name == name:
                return p
        return None

    def _cleanup_expired_reservations(self):
        now = datetime.datetime.now()
        for r in self.warehouse.reserved_products[:]:
            if r["pickup_datetime"] <= now:
                self.warehouse.reserved_products.remove(r)

    def _on_submit(self):
        self._cleanup_expired_reservations()

        name = self.name_cb.currentText().strip()
        p = self._find_by_name(name)
        if p is None:
            show_error(self, "No product found with this name.")
            return

        if not is_product_valid_for_sale_or_reservation(p):
            msg = "Cannot reserve this product: "
            if isinstance(p, FoodProduct):
                msg += "expired."
            elif isinstance(p, ElectronicProduct):
                msg += "out of warranty."
            else:
                msg += "invalid state."
            show_error(self, msg)
            return

        qty = int(self.qty_sb.value())
        if qty <= 0:
            show_error(self, "Invalid quantity.")
            return
        if qty > p.quantity:
            show_error(self, f"Not enough in stock. Available: {p.quantity}")
            return

        dt: datetime.datetime = self.dt_res.dateTime().toPyDateTime()
        if dt <= datetime.datetime.now():
            show_error(self, "Cannot reserve for a past date/time.")
            return

        p.quantity -= qty
        reservation = {
            "product": p,
            "quantity": qty,
            "pickup_datetime": dt
        }
        self.warehouse.reserved_products.append(reservation)
        show_info(self, f"Reserved {qty} '{p.name}' for {dt.strftime('%Y-%m-%d %H:%M')}.")
        self.accept()


class BuyProductDialog(QDialog):
    def __init__(self, parent, warehouse: Warehouse):
        super().__init__(parent)
        self.setWindowTitle("Buy a product")
        self.warehouse = warehouse

        form = QFormLayout(self)

        self.name_cb = QComboBox()
        names = sorted({p.name for p in self.warehouse.products if p.quantity > 0})
        self.name_cb.addItems(names)
        form.addRow("Product name:", self.name_cb)

        self.qty_sb = QSpinBox()
        self.qty_sb.setRange(1, 1_000_000_000)
        form.addRow("Quantity:", self.qty_sb)

        h = QHBoxLayout()
        self.ok_btn = QPushButton("Buy")
        self.cancel_btn = QPushButton("Cancel")
        h.addWidget(self.ok_btn)
        h.addWidget(self.cancel_btn)
        form.addRow(h)

        self.ok_btn.clicked.connect(self._on_submit)
        self.cancel_btn.clicked.connect(self.reject)

    def _find_by_name(self, name: str) -> Optional[Product]:
        for p in self.warehouse.products:
            if p.name == name:
                return p
        return None

    def _on_submit(self):
        name = self.name_cb.currentText().strip()
        p = self._find_by_name(name)
        if p is None:
            show_error(self, "No product found with this name.")
            return

        if not is_product_valid_for_sale_or_reservation(p):
            msg = "Cannot buy this product: "
            if isinstance(p, FoodProduct):
                msg += "expired."
            elif isinstance(p, ElectronicProduct):
                msg += "out of warranty."
            else:
                msg += "invalid state."
            show_error(self, msg)
            return

        qty = int(self.qty_sb.value())
        if qty <= 0:
            show_error(self, "Invalid quantity.")
            return
        if qty > p.quantity:
            show_error(self, f"Not enough in stock. Available: {p.quantity}")
            return

        total = qty * p.price
        p.quantity -= qty
        show_info(self, f"Bought {qty} '{p.name}'. Total to pay: {total:.2f}")
        self.accept()

MENU_TEXT = (
    "/=== MENU ===/\n"
    "1. Add a new product\n"
    "2. Update price/quantity of a product\n"
    "3. Remove all expired products\n"
    "4. Remove all out of warranty products\n"
    "5. Delete any product by their bar code\n"
    "6. Add discount to a product\n"
    "7. Reserve a product now, buy it later\n"
    "8. Buy a product\n"
    "9. Exit program\n"
)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Warehouse GUI")
        self.resize(1100, 700)

        self.warehouse = Warehouse("Main Warehouse")
        try:
            self.warehouse.load_products()
        except Exception:
            pass
        try:
            self.warehouse.load_reservation()
        except Exception:
            pass

        central = QWidget()
        self.setCentralWidget(central)

        root = QVBoxLayout(central)

        top = QHBoxLayout()
        root.addLayout(top, 1)

        left = QVBoxLayout()
        top.addLayout(left, 1)

        self.menu_view = QTextEdit()
        self.menu_view.setReadOnly(True)
        self.menu_view.setFont(QFont("Courier New", 11))
        self.menu_view.setPlainText(MENU_TEXT)
        left.addWidget(QLabel("Menu"))
        left.addWidget(self.menu_view, 3)

        input_row = QHBoxLayout()
        self.cmd_input = QLineEdit()
        self.cmd_input.setPlaceholderText("Enter a number 1-9")
        self.submit_btn = QPushButton("Submit")
        self.submit_btn.clicked.connect(self.handle_command)
        input_row.addWidget(self.cmd_input)
        input_row.addWidget(self.submit_btn)
        left.addLayout(input_row)

        right = QVBoxLayout()
        top.addLayout(right, 1)

        cat_row = QHBoxLayout()
        self.btn_food = QPushButton("Food Products")
        self.btn_elec = QPushButton("Electronic Products")
        self.btn_clo = QPushButton("Clothing Products")
        self.btn_all = QPushButton("All")
        cat_row.addWidget(self.btn_food)
        cat_row.addWidget(self.btn_elec)
        cat_row.addWidget(self.btn_clo)
        cat_row.addWidget(self.btn_all)
        right.addLayout(cat_row)

        self.btn_food.clicked.connect(lambda: self.populate_table("Food"))
        self.btn_elec.clicked.connect(lambda: self.populate_table("Electronic"))
        self.btn_clo.clicked.connect(lambda: self.populate_table("Clothing"))
        self.btn_all.clicked.connect(lambda: self.populate_table(None))

        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "Type", "Name", "Price", "Quantity", "Description", "Bar Code",
            "Exp/Warranty", "Reservation Date/Time", "Reserved"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        right.addWidget(self.table, 5)

        self.populate_table(None)

    def collect_rows(self, filter_type: Optional[str]):
        """Return list of rows (tuple) for table, combining products and reservations."""
        rows = []
        for p in self.warehouse.products:
            tname = product_type_name(p)
            if filter_type and tname != filter_type:
                continue
            rows.append((
                tname, p.name, f"{p.price:.2f}", str(p.quantity), p.description,
                p.bar_code, product_exp_warranty_str(p), "", "No"
            ))
        for r in self.warehouse.reserved_products:
            p = r["product"]
            qty = r["quantity"]
            dt = r["pickup_datetime"].strftime("%Y-%m-%d %H:%M")
            tname = product_type_name(p)
            if filter_type and tname != filter_type:
                continue
            rows.append((
                tname, p.name, f"{p.price:.2f}", str(qty), p.description,
                p.bar_code, product_exp_warranty_str(p), dt, "Yes"
            ))
        return rows

    def populate_table(self, filter_type: Optional[str]):
        rows = self.collect_rows(filter_type)
        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, cell in enumerate(row):
                item = QTableWidgetItem(cell)
                if j in (2, 3):
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                else:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                self.table.setItem(i, j, item)
        self.table.resizeColumnsToContents()

    def handle_command(self):
        cmd = self.cmd_input.text().strip()
        if cmd not in [str(i) for i in range(1, 10)]:
            show_error(self, "Invalid option. Enter a number 1-9.")
            return

        if cmd == "1":
            dlg = AddProductDialog(self, self.warehouse)
            if dlg.exec():
                self.populate_table(None)

        elif cmd == "2":
            dlg = UpdateProductDialog(self, self.warehouse)
            if dlg.exec():
                self.populate_table(None)

        elif cmd == "3":
            dlg = RemoveExpiredDialog(self, self.warehouse)
            dlg.exec()
            self.populate_table(None)

        elif cmd == "4":
            dlg = RemoveOutOfWarrantyDialog(self, self.warehouse)
            dlg.exec()
            self.populate_table(None)

        elif cmd == "5":
            dlg = DeleteProductDialog(self, self.warehouse)
            if dlg.exec():
                self.populate_table(None)

        elif cmd == "6":
            dlg = AddDiscountDialog(self, self.warehouse)
            if dlg.exec():
                self.populate_table(None)

        elif cmd == "7":
            dlg = ReserveProductDialog(self, self.warehouse)
            if dlg.exec():
                self.populate_table(None)

        elif cmd == "8":
            dlg = BuyProductDialog(self, self.warehouse)
            if dlg.exec():
                self.populate_table(None)

        elif cmd == "9":
            self.warehouse.save_products()
            self.warehouse.save_reservation()
            show_info(self, "Thank you for stopping by. See you later!")
            QApplication.instance().quit()

        self.cmd_input.clear()

    def closeEvent(self, event):
        try:
            self.warehouse.save_products()
            self.warehouse.save_reservation()
        except Exception:
            pass
        event.accept()


def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
