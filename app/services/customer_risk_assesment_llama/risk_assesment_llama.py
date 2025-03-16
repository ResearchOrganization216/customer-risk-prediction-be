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
        f"You are an insurance risk assessment expert. Based on the following details, "
        f"explain why the risk percentage is {data['riskPercentage']}%. "
        f"Use the feature importance data internally to justify your explanation and focus on the most influential factors, "
        f"Feature importance data: {formatted_importance}, "
        f"but do NOT display the importance scores in the response.\n\n"
        f"**Customer Details:**\n"
        f"- Age: {data['age']}\n"
        f"- Gender: {data['gender']}\n"
        f"- Vehicle Type: {data['vehicleType']}\n"
        f"- Total Claims: {data['totalClaims']}\n"
        f"- Reason for Claim: {data['reason']}\n"
        f"- Premium (LKR): {data['premium']}\n"
        f"- Claim Amount (LKR): {data['claimAmount']}\n"
        f"- Insured Period (Years): {data['insuredPeriod']}\n\n"
        f"**Additional Considerations:**\n"
        f"- Calculate the necessary premium adjustment based on the claim-to-premium ratio, total claims, and insured period, "
        f"but provide a clear explanation of how the adjustment is derived without referencing technical details.\n"
        f"- Make the explanation practical and relevant to Sri Lanka’s insurance market, using straightforward language.\n\n"
        f"**Response Format:**\n"
        f"🚀. **Explanation:** Justify the assigned risk level, emphasizing the most important factors without mentioning feature importance scores.\n"
        f"🚀. **Premium Adjustment Recommendation:** Clearly state whether the premium should increase or decrease and provide a percentage adjustment derived from your analysis, explaining the rationale behind it. Ensure the reasoning is clear and data-driven.\n"
        f"🚀. **Recommendations for Insurance Agents:** Suggest practical steps, such as policy adjustments or risk mitigation strategies.\n\n"
        f"Ensure the response is data-driven, easy to understand, and avoids technical jargon or raw model outputs."
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
