from flask import Flask 
from db import init_db
from routes import items_bp

app = Flask(__name__)

app.register_blueprint(items_bp)

# Run this immediately when the app starts
init_db() #here and needed to be called after creating app = flask instance, otherwise it will throw an error as the app instance is needed for the db connection to work

@app.route("/")
def index():
    return "Your To-Do API is running!"

if __name__ == "__main__":
    app.run(port=8000, debug=True)