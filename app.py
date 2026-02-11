from flask import Flask, jsonify

app = Flask(__name__)

# This is your home page
@app.route('/')
def home():
    return "Hello! This is your first backend response. It's just plain text."

# This is your first API "endpoint"
@app.route('/shush/hello')
def api_hello():
    # This sends back data in a format called JSON (which looks like a list)
    return jsonify(
        message="Hello from the API!",
        status="the principles here dont trully matter, what matters is this sort of barebones thing and what gets it to work",
        data=123
    )

if __name__ == '__main__':
    app.run(debug=True)