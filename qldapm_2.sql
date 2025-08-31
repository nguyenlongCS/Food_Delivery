CREATE DATABASE IF NOT EXISTS FoodDelivery;
USE FoodDelivery;

-- User table
CREATE TABLE user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Menu items table
CREATE TABLE menu_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    image VARCHAR(255),
    restaurant VARCHAR(100),
    rating DECIMAL(2,1) DEFAULT 0,
    reviews INT DEFAULT 0,
    delivery_time INT DEFAULT 30,
    distance DECIMAL(3,1) DEFAULT 0,
    category VARCHAR(50),
    badge VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Cart table
CREATE TABLE cart (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    item_id INT NOT NULL,
    quantity INT DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (item_id) REFERENCES menu_items(id) ON DELETE CASCADE
);

-- Orders table
CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
);

-- Order items table
CREATE TABLE order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    item_id INT NOT NULL,
    quantity INT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (item_id) REFERENCES menu_items(id) ON DELETE CASCADE
);

-- Insert sample menu items
INSERT INTO menu_items (name, description, price, image, restaurant, rating, reviews, delivery_time, distance, category, badge) VALUES
('Pizza Margherita Đặc Biệt', 'Pizza cổ điển với sốt cà chua tươi, phô mai mozzarella cao cấp và lá húng quế thơm.', 299000, 'uploads/food1.jpg', 'Bella Vista Italian', 4.8, 156, 25, 1.2, 'pizza', 'popular'),
('Burger Phô Mai BBQ', 'Burger bò Wagyu với phô mai cheddar, sốt BBQ đặc biệt và khoai tây chiên giòn.', 229000, 'uploads/food2.jpg', 'American Grill House', 4.6, 203, 20, 0.8, 'burger', 'new'),
('Set Sushi Premium', 'Bộ sưu tập sushi và sashimi tươi ngon từ cá hồi Na Uy và cá ngừ đại dương.', 469000, 'uploads/food3.jpg', 'Tokyo Sushi Bar', 4.9, 89, 30, 2.1, 'sushi', ''),
('Phở Bò Đặc Biệt', 'Phở bò truyền thống với nước dùng được ninh từ xương 12 tiếng, thịt bò tươi ngon.', 89000, 'uploads/food4.jpg', 'Phở Hà Nội Xưa', 4.7, 342, 15, 0.5, 'vietnamese', 'popular'),
('Gà Rán KFC Style', 'Gà rán giòn rụm với 11 loại gia vị bí mật, kèm khoai tây chiên và coleslaw.', 159000, 'uploads/food5.jpg', 'Crispy Chicken Co', 4.4, 178, 18, 1.8, 'chicken', ''),
('Bánh Mì Thịt Nướng', 'Bánh mì giòn với thịt nướng thơm lừng, pate, mayonnaise và rau sống tươi mát.', 35000, 'uploads/food6.jpg', 'Bánh Mì Sài Gòn', 4.5, 267, 10, 0.3, 'vietnamese', 'popular'),
('Pasta Carbonara Ý', 'Mì Ý carbonara với bacon giòn, phô mai Parmesan và lòng đỏ trứng gà trang trại.', 199000, 'uploads/food7.jpg', 'Roma Restaurant', 4.6, 134, 22, 1.5, 'pasta', ''),
('Tôm Tempura Nhật', 'Tôm tempura giòn với bột chiên đặc biệt, kèm sốt tentsuyu truyền thống.', 289000, 'uploads/food8.jpg', 'Sakura Japanese', 4.8, 95, 25, 2.3, 'japanese', 'new'),
('Bún Bò Huế Cay', 'Bún bò Huế cay nồng với nước dùng đậm đà, thịt bò và chả cá Huế.', 65000, 'uploads/food9.jpg', 'Cô Ba Huế', 4.7, 289, 20, 1.1, 'vietnamese', 'popular');