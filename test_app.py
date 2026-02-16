import pytest
import os
import app as my_app 
import db # <--- We import the new database file directly

@pytest.fixture
def client():
    # 1. TELL THE ROBOT: "Don't touch the real data! Use a test file."
    # We explicitly change the variable inside the db module
    db.DB_NAME = "test.db"
    
    # 2. Initialize the test database (create tables)
    db.init_db()
    
    # 3. Create the Test Client
    with my_app.app.test_client() as client:
        yield client
        
    # 4. Cleanup: Delete the test file after we are done
    if os.path.exists("test.db"):
        os.remove("test.db")

# --- THE TESTS ---

def test_create_item(client):
    """Test if we can create a task"""
    response = client.post("/items", json={"title": "Test Task"})
    assert response.status_code == 201
    assert "id" in response.get_json()

def test_read_items(client):
    """Test if we can read tasks"""
    # Create one task first so we have something to read
    client.post("/items", json={"title": "Read Me"})
    
    response = client.get("/items")
    data = response.get_json()
    
    assert response.status_code == 200
    assert len(data) > 0
    # We check if the LAST item added is the one we want
    assert data[-1]["title"] == "Read Me"

def test_update_item(client):
    """Test if we can update a task"""
    # 1. Create
    create_res = client.post("/items", json={"title": "Update Me"})
    item_id = create_res.get_json()["id"]
    
    # 2. Update
    client.put(f"/items/{item_id}", json={"completed": True})
    
    # 3. Verify
    get_res = client.get("/items")
    data = get_res.get_json()
    # Find the specific item we updated
    item = next((i for i in data if i["id"] == item_id), None)
    assert item is not None
    assert item["completed"] == True

def test_delete_item(client):
    """Test if we can delete a task"""
    # 1. Create
    create_res = client.post("/items", json={"title": "Delete Me"})
    item_id = create_res.get_json()["id"]
    
    # 2. Delete
    del_res = client.delete(f"/items/{item_id}")
    assert del_res.status_code == 200
    
    # 3. Verify it's gone
    # We can't just check len(data) == 0 because other tests might have left data behind
    # We specifically check if THIS item is gone.
    get_res = client.get("/items")
    data = get_res.get_json()
    item = next((i for i in data if i["id"] == item_id), None)
    assert item is None