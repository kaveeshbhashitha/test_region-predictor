import pickle
from sklearn.preprocessing import LabelEncoder
import numpy as np

# Load the trained model
with open("tea_models_project\\ExtraTrees_model.pkl", "rb") as file:
    model = pickle.load(file)

# Load the dataset to get the LabelEncoder (to match training labels)
import pandas as pd
data = pd.read_csv("tea_models_project\\tea_aroma_balanced.csv")
y = data.iloc[:, -1].values
encoder = LabelEncoder()
encoder.fit(y)

# ---- Provide your sensor values here ----
# Replace the numbers below with your actual sensor readings
sample_input = [5657.0,2507.0,1762.0,1007.0,3692.0,7301.0,12639.0]

# Convert to numpy array
sample_array = np.array([sample_input])

# Make prediction
pred_idx = model.predict(sample_array)[0]
pred_region = encoder.inverse_transform([pred_idx])[0]

# Optional: get probabilities if model supports it
if hasattr(model, "predict_proba"):
    probs = model.predict_proba(sample_array)[0]
    prob_dict = {region: float(prob) for region, prob in zip(encoder.classes_, probs)}
    confidence = float(probs[pred_idx])
else:
    prob_dict = {pred_region: 1.0}
    confidence = 1.0

# Print results
print("Input sensors:", sample_input)
print("Predicted Tea Region:", pred_region)
print("Prediction Confidence:", round(confidence * 100, 2), "%")
print("All Probabilities:", prob_dict)
