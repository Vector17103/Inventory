# -*- coding: utf-8 -*-
"""
Created on Sat Nov 15 23:26:47 2025
@author: Achyut Niroula
"""
import os
os.environ["FLASK_ENV"] = "development"

from flask import Flask, request, jsonify, render_template, redirect, url_for, session, g, make_response
import firebase_admin
from firebase_admin import credentials, db, auth
import cloudinary
import cloudinary.uploader
from functools import wraps

# Loading environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Cloudinary setup
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)
print("Cloudinary configured with cloud name:", cloudinary.config().cloud_name)

# Initializing Firebase (Admin SDK)
try:
    firebase_admin.get_app()
except ValueError:
    cred = credentials.Certificate("cosc-4607-firebase-adminsdk.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://cosc-4607-default-rtdb.firebaseio.com/'
    })



# Creating Flask app
app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret")  # a strong key in .env

# ------------- Auth helpers -------------

def verify_firebase_token(id_token: str):
    """
    Verify a Firebase ID token and return decoded claims.
    Raises Exception if invalid/expired.
    """
    decoded = auth.verify_id_token(id_token)
    return decoded

def get_user_role(uid: str) -> str:
    """
    Fetch the user's role from Realtime Database: users/{uid}/role.
    Defaults to 'viewer' if missing.
    """
    role_ref = db.reference(f'users/{uid}/role')
    role = role_ref.get()
    if not role:
        # Initializing default role on first access to avoid None checks elsewhere
        role_ref.set('viewer')
        role = 'viewer'
    return role

@app.before_request
def load_current_user():
    """
    Populate g.user if the session contains a verified user.
    """
    user = session.get('user')
    g.user = user if user else None

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not g.user:
            # If client has an id_token cookie, refreshes session automatically
            id_token = request.cookies.get('id_token')
            if id_token:
                try:
                    claims = verify_firebase_token(id_token)
                    uid = claims.get('uid')
                    email = claims.get('email')
                    role = get_user_role(uid)
                    session['user'] = {'uid': uid, 'email': email, 'role': role}
                    g.user = session['user']
                except Exception:
                    pass
        if not g.user:
            # Not authenticated
            if request.accept_mimetypes.accept_html:
                return redirect(url_for('index'))
            return jsonify({"error": "Authentication required"}), 401
        return f(*args, **kwargs)
    return wrapper

