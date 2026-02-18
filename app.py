from flask import Flask, render_template, request, jsonify
import numpy as np
import joblib

app = Flask(__name__)

# -----------------------------
# Load Trained Model
# -----------------------------
model = joblib.load("credit_model.pkl")

# -----------------------------
# PD → CIBIL Conversion
# -----------------------------
def pd_to_cibil(pd_value):
    pd_value = float(np.clip(pd_value, 0.0001, 0.9999))
    A = 600
    B = 50
    score = A - B * np.log(pd_value / (1 - pd_value))
    return float(np.clip(score, 300, 900))

# -----------------------------
# Risk Band Classification
# -----------------------------
def risk_band(score):
    if score < 550:
        return "Poor (High Risk)"
    elif score < 650:
        return "Fair (Medium Risk)"
    elif score < 750:
        return "Good (Low Risk)"
    else:
        return "Excellent (Very Low Risk)"

# -----------------------------
# Encoding Helper
# -----------------------------
def encode_inputs(gender, car, realty):
    g = 1 if gender.upper() == "M" else 0
    c = 1 if car.upper() == "Y" else 0
    r = 1 if realty.upper() == "Y" else 0
    return g, c, r

# -----------------------------
# Routes
# -----------------------------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():

    try:
        data = request.json

        income = float(data["income"])
        credit = float(data["credit"])
        annuity = float(data["annuity"])
        children = float(data["children"])
        bureau_year = float(data["bureau_year"])

        gender = data["gender"]
        car = data["car"]
        realty = data["realty"]

        # Encode categorical
        g, c, r = encode_inputs(gender, car, realty)

        # Feature engineering
        debt_income = annuity / (income + 1)
        credit_income = credit / (income + 1)

        # Prepare input in SAME order as training
        X = np.array([[income,
                       credit,
                       annuity,
                       children,
                       bureau_year,
                       g,
                       c,
                       r,
                       debt_income,
                       credit_income]])

        # Predict PD
        pd_value = model.predict_proba(X)[0][1]

        # Convert to CIBIL
        cibil_score = pd_to_cibil(pd_value)
        band = risk_band(cibil_score)

        return jsonify({
            "pd": round(float(pd_value), 4),
            "cibil_score": int(round(cibil_score)),
            "risk_band": band
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(debug=True)
