-- ============================================================
-- Student Assistant Database Schema
-- ============================================================
-- This file creates the complete database schema for the
-- Student Assistant RAG application
-- Matches the SQLAlchemy models in app/models/
-- ============================================================

-- Drop database if exists (BE CAREFUL - THIS DELETES ALL DATA!)
DROP DATABASE IF EXISTS `study_assistant`;

-- Create database with UTF8MB4 support
CREATE DATABASE `study_assistant` 
    CHARACTER SET utf8mb4 
    COLLATE utf8mb4_unicode_ci;

-- Use the database
USE `study_assistant`;

-- ============================================================
-- Table: users
-- Model: app/models/user.py - User
-- Stores user accounts for authentication
-- ============================================================
CREATE TABLE `users` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(255) NOT NULL,
    `email` VARCHAR(255) UNIQUE NOT NULL,
    `password_hash` VARCHAR(512) NOT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX `idx_id` (`id`),
    INDEX `idx_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- Table: documents
-- Model: app/models/document.py - Document
-- Stores uploaded PDF documents metadata
-- ============================================================
CREATE TABLE `documents` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `filename` VARCHAR(255) NOT NULL,
    `title` VARCHAR(255) DEFAULT NULL,
    `file_path` VARCHAR(500) NOT NULL,
    `page_count` INT DEFAULT 0,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    INDEX `idx_id` (`id`),
    INDEX `idx_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- Table: document_chunks
-- Model: app/models/chunk.py - DocumentChunk
-- Stores text chunks extracted from documents
-- Each chunk gets embedded and stored in Pinecone
-- ============================================================
CREATE TABLE `document_chunks` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `document_id` INT NOT NULL,
    `content` TEXT NOT NULL,
    `page_number` INT NOT NULL,
    `chunk_index` INT NOT NULL,
    FOREIGN KEY (`document_id`) REFERENCES `documents`(`id`) ON DELETE CASCADE,
    INDEX `idx_id` (`id`),
    INDEX `idx_document_id` (`document_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- Table: conversations
-- Model: app/models/conversation.py - Conversation
-- Stores chat conversation threads
-- ============================================================
CREATE TABLE `conversations` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `title` VARCHAR(255) DEFAULT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    INDEX `idx_id` (`id`),
    INDEX `idx_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- Table: messages
-- Model: app/models/message.py - Message
-- Stores individual messages within conversations
-- RoleEnum: user, assistant, system
-- ============================================================
CREATE TABLE `messages` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `conversation_id` INT NOT NULL,
    `role` ENUM('user', 'assistant', 'system') NOT NULL,
    `content` TEXT NOT NULL,
    `citations` JSON DEFAULT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`conversation_id`) REFERENCES `conversations`(`id`) ON DELETE CASCADE,
    INDEX `idx_id` (`id`),
    INDEX `idx_conversation_id` (`conversation_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- Optional: Create a demo user for testing
-- Username: demo
-- Email: demo@example.com
-- Password: demo123
-- (Password hash is for 'demo123' using bcrypt)
-- ============================================================
-- Uncomment the following lines to create a demo user:
-- INSERT INTO `users` (`name`, `email`, `password_hash`) 
-- VALUES (
--     'Demo User',
--     'demo@example.com',
--     '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NU7EhzHhTXSG'
-- );

-- ============================================================
-- Display table information
-- ============================================================
SELECT 'Database created successfully!' AS status;
SHOW TABLES;

-- Display table structures
SELECT 'Table: users' AS '';
DESCRIBE `users`;

SELECT 'Table: documents' AS '';
DESCRIBE `documents`;

SELECT 'Table: document_chunks' AS '';
DESCRIBE `document_chunks`;

SELECT 'Table: conversations' AS '';
DESCRIBE `conversations`;

SELECT 'Table: messages' AS '';
DESCRIBE `messages`;
