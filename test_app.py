import pytest
import os
import app as my_app
import json

# This "Fixture" sets up a fake environment for every test
@pytest.fixture
def client():
    # 1. Switch to a test database so we don't delete your real data
    my_app.DB_NAME = "test.db"
    
    # 2. Initialize the test database
    my_app.init_db()
    
    # 3. Create a "Test Client" (a fake browser)
    with my_app.app.test_client() as client:
        yield client
        
    # 4. Cleanup: Delete the test database after we are done
    if os.path.exists("test.db"):
        os.remove("test.db")

# --- THE TESTS ---

def test_create_item(client):
    """The Robot tries to create a task."""
    response = client.post("/items", json={"title": "Test Task"})
    
    # Assert checks if the result is what we expect
    assert response.status_code == 201
    assert response.json["message"] == "Saved to database!"

def test_read_items(client):
    """The Robot creates a task and checks if it can read it back."""
    client.post("/items", json={"title": "Read Me"})
    
    response = client.get("/items")
    data = response.json
    
    assert response.status_code == 200
    assert len(data) > 0
    assert data[0]["title"] == "Read Me"

def test_update_item(client):
    """The Robot creates a task, updates it, and checks the change."""
    # 1. Create
    create_res = client.post("/items", json={"title": "Update Me"})
    item_id = create_res.json["id"]
    
    # 2. Update
    client.put(f"/items/{item_id}", json={"completed": True})
    
    # 3. Verify
    get_res = client.get("/items")
    item = next(i for i in get_res.json if i["id"] == item_id)
    assert item["completed"] == True

def test_delete_item(client):
    """The Robot creates a task and then destroys it."""
    # 1. Create
    create_res = client.post("/items", json={"title": "Delete Me"})
    item_id = create_res.json["id"]
    
    # 2. Delete
    del_res = client.delete(f"/items/{item_id}")
    assert del_res.status_code == 200
    
    # 3. Verify it's gone
    get_res = client.get("/items")
    assert len(get_res.json) == 0