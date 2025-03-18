import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key')
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:password@34.142.175.163:5432/InnoAInsure'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BUCKET_NAME = "innoainsure-bucket"
    KEY_PATH = "C:\\Users\\Sithija\\Documents\\keyfiles\\innoainsure-project-531bfaa81104.json"  # Set to an empty string in production
    PROJECT_ID = "innoainsure-project"
    SECRET_KEY = 'your-very-secret-key'

    MODEL_PATH = os.path.join('app', 'models', 'xgboost_model.pkl')
    ENCODER_PATHS = {
        'Gender': os.path.join('app', 'models', 'Gender_encoder.pkl'),
        'Vehicle Type': os.path.join('app', 'models', 'Vehicle Type_encoder.pkl'),
        'Reason': os.path.join('app', 'models', 'Reason_encoder.pkl'),
    }