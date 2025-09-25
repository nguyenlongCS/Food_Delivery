from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import mysql.connector
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

    try:
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO user (username, email, password, role) VALUES (%s, %s, %s, %s)",
            (username, email, password, "user")
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

        if user and user["password"] == password:
            return jsonify({
                "success": True,
                "user": {
                    "id": user["id"],
                    "username": user["username"],
                    "email": user["email"],
                    "role": user["role"]
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

        # Fix image paths
        for item in items:
            if item.get('image'):
                if not item['image'].startswith('uploads/'):
                    item['image'] = f"uploads/{item['image']}"

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

        # Fix image paths
        for item in cart_items:
            if item.get('image'):
                if not item['image'].startswith('uploads/'):
                    item['image'] = f"uploads/{item['image']}"

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

    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        # Lấy giỏ hàng theo user
        cursor.execute("""
            SELECT c.item_id, c.quantity, m.price, m.restaurant
            FROM cart c
            JOIN menu_items m ON c.item_id = m.id
            WHERE c.user_id = %s
        """, (user_id,))
        cart_items = cursor.fetchall()

        if not cart_items:
            return jsonify({"success": False, "message": "Giỏ hàng trống!"})

        # Nhóm theo restaurant
        restaurant_groups = {}
        for item in cart_items:
            restaurant = item["restaurant"]
            if restaurant not in restaurant_groups:
                restaurant_groups[restaurant] = []
            restaurant_groups[restaurant].append(item)

        created_orders = []

        # Tạo 1 đơn cho mỗi nhà hàng
        for restaurant, items in restaurant_groups.items():
            total_amount = sum(i["price"] * i["quantity"] for i in items) + 30000  # Cộng phí ship
            cursor.execute(
                "INSERT INTO orders (user_id, restaurant, total_amount, status) VALUES (%s, %s, %s, 'pending')",
                (user_id, restaurant, total_amount)
            )
            order_id = cursor.lastrowid

            # Thêm các món vào order_items
            for i in items:
                cursor.execute(
                    "INSERT INTO order_items (order_id, item_id, quantity, price) VALUES (%s, %s, %s, %s)",
                    (order_id, i["item_id"], i["quantity"], i["price"])
                )

            created_orders.append(order_id)

        # Xóa giỏ hàng
        cursor.execute("DELETE FROM cart WHERE user_id = %s", (user_id,))
        db.commit()

        return jsonify({"success": True, "message": "Đặt hàng thành công!", "orders": created_orders})
    except mysql.connector.Error as e:
        return jsonify({"success": False, "message": f"Lỗi: {str(e)}"})
    finally:
        cursor.close()
        db.close()

# Lấy đơn hàng của 1 user (khách hàng)
@app.route("/api/orders/user/<int:user_id>", methods=["GET"])
def get_user_orders(user_id):
    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT o.id, o.restaurant, o.total_amount, o.status, o.created_at
            FROM orders o
            WHERE o.user_id = %s
            ORDER BY o.created_at DESC
        """, (user_id,))
        orders = cursor.fetchall()
        return jsonify({"success": True, "orders": orders})
    except mysql.connector.Error as e:
        return jsonify({"success": False, "message": f"Lỗi: {str(e)}"})
    finally:
        cursor.close()
        db.close()

# Lấy tất cả đơn hàng (cho nhà hàng) - ĐÃ SỬA LỖI
@app.route("/api/orders/restaurant/<restaurant_name>", methods=["GET"])
def get_restaurant_orders(restaurant_name):
    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT o.id, u.username, o.total_amount, o.status, o.created_at
            FROM orders o
            JOIN user u ON o.user_id = u.id
            WHERE o.restaurant = %s
            ORDER BY o.created_at DESC
        """, (restaurant_name,))
        orders = cursor.fetchall()
        return jsonify({"success": True, "orders": orders})
    except mysql.connector.Error as e:
        return jsonify({"success": False, "message": f"Lỗi: {str(e)}"})
    finally:
        cursor.close()
        db.close()

# Nhà hàng xác nhận/hủy đơn
@app.route("/api/orders/<int:order_id>/status", methods=["PUT"])
def update_order_status(order_id):
    data = request.json
    status = data.get("status")  # 'confirmed' hoặc 'cancelled'

    try:
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("UPDATE orders SET status=%s WHERE id=%s", (status, order_id))
        db.commit()
        return jsonify({"success": True, "message": "Cập nhật trạng thái thành công!"})
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