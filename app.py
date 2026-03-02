import os
from dotenv import load_dotenv
from app import create_app
from flask import render_template

# Load environment variables here (if not already done by config)
load_dotenv()

# Create the flask app instance using the application factory pattern
app = create_app()

# If you still want to serve the frontend from the root URL
@app.route("/")
def home():
    """Route for the home page."""
    # Ensure frontend/templates is reachable or adjust the template folder path when initializing Flask if necessary
    # The new architecture primarily focuses on JSON APIs (/api/predict)
    # The frontend HTML will need to make an AJAX request to /api/predict
    return render_template("index.html")

if __name__ == "__main__":
    # In production, use a WSGI server like gunicorn or waitress
    # run with debug=True only for development
    app.run(debug=True, port=5000)