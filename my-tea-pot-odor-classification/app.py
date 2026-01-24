from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from sklearn.preprocessing import LabelEncoder
import numpy as np
import pandas as pd
import pickle
import io

app = Flask(__name__)
CORS(app)

# MODEL LOADING
MODEL_PATH = 'tea_models_project\\ExtraTrees_model.pkl'

try:
    with open(MODEL_PATH, 'rb') as f:
        model = pickle.load(f)
    print("ExtraTrees model loaded successfully!")
    MODEL_LOADED = True
except Exception as e:
    print(f"Model loading error: {e}")
    MODEL_LOADED = False

# DATA & ENCODER
DATA_PATH = "tea_models_project\\tea_aroma_balanced.csv"
data = pd.read_csv(DATA_PATH)

X_data = data.iloc[:, :-1]
y_data = data.iloc[:, -1]

encoder = LabelEncoder()
encoder.fit(y_data)

TEA_REGIONS = list(encoder.classes_)

# SENSOR RANGE STATISTICS
SENSOR_COLUMNS = X_data.columns.tolist()

GLOBAL_MIN = X_data.min()
GLOBAL_MAX = X_data.max()

REGION_MIN_MAX = {}
for region in TEA_REGIONS:
    subset = data[data.iloc[:, -1] == region].iloc[:, :-1]
    REGION_MIN_MAX[region] = {
        "min": subset.min(),
        "max": subset.max()
    }

TOLERANCE = 5.0              # ±5 deviation
CONFIDENCE_THRESHOLD = 0.55  # confidence gate

# ROUTES
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/map')
def map_page():
    return render_template('map.html')

@app.route('/model')
def model_page():
    return render_template('model.html')

# HELPERS
def global_range_check(sensors):
    for i, val in enumerate(sensors):
        if val < (GLOBAL_MIN[i] - TOLERANCE) or val > (GLOBAL_MAX[i] + TOLERANCE):
            return False
    return True

def region_range_check(region, sensors):
    stats = REGION_MIN_MAX[region]
    for i, val in enumerate(sensors):
        if val < (stats["min"][i] - TOLERANCE) or val > (stats["max"][i] + TOLERANCE):
            return False
    return True

# SINGLE PREDICTION
@app.route('/predict', methods=['POST'])
def predict():
    if not MODEL_LOADED:
        return jsonify({'success': False, 'error': 'Model not loaded'}), 500

    try:
        data_json = request.get_json()
        sensors = data_json.get("sensors")

        if not isinstance(sensors, list) or len(sensors) != 7:
            return jsonify({'success': False, 'error': 'Exactly 7 sensor values required'}), 400

        sensors = [float(v) for v in sensors]

        # ---------- GLOBAL RANGE CHECK ----------
        if not global_range_check(sensors):
            return jsonify({
                'success': False,
                'error': 'Input values are far outside trained sensor ranges',
                'reason': 'OOD_GLOBAL'
            }), 422

        X = np.array([sensors])

        # ---------- MODEL PREDICTION ----------
        pred_idx = model.predict(X)[0]
        predicted_region = encoder.inverse_transform([pred_idx])[0]

        probabilities = model.predict_proba(X)[0]
        confidence = float(probabilities[pred_idx])

        # ---------- CONFIDENCE CHECK ----------
        if confidence < CONFIDENCE_THRESHOLD:
            return jsonify({
                'success': False,
                'error': 'Low model confidence – sample does not clearly belong to any region',
                'confidence': confidence,
                'reason': 'LOW_CONFIDENCE'
            }), 422

        # ---------- REGION RANGE CHECK ----------
        if not region_range_check(predicted_region, sensors):
            return jsonify({
                'success': False,
                'error': 'Sensor pattern does not fit predicted region envelope',
                'predicted_region': predicted_region,
                'reason': 'REGION_MISMATCH'
            }), 422

        # ---------- SUCCESS ----------
        return jsonify({
            'success': True,
            'prediction': predicted_region,
            'confidence': confidence,
            'probabilities': dict(zip(encoder.classes_, probabilities)),
            'input_sensors': sensors,
            'model': 'ExtraTrees'
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# HEALTH
@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'model_loaded': MODEL_LOADED,
        'regions': TEA_REGIONS,
        'tolerance': TOLERANCE,
        'confidence_threshold': CONFIDENCE_THRESHOLD
    })

# RUN
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)