from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from sklearn.preprocessing import LabelEncoder
import numpy as np
import pandas as pd
import pickle
import io
import os

# APP CONFIG
app = Flask(__name__)
CORS(app)

# BASE_DIR → the directory where app.py lives (root of your project)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Paths to model & data inside tea_models_project
MODEL_PATH = os.path.join(BASE_DIR, "tea_models_project", "ExtraTrees_model.pkl")
DATA_PATH = os.path.join(BASE_DIR, "tea_models_project", "tea_aroma_balanced.csv")

# MODEL LOADING
try:
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
    print("ExtraTrees model loaded successfully")
    MODEL_LOADED = True
except Exception as e:
    print(f"Model loading error: {e}")
    MODEL_LOADED = False

# DATA & ENCODER
data = pd.read_csv(DATA_PATH)

X_data = data.iloc[:, :-1]
y_data = data.iloc[:, -1]

encoder = LabelEncoder()
encoder.fit(y_data)

TEA_REGIONS = list(encoder.classes_)
SENSOR_COLUMNS = X_data.columns.tolist()

# SENSOR RANGE STATISTICS
GLOBAL_MIN = X_data.min()
GLOBAL_MAX = X_data.max()

REGION_MIN_MAX = {}
for region in TEA_REGIONS:
    subset = data[data.iloc[:, -1] == region].iloc[:, :-1]
    REGION_MIN_MAX[region] = {
        "min": subset.min(),
        "max": subset.max()
    }

TOLERANCE = 5.0
CONFIDENCE_THRESHOLD = 0.55

# ROUTES
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/map")
def map_page():
    return render_template("map.html")

@app.route("/model")
def model_page():
    return render_template("model.html")

# HELPER FUNCTIONS
def global_range_check(sensors):
    for i, val in enumerate(sensors):
        if val < (GLOBAL_MIN.iloc[i] - TOLERANCE) or val > (GLOBAL_MAX.iloc[i] + TOLERANCE):
            return False
    return True

def region_range_check(region, sensors):
    stats = REGION_MIN_MAX[region]
    for i, val in enumerate(sensors):
        if val < (stats["min"].iloc[i] - TOLERANCE) or val > (stats["max"].iloc[i] + TOLERANCE):
            return False
    return True

# SINGLE PREDICTION
@app.route("/predict", methods=["POST"])
def predict():
    if not MODEL_LOADED:
        return jsonify({"success": False, "error": "Model not loaded"}), 500

    try:
        payload = request.get_json()
        sensors = payload.get("sensors")

        if not isinstance(sensors, list) or len(sensors) != 7:
            return jsonify({
                "success": False,
                "error": "Exactly 7 sensor values required"
            }), 400

        sensors = [float(v) for v in sensors]

        # ---- GLOBAL OOD CHECK ----
        if not global_range_check(sensors):
            return jsonify({
                "success": False,
                "reason": "OOD_GLOBAL",
                "error": "Input values are far outside trained sensor ranges"
            }), 422

        X = np.array([sensors])

        # ---- MODEL PREDICTION ----
        pred_idx = model.predict(X)[0]
        predicted_region = encoder.inverse_transform([pred_idx])[0]
        probabilities = model.predict_proba(X)[0]
        confidence = float(probabilities[pred_idx])

        # ---- CONFIDENCE CHECK ----
        if confidence < CONFIDENCE_THRESHOLD:
            return jsonify({
                "success": False,
                "reason": "LOW_CONFIDENCE",
                "confidence": confidence,
                "error": "Low model confidence – unclear region"
            }), 422

        # ---- REGION ENVELOPE CHECK ----
        if not region_range_check(predicted_region, sensors):
            return jsonify({
                "success": False,
                "reason": "REGION_MISMATCH",
                "predicted_region": predicted_region,
                "confidence": confidence,
                "error": "Sensor pattern does not fit predicted region"
            }), 422

        # ---- SUCCESS ----
        return jsonify({
            "success": True,
            "prediction": predicted_region,
            "confidence": confidence,
            "probabilities": dict(zip(encoder.classes_, probabilities)),
            "input_sensors": sensors,
            "model": "ExtraTrees"
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# BATCH PREDICTION
@app.route("/predict-batch", methods=["POST"])
def predict_batch():
    if not MODEL_LOADED:
        return jsonify({"success": False, "error": "Model not loaded"}), 500

    try:
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files["file"]

        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400

        if not file.filename.lower().endswith(".csv"):
            return jsonify({"error": "Only CSV files are accepted"}), 400

        df = pd.read_csv(io.StringIO(file.read().decode("utf-8")))

        if df.shape[1] != 7:
            return jsonify({"error": "CSV must contain exactly 7 sensor columns"}), 400

        if len(df) == 0:
            return jsonify({"error": "CSV file is empty"}), 400

        if len(df) > 500:
            return jsonify({"error": "Maximum 500 samples per upload"}), 400

        results = []

        for idx, row in df.iterrows():
            sensors = row.values.astype(float).tolist()

            sample = {
                "sample_index": idx + 1,
                "input_sensors": sensors,
                "status": "REJECTED"
            }

            if not global_range_check(sensors):
                sample.update({"reason": "OOD_GLOBAL"})
                results.append(sample)
                continue

            X = np.array([sensors])
            pred_idx = model.predict(X)[0]
            predicted_region = encoder.inverse_transform([pred_idx])[0]
            probabilities = model.predict_proba(X)[0]
            confidence = float(probabilities[pred_idx])

            if confidence < CONFIDENCE_THRESHOLD:
                sample.update({"reason": "LOW_CONFIDENCE", "confidence": confidence})
                results.append(sample)
                continue

            if not region_range_check(predicted_region, sensors):
                sample.update({
                    "reason": "REGION_MISMATCH",
                    "predicted_region": predicted_region,
                    "confidence": confidence
                })
                results.append(sample)
                continue

            sample.update({
                "status": "ACCEPTED",
                "prediction": predicted_region,
                "confidence": confidence,
                "probabilities": dict(zip(encoder.classes_, probabilities))
            })

            results.append(sample)

        return jsonify({
            "success": True,
            "total_samples": len(results),
            "accepted": sum(r["status"] == "ACCEPTED" for r in results),
            "rejected": sum(r["status"] == "REJECTED" for r in results),
            "model": "ExtraTrees",
            "results": results
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# HEALTH CHECK
@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "model_loaded": MODEL_LOADED,
        "regions": TEA_REGIONS,
        "tolerance": TOLERANCE,
        "confidence_threshold": CONFIDENCE_THRESHOLD
    })

# RUN (LOCAL ONLY – RENDER USES GUNICORN)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
