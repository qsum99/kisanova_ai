import os
from dotenv import load_dotenv
from app import create_app
from functools import wraps
from flask import render_template, session, redirect, url_for

load_dotenv()

app = create_app()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function

# Inject user session data into all templates
@app.context_processor
def inject_user():
    return {
        "current_user": session.get("user"),
        "current_role": session.get("role")
    }

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/crop-prediction")
@login_required
def crop_prediction():
    return render_template("crop_prediction.html")

@app.route("/disease-detection")
@login_required
def disease_detection():
    return render_template("disease_detection.html")

@app.route("/crop-prices")
@login_required
def crop_prices():
    return render_template("crop_prices.html")

@app.route("/login")
def login_page():
    return render_template("login.html")

@app.route("/register")
def register_page():
    return render_template("register.html")

if __name__ == "__main__":
    app.run(debug=True, port=5000)