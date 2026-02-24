# Optiminastic_Assesment.

Wallet & Transaction System API
A robust, lightweight backend for managing digital wallets and order processing. Built with Python and Flask, this system ensures financial data integrity through atomic transactions and database locking.

Features: 
Integer-Based Balances: Money is stored in cents (e.g., $10.00 = 1000) to eliminate floating-point rounding errors.

Concurrency Control: Uses SQLAlchemy’s with_for_update() to lock database rows, preventing users from spending the same balance twice simultaneously.

Atomic Order Workflow: Deducts funds before calling external services to ensure the system never loses track of money.

Mock Fulfillment Integration: Simulates a real-world logistics API call with a tracking ID return.

Tech Stack: 
Language: Python 3.x

Framework: Flask

ORM: SQLAlchemy

Database: SQLite (Auto-generated)

Installation & Setup

Install Dependencies:

Bash
pip install flask flask-sqlalchemy
Run the Server:

Bash
python app.py
Note: The server runs on http://127.0.0.1:5000.

🔌 API Endpoints
1. Admin: Credit/Debit Wallet
POST /admin/wallet
Updates or creates a user's wallet.

JSON
{
  "client_id": "user_123",
  "amount": 1000,
  "action": "credit" 
}
2. Client: Create Order
POST /orders
Deducts the amount from the wallet and triggers fulfillment.

JSON
{
  "client_id": "user_123",
  "amount": 500
}

Testing
You can test the endpoints using the browser console, Postman, or curl:

Bash
curl -X POST http://127.0.0.1:5000/admin/wallet \
     -H "Content-Type: application/json" \
     -d '{"client_id": "alice", "amount": 2000, "action": "credit"}'
