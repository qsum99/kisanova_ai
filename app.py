import os
from dotenv import load_dotenv
from app import create_app
from flask import render_template

load_dotenv()

app = create_app()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/crop-prediction")
def crop_prediction():
    return render_template("crop_prediction.html")

@app.route("/disease-detection")
def disease_detection():
    return render_template("disease_detection.html")

if __name__ == "__main__":
    app.run(debug=True, port=5000)