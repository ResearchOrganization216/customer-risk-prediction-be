import logging
import pickle
import xgboost as xgb
import os

# Path to the XGBoost model
MODEL_PATH = os.path.join(os.getcwd(), "app", "models", "customer_risk_prediction", "xgboost_model.pkl")

def load_xgboost_model(model_path=MODEL_PATH):
    try:
        with open(model_path, "rb") as model_file:
            model = pickle.load(model_file)
        return model
    except Exception as e:
        logging.error(f"Error loading XGBoost model: {e}")
        raise ValueError("Failed to load the XGBoost model.")

def get_feature_importance(model):
    try:
        importance = model.get_booster().get_score(importance_type="weight")
        sorted_importance = sorted(importance.items(), key=lambda x: x[1], reverse=True)
        return sorted_importance
    except Exception as e:
        logging.error(f"Error extracting feature importance: {e}")
        raise ValueError("Failed to retrieve feature importance.")

def format_importance_for_prompt(feature_importance):
    formatted = []
    for feature, score in feature_importance:
        formatted.append(f"**{feature}** - Importance Score: {score}.")
    return "\n".join(formatted)
