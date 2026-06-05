# MED DISPENSE

A pharmaceutical traceability and anti-counterfeit system using QR code verification.

## Features

- JWT authentication
- Medicine management
- Batch management
- QR generation
- QR registry
- QR scanner
- Fraud detection
- Scan audit trail
- Expiry alerts
- Fraud analytics dashboard

## Tech Stack

Backend: Flask, PostgreSQL, SQLAlchemy, Flask-JWT-Extended  
Frontend: React, Vite, Tailwind CSS  
Security: HMAC-SHA256 QR signatures

## Setup

### Backend

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
flask db upgrade
flask run