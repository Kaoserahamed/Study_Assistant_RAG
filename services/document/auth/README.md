# Study_Assistant_RAG Authentication Module

## Overview
Authentication system for student/educator/admin roles with OAuth2, JWT, and MFA.

## Files
- `services/document/auth.py` - Authentication logic
- `services/document/models.py` - User and role models
- `services/document/middleware.py` - Auth middleware and RBAC
- `services/document/routes/auth.py` - Auth API routes
- `services/document/mfa.py` - Multi-factor authentication

## Features
- Student, educator, and admin account registration/login
- JWT-based session management
- OAuth2 provider integration
- Role-Based Access Control (RBAC)
- Multi-factor authentication (MFA)
- Password hashing with bcrypt
- Session timeout handling

## Tech Stack
- Python/FastAPI
- MySQL
- JWT (PyJWT)
- OAuth2
- bcrypt for password hashing

## Day 5 Outcome
Authentication module implemented. 1 PR created targeting development.