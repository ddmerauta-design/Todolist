from flask import Flask, jsonify, request
import sqlite3
from datetime import datetime

app = Flask(__name__)

DB_NAME = "todo.db"
# This is our temporary database, we no longer need this if implementing sqlite, this was the whiteboard
# Now the U and D from our CRUD wont be able to update any longer as its trying to reference the previous temporary DATA cache

#DATA = {
#    "items": []
#}

def init_db():
    conn = sqlite3.connect(DB_NAME)
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
    conn = sqlite3.connect(DB_NAME)
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
    conn = sqlite3.connect(DB_NAME)
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
    data = request.get_json()
    
    # 1. Start building the SQL sentence
    # We will collect pieces like "title = ?" and "completed = ?"
    fields_to_update = []
    values = []
    
    if "title" in data:
        fields_to_update.append("title = ?")
        values.append(data["title"])
        
    if "contents" in data:
        fields_to_update.append("contents = ?")
        values.append(data["contents"])
        
    if "priority" in data:
        fields_to_update.append("priority = ?")
        values.append(data["priority"])
        
    if "completed" in data:
        fields_to_update.append("completed = ?")
        values.append(data["completed"])
        
    # If they didn't send any valid fields, stop here
    if not fields_to_update:
        return jsonify({"error": "No data provided"}), 400
        
    # Always update the 'updatedAt' time
    fields_to_update.append("updated_at = ?")
    values.append(datetime.now().isoformat())
    
    # Add the ID at the end for the "WHERE id = ?" part
    values.append(item_id)
    
    # 2. Join the pieces together into one big SQL string
    # It will look like: "UPDATE items SET title = ?, completed = ? WHERE id = ?"
    sql_query = f"UPDATE items SET {', '.join(fields_to_update)} WHERE id = ?"
    
    # 3. Execute it
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(sql_query, values)
    conn.commit()
    
    if c.rowcount == 0:
        conn.close()
        return jsonify({"error": "Item not found"}), 404
        
    conn.close()
    
    # 4. Return the updated item so the user can see it
    return jsonify({"message": "Item updated", "id": item_id})

# --- DELETE (The 'D' in CRUD) ---
@app.route("/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    conn = sqlite3.connect(DB_NAME)
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
@app.route("/items/cleanup", methods=["DELETE"])
def cleanup_completed():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # SQL: Delete every row where completed is 1 (True)
    c.execute("DELETE FROM items WHERE completed = 1")
    
    conn.commit()
    deleted_count = c.rowcount # How many did we zap?
    conn.close()
    
    return jsonify({"message": f"Deleted {deleted_count} completed items"}), 200

# --- SORTING (Advanced Read) --- ( TIME RELATED)
@app.route("/items/sorted", methods=["GET"])
def get_sorted_items():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # SQL: Select all items, but order them by creation date (Descending)
    c.execute("SELECT * FROM items ORDER BY created_at DESC")
    rows = c.fetchall()
    
    results = [dict(row) for row in rows]
    conn.close()
    
    return jsonify(results)

if __name__ == "__main__":
    app.run(port=8000, debug=True)