import tkinter as tk
from tkinter import ttk, messagebox
import pymysql
from PIL import Image, ImageTk
import os

# Connect to MySQL database and create if it doesn't exist
conn = pymysql.connect(
    host="localhost",
    user="root",
    password="1234"
)
cursor = conn.cursor()
cursor.execute("CREATE DATABASE IF NOT EXISTS inventory_db")
cursor.execute("USE inventory_db")

# Create required tables if they don't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS User(
    UserID INT PRIMARY KEY AUTO_INCREMENT,
    Username VARCHAR(50) NOT NULL UNIQUE,
    Password VARCHAR(100) NOT NULL,
    Role ENUM('admin', 'staff') NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Product(
    ProductID INT PRIMARY KEY AUTO_INCREMENT,
    ProductName VARCHAR(100) NOT NULL,
    CategoryID INT,
    QuantityInStock INT DEFAULT 0,
    ReorderLevel INT DEFAULT 10
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Customer(
    CustomerID INT PRIMARY KEY AUTO_INCREMENT,
    CustomerName VARCHAR(100),
    ContactInfo VARCHAR(100)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Supplier(
    SupplierID INT PRIMARY KEY AUTO_INCREMENT,
    SupplierName VARCHAR(100),
    ContactInfo VARCHAR(100)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Transaction(
    TransactionID INT PRIMARY KEY AUTO_INCREMENT,
    ProductID INT,
    Quantity INT,
    Type ENUM('purchase', 'sale'),
    TransactionDate DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

# Insert a default admin user if none exists
cursor.execute("SELECT * FROM User WHERE Username = 'admin'")
if cursor.fetchone() is None:
    cursor.execute("INSERT INTO User (Username, Password, Role) VALUES ('admin', 'admin123', 'admin')")
    conn.commit()

def create_dashboard(editable=True):
    dashboard = tk.Toplevel()
    dashboard.title("Dashboard")
    dashboard.geometry("800x600")

    canvas = tk.Canvas(dashboard, width=800, height=600)
    canvas.pack(fill="both", expand=True)

    try:
        bg_img = Image.open("assets/dashboard_bg.jpg").resize((800, 600))
        bg = ImageTk.PhotoImage(bg_img)
        canvas.create_image(0, 0, image=bg, anchor="nw")
        canvas.image = bg
    except:
        pass

    title = "Admin Dashboard" if editable else "Staff Dashboard"
    canvas.create_text(400, 30, text=title, font=("Arial", 24, "bold"), fill="white")

    tables = ["Product", "Customer", "Supplier", "Transaction"]

    def view_table(table_name):
        view_win = tk.Toplevel(dashboard)
        view_win.title(table_name)
        view_win.geometry("800x400")

        tree = ttk.Treeview(view_win, show="headings")
        tree.pack(fill=tk.BOTH, expand=True)

        cursor.execute(f"DESCRIBE {table_name}")
        columns = [col[0].strip() for col in cursor.fetchall()]
        tree["columns"] = columns

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor=tk.CENTER, width=120, stretch=False)

        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        for row in rows:
            clean_row = tuple(str(item).strip() if isinstance(item, str) else item for item in row)
            tree.insert("", "end", values=clean_row)

        if editable:
            def update_record():
                selected = tree.focus()
                values = tree.item(selected, 'values')
                if not values:
                    return messagebox.showwarning("Select Record", "Please select a record to update.")
                update_win = tk.Toplevel(view_win)
                update_win.title("Update Record")
                entries = []
                for idx, field in enumerate(columns):
                    tk.Label(update_win, text=field).grid(row=idx, column=0)
                    entry = tk.Entry(update_win)
                    entry.grid(row=idx, column=1)
                    entry.insert(0, str(values[idx]).strip())
                    entries.append(entry)

                def save():
                    new_vals = [entry.get().strip() for entry in entries]
                    pk_col = columns[0]
                    update_stmt = f"UPDATE {table_name} SET " + ", ".join(
                        [f"{col}=%s" for col in columns[1:]]) + f" WHERE {pk_col}=%s"
                    cursor.execute(update_stmt, (*new_vals[1:], new_vals[0]))
                    conn.commit()
                    messagebox.showinfo("Success", "Record updated successfully")
                    update_win.destroy()
                    view_win.destroy()
                    view_table(table_name)

                tk.Button(update_win, text="Save", command=save).grid(row=len(columns), columnspan=2)

            def add_record():
                add_win = tk.Toplevel(view_win)
                add_win.title("Add Record")
                entries = []
                for idx, field in enumerate(columns[1:]):
                    tk.Label(add_win, text=field).grid(row=idx, column=0)
                    entry = tk.Entry(add_win)
                    entry.grid(row=idx, column=1)
                    entries.append(entry)

                def save():
                    new_vals = [entry.get().strip() for entry in entries]
                    placeholders = ", ".join(["%s"] * len(new_vals))
                    cursor.execute(
                        f"INSERT INTO {table_name} ({', '.join(columns[1:])}) VALUES ({placeholders})",
                        new_vals
                    )
                    conn.commit()
                    messagebox.showinfo("Success", "Record added successfully")
                    add_win.destroy()
                    view_win.destroy()
                    view_table(table_name)

                tk.Button(add_win, text="Add", command=save).grid(row=len(columns), columnspan=2)

            btn_frame = tk.Frame(view_win)
            btn_frame.pack(pady=5)
            tk.Button(btn_frame, text="Update Record", command=update_record).pack(side=tk.LEFT, padx=10)
            tk.Button(btn_frame, text="Add Record", command=add_record).pack(side=tk.LEFT, padx=10)

        tk.Button(view_win, text="Back", command=view_win.destroy).pack(pady=10, side=tk.BOTTOM)

    for i, table in enumerate(tables):
        tk.Button(dashboard, text=table.strip(), width=20, command=lambda t=table.strip(): view_table(t)).place(x=300, y=100+i*60)

    tk.Button(dashboard, text="Back", command=lambda: [dashboard.destroy(), root.deiconify()]).place(x=360, y=550)

# ... (rest of the code remains unchanged)






       

def signup_window():
    signup_win = tk.Toplevel()
    signup_win.title("Sign Up")
    signup_win.geometry("400x350")

    canvas = tk.Canvas(signup_win, width=400, height=350)
    canvas.pack(fill="both", expand=True)
    try:
        bg_img = Image.open("assets/signup_bg.jpg").resize((500, 400))
        bg = ImageTk.PhotoImage(bg_img)
        canvas.create_image(0, 0, image=bg, anchor="nw")
        canvas.image = bg
    except:
        pass

    canvas.create_text(200, 40, text="Sign Up", font=("Arial", 20, "bold"), fill="white")
    canvas.create_text(100, 100, text="Username", font=("Arial", 12), fill="white", anchor="e")
    username = tk.Entry(signup_win)
    canvas.create_window(110, 100, anchor="w", window=username, width=200)

    canvas.create_text(100, 140, text="Password", font=("Arial", 12), fill="white", anchor="e")
    password = tk.Entry(signup_win, show="*")
    canvas.create_window(110, 140, anchor="w", window=password, width=200)

    canvas.create_text(100, 180, text="Select Role", font=("Arial", 12), fill="white", anchor="e")
    role_var = tk.StringVar()
    role_dropdown = ttk.Combobox(signup_win, textvariable=role_var, values=["admin", "staff"], state="readonly")
    canvas.create_window(110, 180, anchor="w", window=role_dropdown, width=200)
    role_dropdown.current(1)

    def register():
        user = username.get()
        pwd = password.get()
        role = role_var.get()
        try:
            cursor.execute("INSERT INTO User (Username, Password, Role) VALUES (%s, %s, %s)", (user, pwd, role))
            conn.commit()
            messagebox.showinfo("Success", "User registered successfully")
            signup_win.destroy()
        except pymysql.IntegrityError:
            messagebox.showerror("Error", "Username already exists")

    sign_btn = tk.Button(signup_win, text="Sign Up", command=register, bg="#6C63FF", fg="white")
    canvas.create_window(200, 230, window=sign_btn)

    back_btn = tk.Button(signup_win, text="Back", command=signup_win.destroy)
    canvas.create_window(200, 270, window=back_btn)

def open_login_window(role):
    if role == "admin":
        admin_dashboard()
    elif role == "staff":
        staff_dashboard()

def admin_dashboard():
    root.withdraw()
    create_dashboard(editable=True)

def staff_dashboard():
    root.withdraw()
    create_dashboard(editable=False)

def login_window():
    global root
    root = tk.Tk()
    root.title("Login or Sign Up")
    root.geometry("500x400")

    canvas = tk.Canvas(root, width=500, height=400)
    canvas.pack(fill="both", expand=True)

    try:
        bg_img = Image.open("assets/login_bg.jpg").resize((500, 400))
        bg = ImageTk.PhotoImage(bg_img)
        canvas.create_image(0, 0, image=bg, anchor="nw")
        canvas.image = bg
    except:
        pass

    canvas.create_text(250, 50, text="Login", font=("Arial", 24, "bold"), fill="white")

    canvas.create_text(140, 120, text="Username", font=("Arial", 14), fill="white", anchor="e")
    username = tk.Entry(root)
    canvas.create_window(150, 120, anchor="w", window=username, width=200)

    canvas.create_text(140, 160, text="Password", font=("Arial", 14), fill="white", anchor="e")
    password = tk.Entry(root, show="*")
    canvas.create_window(150, 160, anchor="w", window=password, width=200)

    def login():
        user = username.get()
        pwd = password.get()
        cursor.execute("SELECT Role FROM User WHERE Username=%s AND Password=%s", (user, pwd))
        result = cursor.fetchone()
        if result:
            role = result[0]
            messagebox.showinfo("Login Success", f"Logged in as {role}")
            root.withdraw()
            open_login_window(role)
        else:
            messagebox.showerror("Login Failed", "Invalid credentials")

    login_btn = tk.Button(root, text="Login", command=login, bg="#4CAF50", fg="white")
    canvas.create_window(200, 220, window=login_btn)

    signup_btn = tk.Button(root, text="Sign Up", command=signup_window, bg="#2196F3", fg="white")
    canvas.create_window(300, 220, window=signup_btn)

    root.mainloop()

# Start with login window
login_window()
