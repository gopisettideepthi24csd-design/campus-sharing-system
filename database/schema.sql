-- ============================================================
-- Campus Sharing and Resource Sharing System
-- Database Schema (MySQL)
-- ============================================================
-- This file contains the SQL queries to create all required tables.
-- Run this file in MySQL to set up the database manually.
-- Note: If using the application with SQLAlchemy, tables are created
-- automatically on startup.

-- Create the database
CREATE DATABASE IF NOT EXISTS campus_sharing;
USE campus_sharing;

-- ============================================================
-- TABLE: users
-- Stores all registered users (students and admins)
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,          -- Stores bcrypt hashed password
    role VARCHAR(20) DEFAULT 'student',      -- 'student' or 'admin'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_email (email),
    INDEX idx_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- TABLE: resources
-- Stores shared items (notes, tools, electronics, etc.)
-- ============================================================
CREATE TABLE IF NOT EXISTS resources (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    category VARCHAR(100) NOT NULL,          -- Notes, Tools, Electronics, etc.
    status VARCHAR(20) DEFAULT 'Available',  -- 'Available' or 'Borrowed'
    owner_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_status (status),
    INDEX idx_category (category),
    INDEX idx_owner (owner_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- TABLE: books
-- Stores books available for sharing
-- ============================================================
CREATE TABLE IF NOT EXISTS books (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    author VARCHAR(100),
    subject VARCHAR(100),
    status VARCHAR(20) DEFAULT 'Available',  -- 'Available' or 'Borrowed'
    owner_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_status (status),
    INDEX idx_subject (subject),
    INDEX idx_owner (owner_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- TABLE: requests
-- Stores borrow requests with full lifecycle tracking
-- Status flow: Pending → Approved/Rejected → Returned
-- ============================================================
CREATE TABLE IF NOT EXISTS requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    item_id INT NOT NULL,                    -- ID of the resource or book
    item_type VARCHAR(20) NOT NULL,          -- 'resource' or 'book'
    requester_id INT NOT NULL,               -- User who wants to borrow
    owner_id INT NOT NULL,                   -- Owner of the item
    status VARCHAR(20) DEFAULT 'Pending',    -- Pending/Approved/Rejected/Returned
    borrow_date DATETIME NULL,               -- Set when approved
    return_date DATETIME NULL,               -- Set when returned
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (requester_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_status (status),
    INDEX idx_requester (requester_id),
    INDEX idx_owner (owner_id),
    INDEX idx_item (item_id, item_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
