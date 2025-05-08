
DROP DATABASE IF EXISTS inventory;


CREATE DATABASE inventory;
USE inventory;


CREATE TABLE Product (
    product_id VARCHAR(10) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    sku VARCHAR(50) NOT NULL UNIQUE,
    category VARCHAR(50),
    supplier VARCHAR(100),
    price DECIMAL(10, 2) NOT NULL
);


CREATE TABLE Location (
    location_id VARCHAR(10) PRIMARY KEY,
    city VARCHAR(100)
);


CREATE TABLE ProductMovement (
    movement_id VARCHAR(10) PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    from_location VARCHAR(10),
    to_location VARCHAR(10),
    product_id VARCHAR(10) NOT NULL,
    qty INT NOT NULL,
    FOREIGN KEY (product_id) REFERENCES Product(product_id) ON DELETE CASCADE,
    FOREIGN KEY (from_location) REFERENCES Location(location_id) ON DELETE SET NULL,
    FOREIGN KEY (to_location) REFERENCES Location(location_id) ON DELETE SET NULL,
    CONSTRAINT chk_qty CHECK (qty >= 1)
);

INSERT INTO Product (product_id, name, sku, category, supplier, price) VALUES
('P1', 'Laptop', 'SKU001', 'Electronics', 'TechCorp', 999.99),
('P2', 'Smartphone', 'SKU002', 'Electronics', 'MobileInc', 699.99),
('P3', 'Desk Chair', 'SKU003', 'Furniture', 'FurniCo', 149.99),
('P4', 'Headphones', 'SKU004', 'Accessories', 'AudioTech', 89.99);


INSERT INTO Location (location_id, city) VALUES
('L1', 'New York'),
('L2', 'Los Angeles'),
('L3', 'Chicago'),
('L4', 'Houston');


INSERT INTO ProductMovement (movement_id, timestamp, from_location, to_location, product_id, qty) VALUES
('M1', CURRENT_TIMESTAMP, NULL, 'L1', 'P1', 50);


INSERT INTO ProductMovement (movement_id, timestamp, from_location, to_location, product_id, qty) VALUES
('M2', CURRENT_TIMESTAMP, NULL, 'L1', 'P2', 30);


INSERT INTO ProductMovement (movement_id, timestamp, from_location, to_location, product_id, qty) VALUES
('M3', CURRENT_TIMESTAMP, 'L1', 'L2', 'P1', 20);


INSERT INTO ProductMovement (movement_id, timestamp, from_location, to_location, product_id, qty) VALUES
('M4', CURRENT_TIMESTAMP, NULL, 'L3', 'P3', 40),
('M5', CURRENT_TIMESTAMP, NULL, 'L4', 'P4', 60),
('M6', CURRENT_TIMESTAMP, 'L2', 'L3', 'P1', 10),
('M7', CURRENT_TIMESTAMP, 'L1', 'L4', 'P2', 15),
('M8', CURRENT_TIMESTAMP, 'L3', NULL, 'P3', 5),
('M9', CURRENT_TIMESTAMP, 'L4', 'L1', 'P4', 20),
('M10', CURRENT_TIMESTAMP, NULL, 'L2', 'P1', 25),
('M11', CURRENT_TIMESTAMP, NULL, 'L3', 'P2', 10),
('M12', CURRENT_TIMESTAMP, 'L3', 'L2', 'P3', 15),
('M13', CURRENT_TIMESTAMP, 'L1', 'L3', 'P4', 10),
('M14', CURRENT_TIMESTAMP, 'L3', NULL, 'P1', 5),
('M15', CURRENT_TIMESTAMP, 'L4', 'L2', 'P2', 10),
('M16', CURRENT_TIMESTAMP, NULL, 'L1', 'P3', 20),
('M17', CURRENT_TIMESTAMP, 'L3', 'L4', 'P4', 15),
('M18', CURRENT_TIMESTAMP, 'L2', 'L4', 'P1', 10),
('M19', CURRENT_TIMESTAMP, 'L3', NULL, 'P2', 5),
('M20', CURRENT_TIMESTAMP, 'L2', 'L3', 'P3', 10);


CREATE USER IF NOT EXISTS 'flaskuser'@'localhost' IDENTIFIED BY 'mypassword123';
GRANT ALL PRIVILEGES ON inventory.* TO 'flaskuser'@'localhost';
FLUSH PRIVILEGES;