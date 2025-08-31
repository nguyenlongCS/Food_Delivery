CREATE DATABASE FoodDelivery;

USE FoodDelivery;

CREATE TABLE user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) UNIQUE,
    password VARCHAR(255) NOT NULL,
    role ENUM('user', 'admin', 'lessor') DEFAULT 'user'
);

select*from user;

UPDATE user 
SET role = 'admin' 
WHERE username = 'admin123';

DELETE FROM user 
WHERE username = 'long123';

DROP TABLE user;