import pandas as pd
import joblib
import os

# Define paths for encoders
ENCODER_PATHS = {
    'Gender': os.path.join('app/models/customer_risk_prediction', 'Gender_encoder.pkl'),
    'Vehicle Type': os.path.join('app/models/customer_risk_prediction', 'Vehicle_Type_encoder.pkl'),
    'Reason': os.path.join('app/models/customer_risk_prediction', 'Reason_encoder.pkl'),
}

# Load encoders
encoders = {col: joblib.load(path) for col, path in ENCODER_PATHS.items()}

def preprocess(input_data):
    """
    Preprocess the input data:
    - Encode categorical variables using the loaded encoders.
    - Validate input values.
    """
    df = pd.DataFrame([input_data])  # Convert input to DataFrame

    for col, encoder in encoders.items():
        if col in df:
            try:
                # Transform string inputs into their encoded values
                df[col] = encoder.transform(df[col])
            except ValueError as e:
                valid_classes = list(encoder.classes_)
                raise ValueError(f"Invalid value for {col}: {df[col][0]}. Expected one of {valid_classes}.")

    return df
