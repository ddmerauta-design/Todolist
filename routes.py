from flask import Blueprint, request, jsonify
from datetime import datetime
from db import get_db_connection
from schemas import item_schema
from marshmallow import ValidationError

# This acts like a mini-app that holds all your routes related to "items". It helps us keep things organized.
items_bp = Blueprint('items', __name__)

# 2. Use @items_bp.route instead of @items_bp.route

# --- CREATE (The 'C' in CRUD) ---
@items_bp.route("/items", methods=["POST"])
def create_item():
    json_data = request.get_json()
    if not json_data:
        return jsonify({"message": "No input data provided"}), 400

    # 1. VALIDATION: Check if the data follows the rules
    try:
        data = item_schema.load(json_data)
    except ValidationError as err:
        # If the data is bad, stop here and tell the user why
        return jsonify(err.messages), 422

    # 2. If it passed, continue to database logic
    current_time = datetime.now().isoformat()
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO items (title, contents, priority, completed, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        data["title"],
        data.get("contents", ""),
        data.get("priority", "Medium"),
        False,
        current_time,
        current_time
    ))
    conn.commit()
    new_id = c.lastrowid
    conn.close()

    return jsonify({"id": new_id, "message": "Saved to database!"}), 201

# --- READ (The 'R' in CRUD) ---
@items_bp.route("/items", methods=["GET"])
def list_items():
    conn = get_db_connection()
    # This weird line helps us get data back as a dictionary (key: value)
    c = conn.cursor()
    
    c.execute("SELECT * FROM items")
    rows = c.fetchall()
    
    # Convert database rows back to a Python list
    results = [dict(row) for row in rows]
    
    conn.close()
    return jsonify(results)

# --- UPDATE (The 'U' in CRUD) ---
@items_bp.route("/items/<int:item_id>", methods=["PUT"])
def update_item(item_id):
    json_data = request.get_json()
    
    # 1. Ask the Security Guard to check the incoming data
    try:
        # partial=True allows us to update just one field (like only 'completed')
        data = item_schema.load(json_data, partial=True)
    except ValidationError as err:
        return jsonify(err.messages), 422

    # 2. Build the SQL update dynamically based on the VALIDATED data
    fields_to_update = []
    values = []
    
    for key, value in data.items():
        fields_to_update.append(f"{key} = ?")
        values.append(value)
        
    if not fields_to_update:
        return jsonify({"error": "No valid data provided"}), 400
        
    # Always update the timestamp
    fields_to_update.append("updated_at = ?")
    values.append(datetime.now().isoformat())
    
    # Add the ID for the WHERE clause
    values.append(item_id)
    
    sql_query = f"UPDATE items SET {', '.join(fields_to_update)} WHERE id = ?"
    
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(sql_query, values)
    conn.commit()
    
    if c.rowcount == 0:
        conn.close()
        return jsonify({"error": "Item not found"}), 404
        
    conn.close()
    return jsonify({"message": "Item updated", "id": item_id})

# --- DELETE (The 'D' in CRUD) ---
@items_bp.route("/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    conn = get_db_connection()
    c = conn.cursor()
    
    # SQL Translation: "Delete from the 'items' table where the id matches X"
    c.execute("DELETE FROM items WHERE id = ?", (item_id,))
    
    conn.commit()
    
    # Check if we actually deleted something (rowcount tells us how many rows were affected)
    if c.rowcount == 0:
        conn.close()
        return jsonify({"error": "Item not found"}), 404
        
    conn.close()
    return jsonify({"message": "Item deleted"}), 200

# --- CLEANUP (Delete all completed) ---
@items_bp.route("/items/cleanup", methods=["DELETE"])
def cleanup_completed():
    conn = get_db_connection()
    c = conn.cursor()
    
    # SQL: Delete every row where completed is 1 (True)
    c.execute("DELETE FROM items WHERE completed = 1")
    
    conn.commit()
    deleted_count = c.rowcount # How many did we zap?
    conn.close()
    
    return jsonify({"message": f"Deleted {deleted_count} completed items"}), 200

# --- SORTING (Advanced Read) --- ( TIME RELATED)
@items_bp.route("/items/sorted", methods=["GET"])
def get_sorted_items():
    conn = get_db_connection()
   # conn.row_factory = sqlite3.Row no longer needed as db connection handles this for us now
    c = conn.cursor()
    
    # SQL: Select all items, but order them by creation date (Descending)
    c.execute("SELECT * FROM items ORDER BY created_at DESC")
    rows = c.fetchall()
    
    results = [dict(row) for row in rows]
    conn.close()
    
    return jsonify(results)