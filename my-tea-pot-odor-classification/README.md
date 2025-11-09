# 🍃 TeaPot - Tea Region Classification System

AI-Powered Tea Origin Classification using Machine Learning and Aroma Sensor Data

## 🎯 Features

- **Interactive Tea Regions Map**: Explore Sri Lanka's 7 major tea-producing regions
- **ML-Powered Classification**: ExtraTrees model predicts tea origin from 7 sensor inputs
- **Beautiful UI**: Modern Bootstrap 5 design with smooth animations
- **Real-time Predictions**: Instant classification with confidence scores
- **Batch Processing**: Upload CSV files for multiple sample analysis
- **PDF Export**: Generate professional reports of classification results

## 📋 System Requirements

- Python 3.8+
- Modern web browser (Chrome, Firefox, Edge)
- Trained ExtraTrees model (included in `tea_models_project`)

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd my-tea-pot-odor-classification
pip install -r requirements.txt
```

### 2. Verify Model Location

Ensure your ExtraTrees model is at:
```
../tea_models_project/ExtraTrees_model.pkl
```

### 3. Run the Application

```bash
python app.py
```

The server will start on: **http://localhost:5000**

### 4. Access the Application

- **Home**: http://localhost:5000
- **Tea Regions Map**: http://localhost:5000/map
- **ML Classifier**: http://localhost:5000/model

## 🧪 Using the Classifier

### Single Sample Analysis

1. Navigate to the "Tea Classifier" page
2. Enter values for all 7 sensors (0-5V range):
   - Sensor 1: Aroma Compounds
   - Sensor 2: Phenolic Content
   - Sensor 3: Theaflavins
   - Sensor 4: Terpenoids
   - Sensor 5: Caffeine Level
   - Sensor 6: Amino Acids
   - Sensor 7: Volatile Compounds
3. Click "Analyze Sample"
4. View detailed results including:
   - Predicted region with confidence score
   - Probability distribution across all regions
   - Quality assessment
   - Chemical signature profile
   - Tea characteristics

### Batch Analysis

1. Switch to "Batch Analysis" tab
2. Upload a CSV file with columns:
   ```
   Sensor1,Sensor2,Sensor3,Sensor4,Sensor5,Sensor6,Sensor7
   2.5,3.1,2.8,3.4,2.9,3.2,2.7
   4.1,4.3,3.9,4.2,4.0,4.1,3.8
   ...
   ```
3. Preview your data
4. Analyze all samples at once

## 🗺️ Tea Regions

The system classifies tea into 7 major regions:

1. **Nuwara Eliya** - High Grown (above 1,200m)
   - Light, delicate, fragrant with floral notes
   - Known as "Champagne of Ceylon Tea"

2. **Dimbula** - High Grown (1,200-1,800m)
   - Full-bodied with crisp, strong flavor
   - Rose-like aroma

3. **Uva** - High Grown (900-1,500m)
   - Bold and brisk with distinctive flavor
   - Exceptional dry season teas

4. **Kandy** - Mid Grown (600-1,200m)
   - Strong, rich flavor with good color
   - Full-bodied character

5. **Uda Pussellawa** - High Grown (900-1,500m)
   - Medium-bodied with hint of sweetness
   - Pink-tinged liquor

6. **Ruhuna** - Low Grown (below 600m)
   - Full-bodied with strong, distinct flavor
   - Dark color

7. **Sabaragamuwa** - Low to Mid Grown (300-800m)
   - Smooth and mellow
   - Popular for blending

## 🔌 API Endpoints

### Predict Tea Region

**POST** `/predict`

Request:
```json
{
  "sensors": [2.5, 3.1, 2.8, 3.4, 2.9, 3.2, 2.7]
}
```

Response:
```json
{
  "success": true,
  "prediction": "Nuwara Eliya",
  "confidence": 0.92,
  "probabilities": {
    "Nuwara Eliya": 0.92,
    "Dimbula": 0.05,
    "Uva": 0.02,
    ...
  },
  "model": "ExtraTrees",
  "input_sensors": [...]
}
```

### Health Check

**GET** `/health`

Response:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_type": "ExtraTrees",
  "sensors_required": 7,
  "regions": 7
}
```

## 📁 Project Structure

```
my-tea-pot-odor-classification/
├── app.py                      # Flask backend
├── requirements.txt            # Python dependencies
├── templates/
│   ├── index.html             # Home page
│   ├── map.html               # Interactive tea regions map
│   └── model.html             # ML classification interface
├── assets/
│   ├── css/
│   │   └── main.css          # Main stylesheet
│   ├── js/
│   │   ├── main.js           # UI interactions
│   │   └── actions.js        # ML prediction logic
│   ├── img/                  # Images and icons
│   └── vendor/               # Bootstrap, libraries
└── README.md                  # This file
```

## 🎨 Design

- **Framework**: Bootstrap 5.3.3
- **Fonts**: Roboto, Nunito, Poppins
- **Color Scheme**: 
  - Primary: #4154f1
  - Heading: #012970
  - Accent: Blue gradient theme
- **Animations**: AOS (Animate On Scroll)
- **Icons**: Bootstrap Icons

## 🧠 Machine Learning Model

- **Algorithm**: ExtraTrees Classifier
- **Input Features**: 7 MOS (Metal Oxide Semiconductor) sensors
- **Output**: 7 tea regions
- **Training Data**: Balanced tea aroma dataset
- **Accuracy**: ~95% (varies by region)

## 🔧 Troubleshooting

### Model Not Loading

If you see "Model not found" warning:
1. Check model path in `app.py`
2. Verify ExtraTrees model exists
3. Ensure pickle compatibility

The system will work in "mock mode" for testing even without the model.

### Port Already in Use

If port 5000 is busy:
```bash
python app.py --port 8080
```

Or modify `app.py`:
```python
app.run(host='0.0.0.0', port=8080, debug=True)
```

### CORS Errors

Already handled by `flask-cors`. If issues persist, check browser console.

## 📊 Performance

- **Prediction Time**: < 100ms per sample
- **Batch Processing**: ~50 samples per second
- **Model Size**: ~5MB
- **Memory Usage**: ~200MB

## 🚀 Deployment

### Development
```bash
python app.py
```

### Production (with Gunicorn)
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Docker (Optional)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

## 👨‍💻 Developer

**M.A.B. Kaveesh**
- University of Kelaniya
- Department of Computer Science
- Email: kaveesh-ps20021@uok.ac.lk

## 📄 License

Academic Project - University of Kelaniya
For educational and research purposes

## 🙏 Acknowledgments

- Sri Lanka Tea Board for regional data
- Bootstrap Made for design inspiration
- University of Kelaniya - Faculty of Science
- Department of Computer Science & Data Communication

---

**Made with ☕ and 🍃 for Ceylon Tea Research**

