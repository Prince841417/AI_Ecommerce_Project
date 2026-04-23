from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import random
import razorpay 
from ai_engine import hybrid_recommendation
app = Flask(__name__)
app.secret_key = "supersecretkey"

DATABASE = "database.db"

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "database.db")

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# ================= Razorpay key ============

RAZORPAY_KEY_ID = "rzp_test_SI5PDSMDKsznnH"
RAZORPAY_KEY_SECRET = "V5zSdhc3dvZF5CLPltXBzJvh"

client = razorpay.Client(auth=(RAZORPAY_KEY_ID,
RAZORPAY_KEY_SECRET))


# ================= DATABASE INIT =================

def init_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # USERS
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    # PRODUCTS
    c.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        price INTEGER,
        image TEXT,
        category TEXT
    )
    """)
    # CART
    c.execute("""
   CREATE TABLE IF NOT EXISTS cart (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    product_id INTEGER
    )
    """)

    # ORDERS
    c.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        product_name TEXT,
        price INTEGER,
        image TEXT,
        order_date TEXT,
        payment_id TEXT,
        status TEXT

    )
    """)

    conn.commit()

    # Insert products only if empty
    c.execute("SELECT COUNT(*) FROM products")
    if c.fetchone()[0] == 0:
        products = [
                       ### category: Electronics

            ("Laptop", 55000, "laptop.jpg", "Electronics"),
            ("SmartPhone", 20000, "phone.jpg", "Electronics"),
            ("Smartwatch", 15000, "Smartwatch.jpg", "Electronics"),
            ("Headphone", 4500, "head.jpg", "Electronics"),
            ("Bluetooth Speaker", 3500, "Speaker.jpg", "Electronics"),
            ("Tablet", 25000, "Tablet.jpg", "Electronics"),
            ("DSLR Camera", 45000, "camera.jpg", "Electronics"),
            ("Gaming Console", 4000, "Gaming console.jpg", "Electronics"),
            ("Smart TV", 45000, "Smart Tv.jpg", "Electronics"),
            ("Keyboard", 400, "t2.jpg", "Electronics"),

                ### category: Fashionsssss
            ("T-Shirt", 800, "mtshirt.jpg", "Fashion"),
            ("Jeans", 1800, "t4.jpg", "Fashion"),
            ("Sneakers", 2500, "Sneakers.jpg", "Fashion"),
            ("Jacket", 350, "t3.jpg", "Fashion"),
            ("Hoodie", 500, "Hoodie.jpg", "Fashion"),
            ("Kurta", 300, "Kurta.jpg", "Fashion"),
            ("Saree", 5000, "Saree.jpg", "Fashion"),
            ("Formal Shirt", 305, "Formal Shirt.jpg", "Fashion"),
            ("Leather Belt", 250, "Leather Belt.jpg", "Fashion"),
            ("Sunglasses", 1200, "Sunglasses.jpg", "Fashion"),
            


            #### category: Home and Kitchen
            ("Microwave Oven", 3000, "miccc.jpg", " Home & Kitchen"),
            ("Refrigerator", 25000, "Refrigertor.jpg", " Home & Kitchen"),
            ("Electric Kettle", 1500, "kettle.jpg", " Home & Kitchen"),
            ("Mixer Grinder", 1200, "mixer.jpg", " Home & Kitchen"),
            ("Coffee Maker", 1500, "coffee.jpg", " Home & Kitchen"),
            ("Gas Stove", 5000, "gas.jpg", " Home & Kitchen"),
            ("Lunch Box", 120, "lunch.jpg", " Home & Kitchen"),
            ("Water Purifier", 2500, "water.jpg", " Home & Kitchen"),
            ("Pressure Cooker", 3000, "pre.jpg", " Home & Kitchen"),
             ("Dish Drying Rack", 4500, "dish.jpg", " Home & Kitchen"),
             
             ### category: Beauty and Personal Care
            ("Lipstick", 500, "lapstick.jpg", "Beauty & Personal Care"),
            ("Hair Dryer", 1500, "hair.jpg", "Beauty & Personal Care"),
            ("Face Wash", 800, "face.jpg", "Beauty & Personal Care"),
            ("Makeup Kit", 2000, "makeup.jpg", "Beauty & Personal Care"),
            ("Perfume Luxury", 2000, "Perfume.jpg", "Beauty & Personal Care"),

              ### category: Sports and Fitness
            ("Cricket Bat", 3500, "bat.jpg", "Sports & Fitness"),
            ("Football", 2500, "bootball.jpg", "Sports & Fitness"),
            ("Yoga Mat", 1200, "yoga.jpg", "Sports & Fitness"),   
            ("Tennis Ball", 1000, "Tennis Ball.jpg", "Sports & Fitness"), 
            ("Basketball", 1100, "Basketball.jpg", "Sports & Fitness"),  
            ("Skipping Rope", 1500, "Skipping Rope.jpg", "Sports & Fitness"),   
            ("Cycling Helmet", 1800, "Cycling Helmet.jpg", "Sports & Fitness"),
            ("Fitness Band", 2000, "Fitness Band.jpg", "Sports & Fitness"),    
            ("Dumbbel Set", 5000, "dum.jpg", "Sports & Fitness"),  
            ("Gym Bag", 1000, "gym.jpg", "Sports & Fitness"), 
            
            ## category : Food and Heathcare
            ("Basmati Rice", 500, "basmati.jpg", "Food & Heathcare"),
            ("Honey", 800, "honey.jpg", "Food & Heathcare"),
            ("Dry Fruits Mix", 600, "fruits.jpg", "Food & Heathcare"),
            ("Peanut Butter", 400, "peanut.jpg", "Food & Heathcare"),
            ("First Aid Kit", 500, "fir.jpg", "Food & Heathcare"),
            ("Vitamin C Tablets", 200, "vitamin.jpg", "Food & Heathcare"),
            ("Digital Thermometer", 500, "ther.jpg", "Food & Heathcare"),
            ("Blood Pressure Monitor", 900, "bl.jpg", "Food & Heathcare"),
            ("Sanitary Pads", 50, "pra.jpg", "Food & Heathcare"),
            ("Glucose Powder", 340, "g.jpg", "Food & Heathcare"),

           
        ]

        c.executemany("INSERT INTO products (name,price,image,category) VALUES (?,?,?,?)", products)
        conn.commit()

    conn.close()

