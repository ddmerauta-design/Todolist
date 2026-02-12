from flask import Flask, jsonify, request
import sqlite3
from datetime import datetime

app = Flask(__name__)

# This is our temporary database, we no longer need this if implementing sqlite, this was the whiteboard
#
#DATA = {
#    "items": []
#}

def init_db():
    conn = sqlite3.connect('todo.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            contents TEXT,
            priority TEXT,
            completed BOOLEAN,
            created_at TEXT,
            updated_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Run this immediately when the app starts
init_db()

def get_next_id():
    # If list is empty, start at ID 1. Otherwise, find the highest ID and add 1.
    if not DATA["items"]:
        return 1
    return max(item["id"] for item in DATA["items"]) + 1

@app.route("/")
def index():
    return "Your To-Do API is running!"

# --- CREATE (The 'C' in CRUD) ---
@app.route("/items", methods=["POST"])

def create_item():
    data = request.get_json()
    
    # 1. Validation (Same as before)
    if not data or "title" not in data:
        return jsonify({"error": "Title is required"}), 400

    current_time = datetime.now().isoformat()
    
    # 2. Connect to the filing cabinet
    conn = sqlite3.connect('todo.db')
    c = conn.cursor()
    
    # 3. Insert the data (SQL Language)
    # The '?' marks are placeholders for safety
    c.execute('''
        INSERT INTO items (title, contents, priority, completed, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        data["title"],
        data.get("contents", ""),
        data.get("priority", "Medium"),
        False,  # completed is False by default
        current_time,
        current_time
    ))
    
    # 4. Save and Close
    conn.commit()
    new_id = c.lastrowid # Get the ID of the item we just made
    conn.close()

    # Return the new ID so the user knows it worked
    return jsonify({"id": new_id, "message": "Saved to database!"}), 201

# --- READ (The 'R' in CRUD) ---
@app.route("/items", methods=["GET"])
def list_items():
    conn = sqlite3.connect('todo.db')
    # This weird line helps us get data back as a dictionary (key: value)
    conn.row_factory = sqlite3.Row 
    c = conn.cursor()
    
    c.execute("SELECT * FROM items")
    rows = c.fetchall()
    
    # Convert database rows back to a Python list
    results = [dict(row) for row in rows]
    
    conn.close()
    return jsonify(results)

# --- UPDATE (The 'U' in CRUD) ---
@app.route("/items/<int:item_id>", methods=["PUT"])
def update_item(item_id):
    # 1. Find the item
    item = next((i for i in DATA["items"] if i["id"] == item_id), None)
    
    # 2. If it doesn't exist, yell at the user
    if item is None:
        return jsonify({"error": "Item not found"}), 404

    # 3. Get the new data
    data = request.get_json()

    # 4. Update fields ONLY if the user sent them
    if "title" in data:
        item["title"] = data["title"]
    if "contents" in data:
        item["contents"] = data["contents"]
    if "priority" in data:
        item["priority"] = data["priority"]
    if "completed" in data:
        item["completed"] = data["completed"]

    # 5. Always update the timestamp
    item["updatedAt"] = datetime.now().isoformat()

    return jsonify(item)

# --- DELETE (The 'D' in CRUD) ---
@app.route("/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    global DATA
    # This weird looking line keeps every item EXCEPT the one we want to delete
    DATA["items"] = [item for item in DATA["items"] if item["id"] != item_id]
    
    return jsonify({"message": "Item deleted"}), 200

# --- CLEANUP (Delete all completed) ---
@app.route("/items/cleanup", methods=["DELETE"])
def cleanup_completed():
    global DATA
    # Logic: Keep the item ONLY if 'completed' is False
    DATA["items"] = [item for item in DATA["items"] if item["completed"] == False]
    
    return jsonify({"message": "Completed items deleted"}), 200

# --- SORTING (Advanced Read) --- ( TIME RELATED)
@app.route("/items/sorted", methods=["GET"])
def get_sorted_items():
    # 'key=lambda x: ...' is just a fancy way of saying:
    # "For every item 'x', use its 'createdAt' value to decide the order."
    # reverse=True means Descending (Newest first).
    sorted_list = sorted(DATA["items"], key=lambda x: x["createdAt"], reverse=True)
    
    return jsonify(sorted_list)

if __name__ == "__main__":
    app.run(port=8000, debug=True)