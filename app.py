from flask import Flask, request, render_template
import numpy as np
import joblib
app=Flask(__name__)

MODEL_PATH="models/crop recommedation.pkl"
model=joblib.load(MODEL_PATH)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict",methods=["POST"])
def predict():
    try:
        N=float(request.form["N"])
        P=float(request.form["P"])
        K=float(request.form["K"])
        temperature=float(request.form["temperature"])
        humidity=float(request.form["humidity"])
        ph=float(request.form["ph"])
        rainfall=float(request.form["rainfall"])

        features= np.array([[N,P,K,temperature,humidity,ph,rainfall]])
        prediction=model.predict(features)[0]
        
        return render_template(
            "index.html",prediction=prediction,
            form_values={
                    "N": N, "P": P, "K": K,
                    "temperature": temperature, "humidity": humidity,
                    "ph": ph, "rainfall": rainfall,
                },
        )
    except Exception as e:
        return render_template("index.html",error=e)
    
if __name__ == "__main__":
    app.run(debug=False)