init_db()

# ================= HOME =================
@app.route("/")
def home():

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Get all products
    cur.execute("SELECT * FROM products")
    products = cur.fetchall()

    # Category wise grouping
    category_products = {}

    for p in products:
        category = p["category"]

        if category not in category_products:
            category_products[category] = []

        category_products[category].append(p)

    recommended_products = []

    if "cart" in session and session["cart"]:

        ids = tuple(session["cart"])

        query = "SELECT * FROM products WHERE id IN ({})".format(
            ",".join(["?"] * len(ids))
        )

        cur.execute(query, ids)

        cart_products = cur.fetchall()

        recommended_products = hybrid_recommendation(cart_products)

    return render_template(
        "home.html",
        category_products=category_products,
        recommended_products=recommended_products
    )
   #============ Register=======================
@app.route('/register', methods=['GET','POST'])
def register():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()

        # check user exists
        c.execute("SELECT * FROM users WHERE username=?", (username,))
        user = c.fetchone()

        if user:
            return render_template("register.html", error="Username already exists")

        c.execute("INSERT INTO users (username,password) VALUES (?,?)",
                  (username,password))

        conn.commit()
        conn.close()

        return redirect('/login')

    return render_template("register.html")
# ================= LOGIN =================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            session['user_id'] = user[0]   
            session['username'] = user[1]  
            return redirect(url_for('home'))

    return render_template("login.html")


# ================= LOGOUT =================

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ================= dashboard =================
@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # Total Orders
    c.execute("SELECT COUNT(*) FROM orders WHERE user_id=?", (session["user_id"],))
    total_orders = c.fetchone()[0]

    # Total Spending
    c.execute("SELECT SUM(price) FROM orders WHERE user_id=?", (session["user_id"],))
    result = c.fetchone()[0]
    total_spending = result if result else 0

    # Cart Activity
    c.execute("SELECT COUNT(*) FROM cart WHERE user_id=?", (session["user_id"],))
    cart_activity = c.fetchone()[0]

    return render_template(
        "dashboard.html",
        user=session["username"],   
        total_orders=total_orders,
        total_spending=total_spending,
    )

