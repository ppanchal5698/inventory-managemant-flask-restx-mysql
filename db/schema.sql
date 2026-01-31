-- Inventory Management System Database Schema
-- MySQL/MariaDB Compatible
-- Optimized for performance and data integrity

-- Create Database
-- CREATE DATABASE IF NOT EXISTS InventoryManagementSystem CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
-- USE InventoryManagementSystem;

-- Enable strict mode for better data integrity
-- SET SQL_MODE = 'STRICT_TRANS_TABLES,NO_ZERO_DATE,NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    role ENUM('admin', 'manager', 'staff', 'viewer') NOT NULL DEFAULT 'staff',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_username (username),
    UNIQUE KEY uk_email (email),
    INDEX idx_role_active (role, is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;

-- Categories Table
CREATE TABLE IF NOT EXISTS categories (
    category_id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL,
    parent_category_id BIGINT UNSIGNED NULL,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY fk_parent_category (parent_category_id) REFERENCES categories(category_id) ON DELETE SET NULL ON UPDATE CASCADE,
    INDEX idx_category_name (category_name),
    INDEX idx_parent_active (parent_category_id, is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;

-- Suppliers Table
CREATE TABLE IF NOT EXISTS suppliers (
    supplier_id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    supplier_name VARCHAR(150) NOT NULL,
    contact_person VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(20),
    address TEXT,
    city VARCHAR(50),
    state VARCHAR(50),
    country VARCHAR(50) DEFAULT 'USA',
    postal_code VARCHAR(20),
    tax_id VARCHAR(50),
    payment_terms VARCHAR(100),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_supplier_name (supplier_name),
    INDEX idx_email (email),
    INDEX idx_active (is_active),
    INDEX idx_location (country, state, city)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;

-- Brands Table
CREATE TABLE IF NOT EXISTS brands (
    brand_id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    brand_name VARCHAR(100) NOT NULL,
    manufacturer_name VARCHAR(150),
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_brand_name (brand_name),
    INDEX idx_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;

-- Products Table
CREATE TABLE IF NOT EXISTS products (
    product_id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    product_code VARCHAR(50) NOT NULL,
    product_name VARCHAR(200) NOT NULL,
    description TEXT,
    category_id BIGINT UNSIGNED,
    brand_id BIGINT UNSIGNED,
    unit_price DECIMAL(12, 2) NOT NULL CHECK (unit_price >= 0),
    cost_price DECIMAL(12, 2) CHECK (cost_price >= 0),
    reorder_level INT UNSIGNED NOT NULL DEFAULT 10,
    min_stock_level INT UNSIGNED NOT NULL DEFAULT 5,
    max_stock_level INT UNSIGNED,
    unit_of_measure VARCHAR(20) NOT NULL DEFAULT 'pcs',
    barcode VARCHAR(100),
    sku VARCHAR(100),
    weight DECIMAL(10, 3),
    dimensions VARCHAR(50),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_product_code (product_code),
    UNIQUE KEY uk_barcode (barcode),
    UNIQUE KEY uk_sku (sku),
    FOREIGN KEY fk_product_category (category_id) REFERENCES categories(category_id) ON DELETE SET NULL ON UPDATE CASCADE,
    FOREIGN KEY fk_product_brand (brand_id) REFERENCES brands(brand_id) ON DELETE SET NULL ON UPDATE CASCADE,
    INDEX idx_product_name (product_name),
    INDEX idx_category_brand (category_id, brand_id),
    INDEX idx_active_category (is_active, category_id),
    INDEX idx_price_range (unit_price)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;

-- Warehouses Table
CREATE TABLE IF NOT EXISTS warehouses (
    warehouse_id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    warehouse_name VARCHAR(100) NOT NULL,
    location VARCHAR(200),
    address TEXT,
    city VARCHAR(50),
    state VARCHAR(50),
    country VARCHAR(50) DEFAULT 'USA',
    postal_code VARCHAR(20),
    manager_name VARCHAR(100),
    phone VARCHAR(20),
    capacity INT UNSIGNED,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_warehouse_name (warehouse_name),
    INDEX idx_active (is_active),
    INDEX idx_location (country, state, city)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;

-- Stock/Inventory Table
CREATE TABLE IF NOT EXISTS stock (
    stock_id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    product_id BIGINT UNSIGNED NOT NULL,
    warehouse_id BIGINT UNSIGNED NOT NULL,
    quantity_on_hand INT NOT NULL DEFAULT 0 CHECK (quantity_on_hand >= 0),
    quantity_reserved INT NOT NULL DEFAULT 0 CHECK (quantity_reserved >= 0),
    quantity_available INT GENERATED ALWAYS AS (quantity_on_hand - quantity_reserved) STORED,
    last_stock_check TIMESTAMP NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_product_warehouse (product_id, warehouse_id),
    FOREIGN KEY fk_stock_product (product_id) REFERENCES products(product_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY fk_stock_warehouse (warehouse_id) REFERENCES warehouses(warehouse_id) ON DELETE CASCADE ON UPDATE CASCADE,
    INDEX idx_warehouse_quantity (warehouse_id, quantity_on_hand),
    INDEX idx_low_stock (product_id, quantity_on_hand)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;

-- Customers Table
CREATE TABLE IF NOT EXISTS customers (
    customer_id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    customer_name VARCHAR(150) NOT NULL,
    contact_person VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(20),
    address TEXT,
    city VARCHAR(50),
    state VARCHAR(50),
    country VARCHAR(50) DEFAULT 'USA',
    postal_code VARCHAR(20),
    tax_id VARCHAR(50),
    credit_limit DECIMAL(12, 2) CHECK (credit_limit >= 0),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_customer_name (customer_name),
    INDEX idx_email (email),
    INDEX idx_active (is_active),
    INDEX idx_location (country, state, city)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;

-- Purchase Orders Table
CREATE TABLE IF NOT EXISTS purchase_orders (
    po_id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    po_number VARCHAR(50) NOT NULL,
    supplier_id BIGINT UNSIGNED NOT NULL,
    warehouse_id BIGINT UNSIGNED NOT NULL,
    order_date DATE NOT NULL,
    expected_delivery_date DATE,
    actual_delivery_date DATE,
    status ENUM('draft', 'pending', 'approved', 'received', 'cancelled') NOT NULL DEFAULT 'draft',
    total_amount DECIMAL(12, 2) CHECK (total_amount >= 0),
    tax_amount DECIMAL(10, 2) DEFAULT 0 CHECK (tax_amount >= 0),
    shipping_cost DECIMAL(10, 2) DEFAULT 0 CHECK (shipping_cost >= 0),
    notes TEXT,
    created_by BIGINT UNSIGNED,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_po_number (po_number),
    FOREIGN KEY fk_po_supplier (supplier_id) REFERENCES suppliers(supplier_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY fk_po_warehouse (warehouse_id) REFERENCES warehouses(warehouse_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY fk_po_user (created_by) REFERENCES users(user_id) ON DELETE SET NULL ON UPDATE CASCADE,
    INDEX idx_supplier_status (supplier_id, status),
    INDEX idx_order_date (order_date),
    INDEX idx_status_date (status, order_date),
    INDEX idx_warehouse (warehouse_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;

-- Purchase Order Items Table
CREATE TABLE IF NOT EXISTS purchase_order_items (
    po_item_id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    po_id BIGINT UNSIGNED NOT NULL,
    product_id BIGINT UNSIGNED NOT NULL,
    quantity INT UNSIGNED NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(12, 2) NOT NULL CHECK (unit_price >= 0),
    received_quantity INT UNSIGNED NOT NULL DEFAULT 0,
    line_total DECIMAL(12, 2) GENERATED ALWAYS AS (quantity * unit_price) STORED,
    FOREIGN KEY fk_poi_po (po_id) REFERENCES purchase_orders(po_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY fk_poi_product (product_id) REFERENCES products(product_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    INDEX idx_po_product (po_id, product_id),
    INDEX idx_product (product_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;

-- Sales Orders Table
CREATE TABLE IF NOT EXISTS sales_orders (
    order_id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    order_number VARCHAR(50) NOT NULL,
    customer_id BIGINT UNSIGNED NOT NULL,
    warehouse_id BIGINT UNSIGNED NOT NULL,
    order_date DATE NOT NULL,
    expected_delivery_date DATE,
    actual_delivery_date DATE,
    status ENUM('pending', 'processing', 'shipped', 'delivered', 'cancelled') NOT NULL DEFAULT 'pending',
    total_amount DECIMAL(12, 2) CHECK (total_amount >= 0),
    tax_amount DECIMAL(10, 2) DEFAULT 0 CHECK (tax_amount >= 0),
    shipping_cost DECIMAL(10, 2) DEFAULT 0 CHECK (shipping_cost >= 0),
    discount_amount DECIMAL(10, 2) NOT NULL DEFAULT 0 CHECK (discount_amount >= 0),
    payment_status ENUM('unpaid', 'partial', 'paid') NOT NULL DEFAULT 'unpaid',
    notes TEXT,
    created_by BIGINT UNSIGNED,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_order_number (order_number),
    FOREIGN KEY fk_so_customer (customer_id) REFERENCES customers(customer_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY fk_so_warehouse (warehouse_id) REFERENCES warehouses(warehouse_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY fk_so_user (created_by) REFERENCES users(user_id) ON DELETE SET NULL ON UPDATE CASCADE,
    INDEX idx_customer_status (customer_id, status),
    INDEX idx_order_date (order_date),
    INDEX idx_status_payment (status, payment_status),
    INDEX idx_warehouse (warehouse_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;

-- Sales Order Items Table
CREATE TABLE IF NOT EXISTS sales_order_items (
    order_item_id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    order_id BIGINT UNSIGNED NOT NULL,
    product_id BIGINT UNSIGNED NOT NULL,
    quantity INT UNSIGNED NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(12, 2) NOT NULL CHECK (unit_price >= 0),
    discount DECIMAL(10, 2) NOT NULL DEFAULT 0 CHECK (discount >= 0),
    line_total DECIMAL(12, 2) GENERATED ALWAYS AS ((quantity * unit_price) - discount) STORED,
    FOREIGN KEY fk_soi_order (order_id) REFERENCES sales_orders(order_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY fk_soi_product (product_id) REFERENCES products(product_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    INDEX idx_order_product (order_id, product_id),
    INDEX idx_product (product_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;

-- Inventory Transactions Table
CREATE TABLE IF NOT EXISTS inventory_transactions (
    transaction_id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    transaction_type ENUM('purchase', 'sale', 'adjustment', 'transfer', 'return', 'damage') NOT NULL,
    product_id BIGINT UNSIGNED NOT NULL,
    warehouse_id BIGINT UNSIGNED NOT NULL,
    quantity INT NOT NULL,
    reference_type VARCHAR(50),
    reference_id BIGINT UNSIGNED,
    transaction_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    performed_by BIGINT UNSIGNED,
    FOREIGN KEY fk_trans_product (product_id) REFERENCES products(product_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY fk_trans_warehouse (warehouse_id) REFERENCES warehouses(warehouse_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY fk_trans_user (performed_by) REFERENCES users(user_id) ON DELETE SET NULL ON UPDATE CASCADE,
    INDEX idx_product_date (product_id, transaction_date),
    INDEX idx_warehouse_date (warehouse_id, transaction_date),
    INDEX idx_type_date (transaction_type, transaction_date),
    INDEX idx_reference (reference_type, reference_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;

-- Stock Adjustments Table
CREATE TABLE IF NOT EXISTS stock_adjustments (
    adjustment_id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    product_id BIGINT UNSIGNED NOT NULL,
    warehouse_id BIGINT UNSIGNED NOT NULL,
    old_quantity INT NOT NULL CHECK (old_quantity >= 0),
    new_quantity INT NOT NULL CHECK (new_quantity >= 0),
    quantity_difference INT GENERATED ALWAYS AS (new_quantity - old_quantity) STORED,
    reason ENUM('physical_count', 'damage', 'theft', 'expired', 'correction', 'other') NOT NULL,
    notes TEXT,
    adjusted_by BIGINT UNSIGNED,
    adjustment_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY fk_adj_product (product_id) REFERENCES products(product_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY fk_adj_warehouse (warehouse_id) REFERENCES warehouses(warehouse_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY fk_adj_user (adjusted_by) REFERENCES users(user_id) ON DELETE SET NULL ON UPDATE CASCADE,
    INDEX idx_product_warehouse (product_id, warehouse_id),
    INDEX idx_date (adjustment_date),
    INDEX idx_reason_date (reason, adjustment_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;

-- =====================================================================
-- OPTIMIZED VIEWS FOR COMMON QUERIES
-- =====================================================================

-- View: Product inventory summary across all warehouses
CREATE OR REPLACE VIEW v_product_inventory_summary AS
SELECT
    p.product_id,
    p.product_code,
    p.product_name,
    c.category_name,
    b.brand_name,
    p.unit_price,
    p.cost_price,
    p.reorder_level,
    p.min_stock_level,
    COALESCE(SUM(s.quantity_on_hand), 0) AS total_quantity_on_hand,
    COALESCE(SUM(s.quantity_reserved), 0) AS total_quantity_reserved,
    COALESCE(SUM(s.quantity_available), 0) AS total_quantity_available,
    COALESCE(SUM(s.quantity_on_hand * p.cost_price), 0) AS total_inventory_value,
    CASE
        WHEN COALESCE(SUM(s.quantity_available), 0) <= p.min_stock_level THEN 'Critical'
        WHEN COALESCE(SUM(s.quantity_available), 0) <= p.reorder_level THEN 'Low'
        ELSE 'Adequate'
    END AS stock_status,
    p.is_active
FROM products p
LEFT JOIN categories c ON p.category_id = c.category_id
LEFT JOIN brands b ON p.brand_id = b.brand_id
LEFT JOIN stock s ON p.product_id = s.product_id
GROUP BY p.product_id, p.product_code, p.product_name, c.category_name,
         b.brand_name, p.unit_price, p.cost_price, p.reorder_level,
         p.min_stock_level, p.is_active;

-- View: Warehouse stock levels
CREATE OR REPLACE VIEW v_warehouse_stock_levels AS
SELECT
    w.warehouse_id,
    w.warehouse_name,
    w.city,
    w.state,
    p.product_id,
    p.product_code,
    p.product_name,
    s.quantity_on_hand,
    s.quantity_reserved,
    s.quantity_available,
    p.reorder_level,
    p.unit_price,
    p.cost_price,
    (s.quantity_on_hand * p.cost_price) AS stock_value,
    s.last_stock_check,
    s.updated_at AS last_updated
FROM stock s
INNER JOIN warehouses w ON s.warehouse_id = w.warehouse_id
INNER JOIN products p ON s.product_id = p.product_id
WHERE w.is_active = TRUE AND p.is_active = TRUE;

-- View: Low stock alerts
CREATE OR REPLACE VIEW v_low_stock_alerts AS
SELECT
    p.product_id,
    p.product_code,
    p.product_name,
    w.warehouse_id,
    w.warehouse_name,
    s.quantity_on_hand,
    s.quantity_reserved,
    s.quantity_available,
    p.reorder_level,
    p.min_stock_level,
    CASE
        WHEN s.quantity_available <= p.min_stock_level THEN 'Critical'
        WHEN s.quantity_available <= p.reorder_level THEN 'Low'
    END AS alert_level
FROM stock s
INNER JOIN products p ON s.product_id = p.product_id
INNER JOIN warehouses w ON s.warehouse_id = w.warehouse_id
WHERE p.is_active = TRUE
  AND w.is_active = TRUE
  AND s.quantity_available <= p.reorder_level;

-- View: Purchase order summary with line items
CREATE OR REPLACE VIEW v_purchase_order_details AS
SELECT
    po.po_id,
    po.po_number,
    s.supplier_name,
    w.warehouse_name,
    po.order_date,
    po.expected_delivery_date,
    po.actual_delivery_date,
    po.status,
    poi.product_id,
    p.product_code,
    p.product_name,
    poi.quantity,
    poi.unit_price,
    poi.received_quantity,
    poi.line_total,
    (poi.quantity - poi.received_quantity) AS pending_quantity,
    po.total_amount,
    po.tax_amount,
    po.shipping_cost,
    u.username AS created_by_user
FROM purchase_orders po
INNER JOIN suppliers s ON po.supplier_id = s.supplier_id
INNER JOIN warehouses w ON po.warehouse_id = w.warehouse_id
LEFT JOIN purchase_order_items poi ON po.po_id = poi.po_id
LEFT JOIN products p ON poi.product_id = p.product_id
LEFT JOIN users u ON po.created_by = u.user_id;

-- View: Sales order summary with line items
CREATE OR REPLACE VIEW v_sales_order_details AS
SELECT
    so.order_id,
    so.order_number,
    c.customer_name,
    w.warehouse_name,
    so.order_date,
    so.expected_delivery_date,
    so.actual_delivery_date,
    so.status,
    so.payment_status,
    soi.product_id,
    p.product_code,
    p.product_name,
    soi.quantity,
    soi.unit_price,
    soi.discount,
    soi.line_total,
    so.total_amount,
    so.tax_amount,
    so.shipping_cost,
    so.discount_amount,
    u.username AS created_by_user
FROM sales_orders so
INNER JOIN customers c ON so.customer_id = c.customer_id
INNER JOIN warehouses w ON so.warehouse_id = w.warehouse_id
LEFT JOIN sales_order_items soi ON so.order_id = soi.order_id
LEFT JOIN products p ON soi.product_id = p.product_id
LEFT JOIN users u ON so.created_by = u.user_id;

-- View: Product transaction history
CREATE OR REPLACE VIEW v_product_transaction_history AS
SELECT
    it.transaction_id,
    it.transaction_type,
    it.transaction_date,
    p.product_id,
    p.product_code,
    p.product_name,
    w.warehouse_name,
    it.quantity,
    it.reference_type,
    it.reference_id,
    u.username AS performed_by_user,
    it.notes
FROM inventory_transactions it
INNER JOIN products p ON it.product_id = p.product_id
INNER JOIN warehouses w ON it.warehouse_id = w.warehouse_id
LEFT JOIN users u ON it.performed_by = u.user_id
ORDER BY it.transaction_date DESC;

-- View: Financial summary - Inventory valuation
CREATE OR REPLACE VIEW v_inventory_valuation AS
SELECT
    w.warehouse_id,
    w.warehouse_name,
    COUNT(DISTINCT s.product_id) AS total_products,
    SUM(s.quantity_on_hand) AS total_units,
    SUM(s.quantity_on_hand * p.cost_price) AS total_cost_value,
    SUM(s.quantity_on_hand * p.unit_price) AS total_retail_value,
    SUM(s.quantity_on_hand * (p.unit_price - p.cost_price)) AS potential_profit
FROM stock s
INNER JOIN products p ON s.product_id = p.product_id
INNER JOIN warehouses w ON s.warehouse_id = w.warehouse_id
WHERE p.is_active = TRUE AND w.is_active = TRUE
GROUP BY w.warehouse_id, w.warehouse_name;

-- View: Pending purchase orders summary
CREATE OR REPLACE VIEW v_pending_purchase_orders AS
SELECT
    po.po_id,
    po.po_number,
    s.supplier_name,
    po.order_date,
    po.expected_delivery_date,
    po.status,
    po.total_amount,
    COUNT(poi.po_item_id) AS total_items,
    SUM(poi.quantity) AS total_quantity,
    SUM(poi.received_quantity) AS total_received,
    SUM(poi.quantity - poi.received_quantity) AS total_pending
FROM purchase_orders po
INNER JOIN suppliers s ON po.supplier_id = s.supplier_id
LEFT JOIN purchase_order_items poi ON po.po_id = poi.po_id
WHERE po.status IN ('pending', 'approved')
GROUP BY po.po_id, po.po_number, s.supplier_name, po.order_date,
         po.expected_delivery_date, po.status, po.total_amount;

-- View: Active sales orders summary
CREATE OR REPLACE VIEW v_active_sales_orders AS
SELECT
    so.order_id,
    so.order_number,
    c.customer_name,
    so.order_date,
    so.expected_delivery_date,
    so.status,
    so.payment_status,
    so.total_amount,
    COUNT(soi.order_item_id) AS total_items,
    SUM(soi.quantity) AS total_quantity
FROM sales_orders so
INNER JOIN customers c ON so.customer_id = c.customer_id
LEFT JOIN sales_order_items soi ON so.order_id = soi.order_id
WHERE so.status IN ('pending', 'processing', 'shipped')
GROUP BY so.order_id, so.order_number, c.customer_name, so.order_date,
         so.expected_delivery_date, so.status, so.payment_status, so.total_amount;
