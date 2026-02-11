from flask import Flask, jsonify, request
from datetime import datetime

app = Flask(__name__)

# This is our temporary database
DATA = {
    "items": []
}

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
    
    # Validation: Make sure they sent a title
    if not data or "title" not in data:
        return jsonify({"error": "Title is required"}), 400

    # Get the current time
    current_time = datetime.now().isoformat()

    new_item = {
        "id": get_next_id(),
        "title": data["title"],
        "contents": data.get("contents", ""), # attempts to extract data from what was sent under contents, if nothing results in ""
        "priority": data.get("priority", "Medium"),  # <--- YOU ADDED THIS! #get data if none then medium automatically,
        "completed": False, #assumes that the priority = automatically false
        "createdAt": current_time,
        "updatedAt": current_time
    }
    
    DATA["items"].append(new_item)
    return jsonify(new_item), 201

# --- READ (The 'R' in CRUD) ---
@app.route("/items", methods=["GET"])
def list_items():
    return jsonify(DATA["items"])

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