def require_roles(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not g.user:
                return jsonify({"error": "Authentication required"}), 401
            user_role = g.user.get('role', 'viewer')
            if user_role not in allowed_roles:
                return jsonify({"error": "Access denied", "required_roles": allowed_roles, "your_role": user_role}), 403
            return f(*args, **kwargs)
        return wrapper
    return decorator

# ------------- Auth routes -------------

@app.route('/auth/session', methods=['POST'])
def create_session():
    """
    Client posts Firebase ID token after login via Firebase JS SDK.
    Server verifies token, loads/stores role, and sets Flask session.
    Optionally sets a secure cookie with id_token (for silent re-auth).
    """
    payload = request.get_json(silent=True) or {}
    id_token = payload.get('idToken')
    if not id_token:
        return jsonify({"error": "idToken required"}), 400

    try:
        claims = verify_firebase_token(id_token)
        uid = claims.get('uid')
        email = claims.get('email')
        role = get_user_role(uid)

        session['user'] = {'uid': uid, 'email': email, 'role': role}

        resp = make_response(jsonify({"status": "session_created", "role": role, "email": email}))
        # Setting a short-lived cookie (client will refresh via JS when needed)
        resp.set_cookie(
            'id_token',
            id_token,
            httponly=True,        # mitigate XSS
            secure=True,          # require HTTPS in production
            samesite='Lax',       # CSRF protection with forms
            max_age=60 * 60       # 1 hour
        )
        return resp
    except Exception as e:
        return jsonify({"error": "Invalid or expired token", "details": str(e)}), 401

@app.route('/logout', methods=['POST', 'GET'])
def logout():
    """
    Clear session and id_token cookie.
    """
    session.pop('user', None)
    resp = make_response(redirect(url_for('index')))
    resp.set_cookie('id_token', '', expires=0)
    return resp

# ------------- Utility -------------

def upload_image_to_cloudinary(file):
    """
    Uploads a file-like object to Cloudinary and returns a secure URL.
    """
    result = cloudinary.uploader.upload(
        file,
        folder="inventory",
        resource_type="image",
        overwrite=False,
        unique_filename=True
    )
    return result.get("secure_url")

def safe_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default

def safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default

# ------------- Routes -------------

@app.route('/')
def index():
    """
    Landing page. If authenticated, redirect to dashboard.
    """
    if g.user:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    ref = db.reference('inventory')
    items = ref.get() or {}

    total_value = 0
    total_items = 0
    category_counts = {}
    category_values = {}

    for key, item in items.items():
        qty = safe_int(item.get('quantity', 0))
        price = safe_float(item.get('price', 0.0))
        category = item.get('category', 'Uncategorized')

        total_value += qty * price
        total_items += qty
        category_counts[category] = category_counts.get(category, 0) + qty
        category_values[category] = category_values.get(category, 0.0) + (qty * price)

    return render_template(
        'dashboard.html',
        total_value=total_value,
        total_items=total_items,
        category_counts=category_counts,
        category_values=category_values,
        user=g.user
    )
@app.route('/inventory')
@login_required
def inventory():
    return render_template('index.html')

@app.route('/items', methods=['GET'])
@login_required
def get_items():
    """
    View items: any authenticated user can read.
    """
    ref = db.reference('inventory')
    items = ref.get() or {}
    return jsonify(items)

@app.route('/add', methods=['POST'])
@login_required
@require_roles('admin', 'editor')
def add_item():
    """
    Create item: restricted to admin/editor.
    """
    data = request.form.to_dict()
    image = request.files.get('image')
    image_url = None
    if image and image.filename:
        try:
            image_url = upload_image_to_cloudinary(image)
        except Exception as e:
            print("Cloudinary upload failed:", e)

    ref = db.reference('inventory')
    ref.push({
        'name': data.get('name'),
        'quantity': safe_int(data.get('quantity')),
        'price': safe_float(data.get('price')),
        'category': data.get('category'),
        'imageURL': image_url,
        'ownerUID': g.user.get('uid')  # tracking who added
    })
    return jsonify({"status": "Item added!"}), 200

@app.route('/delete/<item_id>', methods=['DELETE'])
@login_required
@require_roles('admin')
def delete_item(item_id):
    """
    Delete item: restricted to admin only.
    """
    ref = db.reference('inventory/' + item_id)
    if ref.get() is None:
        return jsonify({"error": "Item not found"}), 404
    ref.delete()
    return jsonify({"status": f"Item {item_id} deleted!"})

@app.route('/update_quantity/<item_id>', methods=['POST'])
@login_required
@require_roles('admin', 'editor')
def update_quantity(item_id):
    """
    Update quantity: restricted to admin/editor.
    """
    ref = db.reference('inventory/' + item_id)
    item = ref.get()
    if item is None:
        return jsonify({"error": "Item not found"}), 404

    payload = request.get_json(silent=True) or {}
    action = payload.get("action")  # "increase" or "decrease"
    qty = safe_int(item.get('quantity', 0))

    if action == "increase":
        qty += 1
    elif action == "decrease" and qty > 0:
        qty -= 1
    else:
        return jsonify({"error": "Invalid action"}), 400

    ref.update({"quantity": qty})
    return jsonify({"status": "Quantity updated", "new_quantity": qty}), 200


if __name__ == '__main__':
    print("Flask app running at http://127.0.0.1:8080")
    app.run(host='0.0.0.0', port=8080, debug=True)
