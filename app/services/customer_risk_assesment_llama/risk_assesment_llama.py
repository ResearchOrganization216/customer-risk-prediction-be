import os
import logging
from flask import jsonify
from app.utils.customer_risk_assesment_llama.risk_assesment_utils_llama import get_groq_client
from app.utils.customer_risk_assesment.risk_assesment_utils import load_xgboost_model, get_feature_importance, format_importance_for_prompt, MODEL_PATH
from cerberus import Validator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = get_groq_client()

# Input validation schema
schema = {
    'age': {'type': 'integer', 'min': 0},
    'gender': {'type': 'string', 'allowed': ['Male', 'Female', 'Other']},
    'vehicleType': {'type': 'string', 'allowed': ['Private', 'Hiring']},
    'totalClaims': {'type': 'integer', 'min': 0},
    'reason': {'type': 'string'},
    'premium': {'type': 'number', 'min': 0},
    'claimAmount': {'type': 'number', 'min': 0},
    'insuredPeriod': {'type': 'integer', 'min': 0},
    'riskPercentage': {'type': 'number', 'min': 0, 'max': 100},
}

def validate_input(data):
    """Validate input data using the defined schema."""
    v = Validator(schema)
    if not v.validate(data):
        raise ValueError(f"Input validation failed: {v.errors}")

def generate_content_with_prompt(data):
    try:
        # Validate input
        validate_input(data)

        # Load the model and get feature importance
        model = load_xgboost_model(MODEL_PATH)
        feature_importance = get_feature_importance(model)
        formatted_importance = format_importance_for_prompt(feature_importance)

        # Build the prompt
        prompt = (
            f"You are an insurance risk assessment expert. Based on the following features and their relative importance, "
            f"provide a concise explanation of the calculated risk percentage ({data['riskPercentage']}%). "
            f"Focus on business insights to explain how each feature impacts the risk calculation, "
            f"emphasizing the most influential factors.\n\n"
            f"### Features and Importance:\n"
            f"{formatted_importance}\n\n"
            f"### Details for the specific case:\n"
            f"- **Age**: {data['age']}\n"
            f"- **Gender**: {data['gender']}\n"
            f"- **Vehicle Type**: {data['vehicleType']}\n"
            f"- **Total Claims**: {data['totalClaims']}\n"
            f"- **Reason for Claim**: {data['reason']}\n"
            f"- **Premium (LKR)**: {data['premium']}\n"
            f"- **Claim Amount (LKR)**: {data['claimAmount']}\n"
            f"- **Insured Period (Years)**: {data['insuredPeriod']}\n\n"
            f"Provide a concise business-focused analysis of how these factors contribute to the risk percentage."
            f"Avoid technical jargon and focus on actionable insights for the insurance company non-technical staff.\n\n"
            f"Give recommendations for risk mitigation strategies based on premium and claim amount.\n\n"
            f"Use 5-6 sentences to summarize the key points.\n"
            f"All these explations should be relevant to the Sri Lankan Vehicle Insurance industry."
        )

        # Generate analysis
        analysis = client.chat.completions.create(
            messages=[
                {"role": "user", "content": "You are a Specialist in the Vehicle Insurance industry"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1024,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            model="llama-3.3-70b-versatile", #llama-3.3-70b-versatile #llama-3.1-8b-instant
        )
        return analysis.choices[0].message.content

    except ValueError as e:
        logger.error("Validation error: %s", e)
        return jsonify({"error": str(e)}), 400
    except FileNotFoundError as e:
        logger.error("File not found: %s", e)
        return jsonify({"error": "A required file is missing. Please contact support."}), 500
    except KeyError as e:
        logger.error("Key error: Missing key in input data: %s", e)
        return jsonify({"error": "The input data is incomplete. Please check the request payload."}), 400
    except Exception as e:
        logger.exception("An unexpected error occurred.")
        return jsonify({"error": "An unexpected error occurred. Please try again later."}), 500