###==============chartbot==============================
@app.route("/chatbot", methods=["POST"])
def chatbot():

    data = request.get_json()
    message = data["message"].lower()

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # greeting
    if "hi" in message or "hello" in message:
        reply = "Hello 👋 I am SmartCart AI assistant. Ask me to recommend products."

    # electronics
    elif "laptop" in message or "electronics" in message or "phone" in message:

        c.execute("SELECT name, price FROM products WHERE category='electronics' LIMIT 3")
        products = c.fetchall()

        reply = "Recommended Electronics:\n"

        for p in products:
            reply += f"• {p[0]} - ₹{p[1]}\n"

    # fashion
    elif "fashion" in message or "clothes" in message or "shoes" in message:

        c.execute("SELECT name, price FROM products WHERE category='fashion' LIMIT 3")
        products = c.fetchall()

        reply = "Recommended Fashion Products:\n"

        for p in products:
            reply += f"• {p[0]} - ₹{p[1]}\n"

    # trending products
    elif "trending" in message or "popular" in message:

        c.execute("SELECT name, price FROM products LIMIT 3")
        products = c.fetchall()

        reply = "Trending Products:\n"

        for p in products:
            reply += f"• {p[0]} - ₹{p[1]}\n"

    # order help
    elif "order" in message:

        reply = "You can check your order history in the Orders section."

    else:

        reply = "You can ask:\n• recommend laptop\n• show fashion\n• trending products"

    conn.close()

    return {"reply": reply}

# ================= ADD TO CART =================
@app.route("/add_to_cart/<int:product_id>")
def add_to_cart(product_id):

    if "cart" not in session:
        session["cart"] = []

    session["cart"].append(product_id)

    session.modified = True

    return redirect("/cart")

# ================= CART =================
@app.route("/cart")
def cart():

    if "cart" not in session:
        session["cart"] = []

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    items = []
    total = 0

    for product_id in session["cart"]:
        c.execute("SELECT * FROM products WHERE id=?", (product_id,))
        product = c.fetchone()
        if product:
            items.append(product)
            total += product["price"]

    conn.close()

    return render_template("cart.html", items=items, total=total)
# ================= remove from cart=================
@app.route("/remove_from_cart/<int:product_id>")
def remove_from_cart(product_id):

    if "cart" in session:
        session["cart"] = [p for p in session["cart"] if p != product_id]

    return redirect("/cart")

# ================= CHECKOUT =================
@app.route("/checkout")
def checkout():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if "cart" not in session or len(session["cart"]) == 0:
        return redirect(url_for("home"))

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    total_amount = 0
    product_names = []
    product_images = []

    for pid in session["cart"]:
        c.execute("SELECT name, price, image FROM products WHERE id=?", (pid,))
        product = c.fetchone()

        if product:
            product_names.append(product[0])
            product_images.append(product[2])
            total_amount += product[1]

    conn.close()

    # SAVE IN SESSION (VERY IMPORTANT)
    session["product_name"] = ", ".join(product_names)
    session["price"] = total_amount
    session["image"] = product_images[0] if product_images else ""

    # Razorpay expects amount in paise
    order = client.order.create({
        "amount": total_amount * 100,
        "currency": "INR",
        "payment_capture": 1
    })

    return render_template(
        "payment.html",
        total=total_amount,
        razorpay_order_id=order["id"],
        razorpay_key=RAZORPAY_KEY_ID
    )
# ================== ORDER HISTORY ==================
@app.route("/orders")
def orders():

    if "user_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # Only show orders of logged in user
    c.execute(
        "SELECT * FROM orders WHERE user_id = ?",
        (session["user_id"],)
    )

    orders = c.fetchall()

    return render_template("orders.html", orders=orders)
# ================= INVOICE =================
@app.route("/invoice/<int:order_id>")
def invoice(order_id):

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute("SELECT * FROM orders WHERE id=?", (order_id,))
    order = c.fetchone()

    conn.close()

    if not order:
        return "Order not found"

    return render_template("invoice.html", order=order)

    # ================= download_invoice=================
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from flask import send_file
import sqlite3
import io
from datetime import datetime


