import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://postgres:password@db:5432/mydatabase')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Paths to models and encoders
    MODEL_PATH = os.path.join('app', 'models', 'xgboost_model.pkl')
    ENCODER_PATHS = {
        'Gender': os.path.join('app', 'models', 'Gender_encoder.pkl'),
        'Vehicle Type': os.path.join('app', 'models', 'Vehicle Type_encoder.pkl'),
        'Reason': os.path.join('app', 'models', 'Reason_encoder.pkl'),
    }
