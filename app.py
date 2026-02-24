import time
import random
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# --- CONFIGURATION ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///wallets.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- MODELS ---

class Wallet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.String(50), unique=True, nullable=False)
    balance = db.Column(db.Integer, default=0, nullable=False)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    fulfillment_id = db.Column(db.String(50), nullable=True)
    status = db.Column(db.String(20), default='PENDING')

# --- HELPER FUNCTIONS ---

def mock_fulfillment_api(order_id):
    time.sleep(0.5) 
    return f"FULFILL-{order_id}-{random.randint(1000,9999)}"

# --- ROUTES ---

@app.route('/')
def home():
    return "The Transaction System is Running! Use Postman to test the APIs."

@app.route('/admin/wallet', methods=['POST'])
def admin_update_wallet():
    data = request.get_json()
    client_id = data.get('client_id')
    amount = data.get('amount')
    action = data.get('action', 'credit')

    if not client_id or amount is None:
        return jsonify({'error': 'Invalid input'}), 400

    try:
        wallet = Wallet.query.filter_by(client_id=client_id).with_for_update().first()

        if not wallet:
            if action == 'debit':
                return jsonify({'error': 'Wallet not found'}), 404
            wallet = Wallet(client_id=client_id, balance=0)
            db.session.add(wallet)
        
        if action == 'credit':
            wallet.balance += amount
        elif action == 'debit':
            if wallet.balance < amount:
                return jsonify({'error': 'Insufficient funds'}), 400
            wallet.balance -= amount

        db.session.commit()
        return jsonify({'message': 'Success', 'new_balance': wallet.balance})

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/orders', methods=['POST'])
def create_order():
    data = request.get_json()
    client_id = data.get('client_id')
    amount = data.get('amount')

    if not client_id or not amount:
        return jsonify({'error': 'Missing data'}), 400

    try:
        # Step 1: Deduct Balance
        wallet = Wallet.query.filter_by(client_id=client_id).with_for_update().first()

        if not wallet or wallet.balance < amount:
            db.session.rollback()
            return jsonify({'error': 'Insufficient funds'}), 400

        wallet.balance -= amount
        new_order = Order(client_id=client_id, amount=amount, status='PROCESSING')
        db.session.add(new_order)
        db.session.commit()

        # Step 2: Call External API
        fulfillment_id = mock_fulfillment_api(new_order.id)

        # Step 3: Update Order
        order_record = Order.query.get(new_order.id)
        order_record.fulfillment_id = fulfillment_id
        order_record.status = 'COMPLETED'
        db.session.commit()

        return jsonify({'message': 'Order processed', 'fulfillment_id': fulfillment_id})

    except Exception as e:
        return jsonify({'error': f"Order failed: {str(e)}"}), 500

# --- SERVER STARTUP ---

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    # FIX: use_reloader=False prevents the SystemExit error in VS Code
    app.run(debug=True, port=5000, use_reloader=False)
