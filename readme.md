##Health Record API
A secure Django REST API for managing personal health records with role-based access for patients and doctors.
Features

User Authentication: Token-based authentication with 5-minute token expiry
Role-based Access: Separate functionality for patients and doctors
Health Records: Patients can create, update, and manage their health records
Doctor Annotations: Doctors can view and annotate assigned patient records
Assignment System: Doctors can be assigned to patients with automatic notifications
Secure Access Control: Strict permissions to protect sensitive health data

Tech Stack

Backend: Django 5.1, Django REST Framework
Database: PostgreSQL (Supabase for production)
Authentication: Token-based with custom expiry middleware
Deployment: Render (production)

Quick Start
Prerequisites

Python 3.8+
PostgreSQL
Git
