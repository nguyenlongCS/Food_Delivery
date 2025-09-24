from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
CORS(app)

# -------------------------
# Configuration
# -------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOADS_DIR = os.path.join(BASE_DIR, 'uploads')

# Tạo folder uploads nếu chưa tồn tại
os.makedirs(UPLOADS_DIR, exist_ok=True)


# -------------------------
# Serve uploaded images
# -------------------------
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOADS_DIR, filename)


# -------------------------
# Database connection
# -------------------------
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="longga1505",
        database="FoodDelivery"
    )


# -------------------------
# User registration
# -------------------------
@app.route("/api/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    confirm_password = data.get("confirm_password")

    if password != confirm_password:
        return jsonify({"success": False, "message": "Mật khẩu xác nhận không khớp!"})

    hashed_pw = generate_password_hash(password)

    try:
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO user (username, email, password, role) VALUES (%s, %s, %s, %s)",
            (username, email, hashed_pw, "user")
        )
        db.commit()
        return jsonify({"success": True, "message": "Đăng ký thành công!"})
    except mysql.connector.Error as e:
        return jsonify({"success": False, "message": f"Lỗi: {str(e)}"})
    finally:
        cursor.close()
        db.close()


# -------------------------
# User login
# -------------------------
@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user WHERE username=%s", (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user["password"], password):
            return jsonify({
                "success": True,
                "user": {
                    "id": user["id"],
                    "username": user["username"],
                    "email": user["email"]
                }
            })
        else:
            return jsonify({"success": False, "message": "Sai tên đăng nhập hoặc mật khẩu!"})
    except mysql.connector.Error as e:
        return jsonify({"success": False, "message": f"Lỗi: {str(e)}"})
    finally:
        cursor.close()
        db.close()


# -------------------------
# Get menu items
# -------------------------
@app.route("/api/menu", methods=["GET"])
def get_menu():
    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM menu_items")
        items = cursor.fetchall()
        return jsonify({"success": True, "items": items})
    except mysql.connector.Error as e:
        return jsonify({"success": False, "message": f"Lỗi: {str(e)}"})
    finally:
        cursor.close()
        db.close()


# -------------------------
# Cart operations
# -------------------------
@app.route("/api/cart", methods=["POST"])
def add_to_cart():
    data = request.json
    user_id = data.get("user_id")
    item_id = data.get("item_id")
    quantity = data.get("quantity", 1)

    try:
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute(
            "SELECT * FROM cart WHERE user_id=%s AND item_id=%s",
            (user_id, item_id)
        )
        existing = cursor.fetchone()

        if existing:
            cursor.execute(
                "UPDATE cart SET quantity = quantity + %s WHERE user_id=%s AND item_id=%s",
                (quantity, user_id, item_id)
            )
        else:
            cursor.execute(
                "INSERT INTO cart (user_id, item_id, quantity) VALUES (%s, %s, %s)",
                (user_id, item_id, quantity)
            )

        db.commit()
        return jsonify({"success": True, "message": "Đã thêm vào giỏ hàng!"})
    except mysql.connector.Error as e:
        return jsonify({"success": False, "message": f"Lỗi: {str(e)}"})
    finally:
        cursor.close()
        db.close()


@app.route("/api/cart/<int:user_id>", methods=["GET"])
def get_cart(user_id):
    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT c.id, c.quantity, m.name, m.price, m.image 
            FROM cart c 
            JOIN menu_items m ON c.item_id = m.id 
            WHERE c.user_id = %s
        """, (user_id,))
        cart_items = cursor.fetchall()
        return jsonify({"success": True, "items": cart_items})
    except mysql.connector.Error as e:
        return jsonify({"success": False, "message": f"Lỗi: {str(e)}"})
    finally:
        cursor.close()
        db.close()


@app.route("/api/cart/update", methods=["PUT"])
def update_cart():
    data = request.json
    cart_id = data.get("cart_id")
    quantity = data.get("quantity")

    try:
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute(
            "UPDATE cart SET quantity = %s WHERE id = %s",
            (quantity, cart_id)
        )
        db.commit()
        return jsonify({"success": True, "message": "Đã cập nhật số lượng!"})
    except mysql.connector.Error as e:
        return jsonify({"success": False, "message": f"Lỗi: {str(e)}"})
    finally:
        cursor.close()
        db.close()


@app.route("/api/cart/<int:cart_id>", methods=["DELETE"])
def remove_from_cart(cart_id):
    try:
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("DELETE FROM cart WHERE id = %s", (cart_id,))
        db.commit()
        return jsonify({"success": True, "message": "Đã xóa khỏi giỏ hàng!"})
    except mysql.connector.Error as e:
        return jsonify({"success": False, "message": f"Lỗi: {str(e)}"})
    finally:
        cursor.close()
        db.close()


# -------------------------
# Orders
# -------------------------
@app.route("/api/order", methods=["POST"])
def create_order():
    data = request.json
    user_id = data.get("user_id")
    total_amount = data.get("total_amount")

    try:
        db = get_db_connection()
        cursor = db.cursor()
        # Create order
        cursor.execute(
            "INSERT INTO orders (user_id, total_amount, status) VALUES (%s, %s, 'pending')",
            (user_id, total_amount)
        )
        order_id = cursor.lastrowid

        # Move cart items to order_items
        cursor.execute("""
            INSERT INTO order_items (order_id, item_id, quantity, price)
            SELECT %s, c.item_id, c.quantity, m.price
            FROM cart c
            JOIN menu_items m ON c.item_id = m.id
            WHERE c.user_id = %s
        """, (order_id, user_id))

        # Clear cart
        cursor.execute("DELETE FROM cart WHERE user_id = %s", (user_id,))

        db.commit()
        return jsonify({"success": True, "message": "Đặt hàng thành công!", "order_id": order_id})
    except mysql.connector.Error as e:
        return jsonify({"success": False, "message": f"Lỗi: {str(e)}"})
    finally:
        cursor.close()
        db.close()


# -------------------------
# Run app
# -------------------------
if __name__ == "__main__":
    app.run(debug=True, port=5000)
