CREATE DATABASE inventory;
USE inventory;


CREATE TABLE Product (
    product_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    sku VARCHAR(50) UNIQUE,
    category VARCHAR(50),
    supplier VARCHAR(100),
    available INT NOT NULL CHECK (available >= 0),
    quantity INT CHECK (quantity > 0),
    price DECIMAL(10,2) CHECK (price > 0),
    added_date DATE NOT NULL,
    added_time TIME NOT NULL
) AUTO_INCREMENT = 101;


CREATE TABLE Location (
    location_id VARCHAR(50) PRIMARY KEY,
    city VARCHAR(100),
    capacity INT
);


CREATE TABLE ProductMovement (
    movement_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    from_location VARCHAR(50),
    to_location VARCHAR(50),
    date_moved DATE NOT NULL,
    time_moved TIME NOT NULL,
    qty INT NOT NULL CHECK (qty > 0),
    was_damaged TINYINT(1) DEFAULT 0,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES Product(product_id),
    FOREIGN KEY (from_location) REFERENCES Location(location_id),
    FOREIGN KEY (to_location) REFERENCES Location(location_id)
) AUTO_INCREMENT = 301;


SHOW TABLES;
DESC Product;
DESC Location;
DESC ProductMovement;