@app.route("/download_invoice/<int:order_id>")
def download_invoice(order_id):

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute("SELECT * FROM orders WHERE id=?", (order_id,))
    order = c.fetchone()
    conn.close()

    if not order:
        return "Order not found"

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)

    elements = []
    styles = getSampleStyleSheet()

    # ===== COMPANY HEADER =====
    elements.append(Paragraph("<b>PRINCE ENTERPRISES</b>", styles['Title']))
    elements.append(Paragraph("Uma Complex, Mashrak Saran 841417", styles['Normal']))
    elements.append(Paragraph("Email: princeyadavmashrak@gmail.com", styles['Normal']))
    elements.append(Spacer(1, 0.3 * inch))

    # ===== INVOICE DETAILS =====
    invoice_no = f"INV-{order['id']:05d}"
    date = order['order_date']
    payment_id = order['payment_id']
    status = order['status']

    details_data = [
        ["Invoice No:", invoice_no],
        ["Date:", date],
        ["Payment ID:", payment_id],
        ["Order Status:", status],
    ]

    details_table = Table(details_data, colWidths=[120, 250])
    details_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('BACKGROUND', (0,0), (0,-1), colors.whitesmoke),
    ]))

    elements.append(details_table)
    elements.append(Spacer(1, 0.4 * inch))

    # ===== PRODUCT TABLE =====
    price = order['price']
    subtotal = price
    tax = round(subtotal * 0.00, 2)  # 0% tax (change if needed)
    grand_total = subtotal + tax

    product_data = [
        ["Description", "Qty", "Unit Price", "Line Total"],
        [order['product_name'], "1", f"₹ {price}", f"₹ {price}"],
    ]

    product_table = Table(product_data, colWidths=[180, 50, 100, 100])
    product_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('ALIGN', (1,1), (-1,-1), 'CENTER'),
    ]))

    elements.append(product_table)
    elements.append(Spacer(1, 0.3 * inch))

    # ===== TOTAL SECTION =====
    total_data = [
        ["Subtotal", f"₹ {subtotal}"],
        ["Tax (0%)", f"₹ {tax}"],
        ["Grand Total", f"₹ {grand_total}"],
    ]

    total_table = Table(total_data, colWidths=[330, 100])
    total_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('BACKGROUND', (0,2), (-1,2), colors.yellow),
    ]))

    elements.append(total_table)
    elements.append(Spacer(1, 0.5 * inch))

    # ===== FOOTER =====
    elements.append(Paragraph("Thank you for shopping with Prince Enterprises.", styles['Normal']))
    elements.append(Paragraph("For support contact: princeyadavmashrak@gmail.com", styles['Normal']))

    doc.build(elements)

    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"Invoice_{order_id}.pdf",
        mimetype='application/pdf'
    )
# ================= CANCEL ORDER =================
@app.route("/cancel_order/<int:order_id>")
def cancel_order(order_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Update order status
    c.execute("""
        UPDATE orders
        SET status = ?
        WHERE id = ? AND user_id = ?
    """, ("Cancelled", order_id, session["user_id"]))

    conn.commit()
    conn.close()

    return redirect(url_for("orders"))

# ================= payment =================
@app.route("/payment")
def payment():

    if "cart" not in session or len(session["cart"]) == 0:
        return redirect("/cart")

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    items = []
    total = 0

    for product_id in session["cart"]:
        c.execute("SELECT * FROM products WHERE id=?", (product_id,))
        product = c.fetchone()
        if product:
            items.append(product)
            total += product["price"]

    conn.close()

    return render_template("payment.html",
                           items=items,
                           total=total,
                           key_id=RAZORPAY_KEY_ID)
# ================= payment_success=================
from datetime import datetime
import uuid

@app.route("/payment_success", methods=["GET", "POST"])
def payment_success():

    if "cart" not in session or len(session["cart"]) == 0:
        return redirect("/")

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    payment_id = "PAY" + str(uuid.uuid4())[:8]   # generate random payment id

    for product_id in session["cart"]:

        c.execute("SELECT * FROM products WHERE id=?", (product_id,))
        product = c.fetchone()

        if product:
            c.execute("""
                INSERT INTO orders 
                (user_id, product_name, price, image, order_date, payment_id, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                session.get("user_id", 1),
                product["name"],
                product["price"],
                product["image"],
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                payment_id,
                "Paid"
            ))

    conn.commit()
    conn.close()

    # clear cart
    session.pop("cart", None)

    return render_template("payment_success.html")
# ================= PRODUCT DETAILS =================
@app.route("/product/<int:id>")
def product_details(id):

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute("SELECT * FROM products WHERE id=?", (id,))
    product = c.fetchone()

    return render_template("product_details.html", product=product)

###=========search=================
@app.route("/search", methods=["GET"])
def search_products():

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    search = request.args.get("search")

    if search:
        query = """
            SELECT * FROM products
            WHERE name LIKE ?
            OR category LIKE ?
        """
        cursor.execute(query, (
            f"%{search}%",
            f"%{search}%",
        ))
    else:
        cursor.execute("SELECT * FROM products")

    products = cursor.fetchall()
    conn.close()

    return render_template("index.html", products=products)

# ================= run =================
if __name__ == "__main__":
    init_db()
    app.run(debug=True)