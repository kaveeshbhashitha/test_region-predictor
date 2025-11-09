"""
Flask Backend for Tea Region Classification
Connects to ExtraTrees ML Model
Only accepts real user inputs - NO mock data
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from sklearn.preprocessing import LabelEncoder
import numpy as np
import pandas as pd
import pickle
import os
import io

app = Flask(__name__)
CORS(app)

# Load the trained ExtraTrees model
MODEL_PATH = 'tea_models_project\\ExtraTrees_model.pkl'

try:
    with open(MODEL_PATH, 'rb') as f:
        model = pickle.load(f)
    print("✅ ExtraTrees model loaded successfully!")
    MODEL_LOADED = True
except FileNotFoundError:
    print(f"⚠️ Model not found at: {MODEL_PATH}")
    print("⚠️ Please ensure model file exists at the specified path")
    MODEL_LOADED = False
except Exception as e:
    print(f"⚠️ Error loading model: {e}")
    MODEL_LOADED = False

data = pd.read_csv("tea_models_project\\tea_aroma_balanced.csv")
y = data.iloc[:, -1].values  # assuming last column is label
encoder = LabelEncoder()
encoder.fit(y)

# Tea regions (must match your training labels)
TEA_REGIONS = [
    'Nuwara Eliya',
    'Dimbula',
    'Uva',
    'Kandy',
    'Uda Pussellawa',
    'Ruhuna',
    'Sabaragamuwa'
]

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/map')
def map_page():
    """Tea regions map page"""
    return render_template('map.html')

@app.route('/model')
def model_page():
    """ML model page"""
    return render_template('model.html')

@app.route('/predict', methods=['POST'])
def predict():
    """
    Predict tea region from 7 sensor values (USER INPUT ONLY)
    
    Expected JSON:
    {
        "sensors": [sensor1, sensor2, sensor3, sensor4, sensor5, sensor6, sensor7]
    }
    """
    # Check if model is loaded
    if not MODEL_LOADED:
        return jsonify({
            'success': False,
            'error': 'Model not loaded. Please ensure ExtraTrees_model.pkl exists at the correct path.'
        }), 500
    
    try:
        data = request.get_json()
        
        if 'sensors' not in data:
            return jsonify({'error': 'Missing "sensors" field'}), 400
        
        sensor_data = data['sensors']
        
        # Validate input
        if not isinstance(sensor_data, list):
            return jsonify({'error': 'Sensors must be an array'}), 400
        
        if len(sensor_data) != 7:
            return jsonify({'error': f'Expected 7 sensor values, got {len(sensor_data)}'}), 400
        
        # Validate each sensor value is a number
        try:
            sensor_data = [float(val) for val in sensor_data]
        except (ValueError, TypeError):
            return jsonify({'error': 'All sensor values must be numbers'}), 400
        
        # Convert to numpy array
        X = np.array([sensor_data])
        
        # Make REAL prediction using ExtraTrees model
        prediction_idx = model.predict(X)[0]
        predicted_region = encoder.inverse_transform([prediction_idx])[0]
        
        # Get probabilities
        if hasattr(model, 'predict_proba'):
            probabilities = model.predict_proba(X)[0]
            prob_dict = {region: float(prob) for region, prob in zip(encoder.classes_, probabilities)}
            confidence = float(probabilities[prediction_idx])
        else:
            prob_dict = {predicted_region: 1.0}
            confidence = 1.0
        
        # Return results
        return jsonify({
            'success': True,
            'prediction': predicted_region,
            'confidence': confidence,
            'probabilities': prob_dict,
            'model': 'ExtraTrees',
            'input_sensors': sensor_data
        })
    
    except Exception as e:
        print(f"Error during prediction: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/predict-batch', methods=['POST'])
def predict_batch():
    """
    Batch prediction from CSV file (USER FILE UPLOAD ONLY)
    
    Expected CSV format:
    Sensor1,Sensor2,Sensor3,Sensor4,Sensor5,Sensor6,Sensor7
    2.5,3.1,2.8,3.4,2.9,3.2,2.7
    4.1,4.3,3.9,4.2,4.0,4.1,3.8
    ...
    """
    # Check if model is loaded
    if not MODEL_LOADED:
        return jsonify({
            'success': False,
            'error': 'Model not loaded. Please ensure ExtraTrees_model.pkl exists at the correct path.'
        }), 500
    
    try:
        # Check if file is provided
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.endswith('.csv'):
            return jsonify({'error': 'Only CSV files are accepted'}), 400
        
        # Read CSV file
        csv_content = file.read().decode('utf-8')
        df = pd.read_csv(io.StringIO(csv_content))
        
        # Validate CSV columns
        expected_columns = ['Sensor1', 'Sensor2', 'Sensor3', 'Sensor4', 'Sensor5', 'Sensor6', 'Sensor7']
        
        # Check if columns exist (case-insensitive)
        df.columns = df.columns.str.strip()
        column_mapping = {col.lower(): col for col in df.columns}
        
        missing_columns = []
        for expected_col in expected_columns:
            if expected_col.lower() not in column_mapping:
                missing_columns.append(expected_col)
        
        if missing_columns:
            return jsonify({
                'error': f'Missing required columns: {", ".join(missing_columns)}',
                'expected': expected_columns
            }), 400
        
        # Limit batch size
        if len(df) > 100:
            return jsonify({'error': 'Maximum 100 samples per batch'}), 400
        
        if len(df) == 0:
            return jsonify({'error': 'CSV file is empty'}), 400
        
        # Extract sensor data (case-insensitive column matching)
        sensor_data = []
        for expected_col in expected_columns:
            actual_col = next(col for col in df.columns if col.lower() == expected_col.lower())
            sensor_data.append(df[actual_col].values)
        
        X = np.array(sensor_data).T
        
        # Validate all values are numeric
        if not np.issubdtype(X.dtype, np.number):
            return jsonify({'error': 'All sensor values must be numeric'}), 400
        
        # Make REAL predictions
        predictions = model.predict(X)
        
        # Get probabilities
        if hasattr(model, 'predict_proba'):
            probabilities = model.predict_proba(X)
        else:
            probabilities = None
        
        # Format results
        results = []
        for i, pred_idx in enumerate(predictions):
            predicted_region = TEA_REGIONS[pred_idx]
            
            result = {
                'sample_index': i + 1,
                'prediction': predicted_region,
                'input_sensors': X[i].tolist()
            }
            
            if probabilities is not None:
                result['confidence'] = float(probabilities[i][pred_idx])
                result['probabilities'] = {
                    region: float(prob) for region, prob in zip(TEA_REGIONS, probabilities[i])
                }
            
            results.append(result)
        
        # Return batch results
        return jsonify({
            'success': True,
            'total_samples': len(results),
            'model': 'ExtraTrees',
            'results': results
        })
    
    except pd.errors.ParserError:
        return jsonify({'error': 'Invalid CSV format'}), 400
    except Exception as e:
        print(f"Error during batch prediction: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': MODEL_LOADED,
        'model_type': 'ExtraTrees',
        'sensors_required': 7,
        'regions': len(TEA_REGIONS)
    })

if __name__ == '__main__':
    print("=" * 60)
    print("🍃 TeaPot - Tea Region Classification System")
    print("=" * 60)
    print(f"Model Status: {'✅ Loaded' if MODEL_LOADED else '❌ NOT LOADED'}")
    if not MODEL_LOADED:
        print(f"⚠️  WARNING: Model file not found!")
        print(f"⚠️  Path: {MODEL_PATH}")
        print(f"⚠️  Predictions will FAIL until model is loaded")
    print(f"Model Type: ExtraTrees")
    print(f"Sensors Required: 7")
    print(f"Tea Regions: {len(TEA_REGIONS)}")
    print("=" * 60)
    print("Endpoints:")
    print("  POST /predict        - Single sample prediction")
    print("  POST /predict-batch  - Batch CSV file prediction")
    print("  GET  /health         - Health check")
    print("=" * 60)
    print("Starting server on http://localhost:5000")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=True)