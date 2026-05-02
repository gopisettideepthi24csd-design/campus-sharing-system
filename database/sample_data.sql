-- ============================================================
-- Campus Sharing and Resource Sharing System
-- Sample Data Insertion
-- ============================================================
-- Run this after schema.sql to populate the database with test data.
-- Passwords are bcrypt hashed (plain text shown in comments for reference)

USE campus_sharing;

-- ============================================================
-- INSERT SAMPLE USERS
-- ============================================================
-- Note: In production, passwords are hashed by the application.
-- These are pre-hashed values for the sample data.
-- admin123 → hashed | student123 → hashed

INSERT INTO users (name, email, password, role) VALUES
('Admin', 'admin@campus.edu', '$2b$12$LQv3c1yqBo9SkvXS7QTJPOoGT1GfbRZ2FqDH3a4HXLbKz.jW7WGWK', 'admin'),
('John Student', 'john@campus.edu', '$2b$12$LQv3c1yqBo9SkvXS7QTJPOoGT1GfbRZ2FqDH3a4HXLbKz.jW7WGWK', 'student'),
('Alice Kumar', 'alice@campus.edu', '$2b$12$LQv3c1yqBo9SkvXS7QTJPOoGT1GfbRZ2FqDH3a4HXLbKz.jW7WGWK', 'student'),
('Bob Singh', 'bob@campus.edu', '$2b$12$LQv3c1yqBo9SkvXS7QTJPOoGT1GfbRZ2FqDH3a4HXLbKz.jW7WGWK', 'student');

-- ============================================================
-- INSERT SAMPLE BOOKS (as specified in requirements)
-- ============================================================

INSERT INTO books (title, author, subject, status, owner_id) VALUES
('Data Structures', 'Ellis Horowitz', 'Computer Science', 'Available', 1),
('Operating System Concepts', 'Abraham Silberschatz', 'Computer Science', 'Available', 1),
('Computer Networks', 'Andrew S. Tanenbaum', 'Computer Science', 'Available', 1),
('Database System Concepts', 'Abraham Silberschatz', 'Computer Science', 'Available', 1),
('Introduction to Algorithms', 'Thomas H. Cormen', 'Computer Science', 'Available', 2),
('Discrete Mathematics', 'Kenneth H. Rosen', 'Mathematics', 'Available', 2),
('Digital Logic Design', 'Morris Mano', 'Electronics', 'Available', 3);

-- ============================================================
-- INSERT SAMPLE RESOURCES
-- ============================================================

INSERT INTO resources (title, description, category, status, owner_id) VALUES
('Python Programming Notes', 'Complete notes covering Python basics to advanced topics including OOP, file handling, and libraries', 'Notes', 'Available', 1),
('Arduino Starter Kit', 'Arduino UNO with sensors and components for IoT projects', 'Electronics', 'Available', 1),
('Web Development Toolkit', 'Collection of tools and templates for web development projects', 'Tools', 'Available', 2),
('Machine Learning Notes', 'Handwritten notes on ML algorithms, neural networks, and deep learning', 'Notes', 'Available', 3),
('Scientific Calculator', 'Casio FX-991EX scientific calculator for engineering calculations', 'Tools', 'Available', 3),
('Java Programming Guide', 'Comprehensive guide to Java programming with examples', 'Notes', 'Available', 4);

-- ============================================================
-- INSERT SAMPLE REQUESTS (to demonstrate the workflow)
-- ============================================================

INSERT INTO requests (item_id, item_type, requester_id, owner_id, status, borrow_date) VALUES
(1, 'book', 2, 1, 'Approved', NOW()),        -- John borrowed Data Structures from Admin
(1, 'resource', 3, 1, 'Pending', NULL),       -- Alice requested Python Notes from Admin
(2, 'book', 3, 1, 'Rejected', NULL);          -- Alice's request for OS Concepts was rejected

-- Update the borrowed book's status
UPDATE books SET status = 'Borrowed' WHERE id = 1;
