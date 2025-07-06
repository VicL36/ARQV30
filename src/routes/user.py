from flask import Blueprint, request, jsonify
from ..database import SessionLocal
from ..models.user import User

user_bp = Blueprint('user', __name__)

@user_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    db = SessionLocal()
    try:
        if db.query(User).filter(User.email == email).first():
            return jsonify({'error': 'Email already registered'}), 400
        
        new_user = User(email=email)
        new_user.set_password(password)
        db.add(new_user)
        db.commit()
        return jsonify({'message': 'User created successfully'}), 201
    finally:
        db.close()

@user_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if user and user.check_password(password):
            return jsonify({'message': 'Login successful', 'user_id': user.id}), 200
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
    finally:
        db.close()
