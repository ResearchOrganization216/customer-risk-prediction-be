import joblib
import os
from app.utils.customer_risk_prediction.preprocess import preprocess

# Load the trained model
MODEL_PATH = os.path.join('app/models/customer_risk_prediction', 'xgboost_model.pkl')
model = joblib.load(MODEL_PATH)

def predict_risk(input_data):
    """
    Predict risk percentage using the trained model.
    """
    # Preprocess input data
    processed_data = preprocess(input_data)
    
    # Predict using the loaded model
    prediction = model.predict(processed_data)

    # Convert NumPy float32 to Python float
    return float(prediction[0])
