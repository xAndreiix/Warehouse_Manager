# Warehouse Management System (Python)

This project is a **warehouse management system** built in Python, designed to simulate real-world warehouse operations.  
It includes support for multiple product categories, product reservations, purchase logic, warranty/expiration checks, and manager-only operations during restricted hours.  

The system also comes with a simple **graphical interface** (using PyQt6) that mirrors the command-line menu.  

---

## 🚀 Features

- **Product categories:**
  - Food Products (with expiration dates)
  - Electronic Products (with warranty dates)
  - Clothing Products (with size, color, material)

- **Core functionalities:**
  - Add new products
  - Update product details
  - Buy products
  - Reserve products for later pickup
  - Apply discounts
  - Delete products
  - Automatically remove expired or out-of-warranty items

- **Reservation system:**
  - Products can be reserved for a future date & time
  - Expired reservations are automatically cleared
  - Reserved products show separately from warehouse stock

- **Business rules enforced:**
  - Expired food items cannot be purchased or reserved
  - Electronics out of warranty cannot be purchased or reserved
  - Manager-only operations (e.g., adding/removing products, discounts) are allowed only between **23:00–06:00**

- **Graphical UI (PyQt6):**
  - Main window with:
    - Menu (select operations by number + submit button)
    - Category buttons (Food / Electronics / Clothing)
    - Product list displayed per category (warehouse + reservations)
  - Each operation opens a new window for user input
  - Success and error messages shown in dialogs

---

## 🛠️ Project Structure

- 📁 warehouse-management/
- │
- ├── products.py         # Defines Product base class + Food, Electronics, Clothing subclasses
- ├── warehouse.py        # Core warehouse logic (inventory, reservations, buying, etc.)
- ├── decorators.py       # Business logic decorator (manager-only actions restricted to 23:00–06:00)
- ├── main.py             # Entry point – CLI + GUI menu
- ├── test_warehouse.py
- ├── test_decorators.py
- ├── .gitignore file
- ├── MIT License file
- ├── requirements.txt    # Python dependencies
- └── README.md           # Project documentation

---

## 📦 Installation

1. Clone this repository:

- git clone https://github.com/xAndreiix/Warehouse-Manager.git
cd warehouse-management

2. (Optional but recommended) Create a virtual environment:

- python -m venv venv
- source venv/bin/activate   # On Linux/Mac
- venv\Scripts\activate      # On Windows

3. Install dependencies:

- pip install -r requirements.txt

---

▶️ Usage

- Run the program:
python main.py


- The main window will show the warehouse menu and product categories.
- Choose an option by entering its number and pressing Submit.
- Or click a category button (Food / Electronics / Clothing) to view available products.
- When performing actions (buying, reserving, adding, etc.), a new input window will open.
- Messages will guide you if the action succeeds or fails.

---

✅ Requirements

- Python 3.9+
- Dependencies listed in requirements.txt

---

🧪 Code Testing
- python -m unittest test_warehouse.py
- python -m unittest test_decorators.py

---

🧩 Example Workflow

- Start program → main window opens with menu.
- Click Food Products → see all food items (with expiration dates).
- Choose menu option 3 (Buy Product) → input name + quantity → success message shows.
- Try to reserve an expired product → system blocks with warning.
- Manager logs in at 23:30 → can add new stock and apply discounts.

---

📌 Notes
- Manager-only actions (add_product, update_products, remove_expired_products, remove_out_of_warranty_products, delete_products, add_discount) are restricted to 23:00–06:00.
- Customers can buy or reserve anytime, but outside business hours the action is logged for the next business day.

---

📜 License
- This project is released under the MIT License.
- You are free to use, modify, and distribute it.
