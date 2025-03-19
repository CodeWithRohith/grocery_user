from flask import Flask, jsonify, request
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import os

app = Flask(__name__)

# MongoDB Atlas connection using environment variables
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://rohith:p3drlCoZj9pNKoJf@grocerystorecluster.2pjph.mongodb.net/?retryWrites=true&w=majority")
client = MongoClient(MONGO_URI)
db = client['grocery_store']

# Helper function for responses
def generate_response(status, message, data=None):
    response = {"status": status, "message": message}
    if data:
        response["data"] = data
    return jsonify(response)

# -----------------------------------
# 🚀 USER APIs
# -----------------------------------

@app.route('/users', methods=['POST'])
def add_user():
    """Add a new user."""
    user_data = request.json
    required_fields = ["name", "email", "password"]

    if not all(field in user_data for field in required_fields):
        return generate_response("error", "Missing required fields (name, email, password)"), 400

    user_data["created_at"] = datetime.utcnow()
    user_id = db["users"].insert_one(user_data).inserted_id
    return generate_response("success", "User added successfully", {"user_id": str(user_id)}), 201

@app.route('/users', methods=['GET'])
def get_all_users():
    """Get all users."""
    users = list(db["users"].find({}, {"password": 0}))  # Exclude password for security
    for user in users:
        user["_id"] = str(user["_id"])
    return generate_response("success", "All users retrieved successfully", users), 200

@app.route('/users/<user_id>', methods=['GET'])
def get_user(user_id):
    """Get a user by ID."""
    try:
        user = db["users"].find_one({"_id": ObjectId(user_id)}, {"password": 0})  # Exclude password
        if user:
            user["_id"] = str(user["_id"])
            return generate_response("success", "User found", user), 200
        return generate_response("error", "User not found"), 404
    except Exception as e:
        return generate_response("error", str(e)), 400

@app.route('/users/<user_id>', methods=['PUT'])
def update_user(user_id):
    """Update a user."""
    updated_data = request.json
    if not updated_data:
        return generate_response("error", "No data provided for update"), 400

    result = db["users"].update_one({"_id": ObjectId(user_id)}, {"$set": updated_data})
    if result.matched_count:
        return generate_response("success", "User updated successfully"), 200
    return generate_response("error", "User not found"), 404

@app.route('/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete a user."""
    result = db["users"].delete_one({"_id": ObjectId(user_id)})
    if result.deleted_count:
        return generate_response("success", "User deleted successfully"), 200
    return generate_response("error", "User not found"), 404

# -----------------------------------
# 🛒 CART APIs
# -----------------------------------

@app.route('/users/<user_id>/cart', methods=['POST'])
def add_to_cart(user_id):
    """Add an item to the user's cart."""
    cart_data = request.json
    required_fields = ["product_id", "name", "quantity", "price"]

    if not all(field in cart_data for field in required_fields):
        return generate_response("error", "Missing required fields (product_id, name, quantity, price)"), 400

    cart_data["user_id"] = user_id
    cart_data["created_at"] = datetime.utcnow()
    cart_id = db["carts"].insert_one(cart_data).inserted_id
    return generate_response("success", "Item added to cart successfully", {"cart_id": str(cart_id)}), 201

@app.route('/users/<user_id>/cart', methods=['GET'])
def get_cart(user_id):
    """Get all items in the user's cart."""
    cart_items = list(db["carts"].find({"user_id": user_id}))
    for item in cart_items:
        item["_id"] = str(item["_id"])
    return generate_response("success", "Cart items retrieved successfully", cart_items), 200

@app.route('/users/<user_id>/cart/<item_id>', methods=['DELETE'])
def remove_from_cart(user_id, item_id):
    """Remove an item from the cart."""
    result = db["carts"].delete_one({"_id": ObjectId(item_id), "user_id": user_id})
    if result.deleted_count:
        return generate_response("success", "Item removed from cart successfully"), 200
    return generate_response("error", "Item not found in cart"), 404

# -----------------------------------
# 🚀 APP RUN
# -----------------------------------

if __name__ == '__main__':
    app.run(debug=True)
