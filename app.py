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

# ── Phase 5 Routes ──
@app.route("/farm-setup")
@login_required
def farm_setup():
    return render_template("farm_setup.html")

@app.route("/irrigation")
@login_required
def irrigation():
    return render_template("irrigation.html")

@app.route("/fertilizer")
@login_required
def fertilizer():
    return render_template("fertilizer.html")

@app.route("/farm-health")
@login_required
def farm_health():
    return render_template("farm_health.html")

@app.route("/admin/phase5-status")
@login_required
def admin_phase5_status_page():
    if session.get("role") != "admin":
        return redirect("/")
    return render_template("admin_phase5.html")



if __name__ == "__main__":
    app.run(debug=True, port=5000)