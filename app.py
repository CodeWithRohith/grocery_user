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

# -----------------------------------
# 🚀 APP RUN
# -----------------------------------

if __name__ == '__main__':
    app.run(debug=True)
