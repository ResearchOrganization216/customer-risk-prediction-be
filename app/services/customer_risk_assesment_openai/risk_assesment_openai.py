import logging
from flask import jsonify
from cerberus import Validator
from app.utils.customer_risk_assesment_openai.risk_assesment_openai_utils import get_openai_response
from app.utils.customer_risk_assesment.risk_assesment_utils import load_xgboost_model, get_feature_importance, format_importance_for_prompt, MODEL_PATH

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        f"### **Response Format:**\n"
        f"1. **Explanation:** Justify the assigned risk level, emphasizing the most important factors without mentioning feature importance scores.\n"
        f"2. **Premium Adjustment Recommendation:** Clearly state whether the premium should increase or decrease and provide a percentage adjustment derived from your analysis, explaining the rationale behind it. Ensure the reasoning is clear and data-driven.\n"
        f"3. **Recommendations for Insurance Agents:** Suggest practical steps, such as policy adjustments or risk mitigation strategies.\n\n"
        f"Ensure the response is data-driven, easy to understand, and avoids technical jargon or raw model outputs."
    )


        # Generate response
        return get_openai_response(prompt)

    except ValueError as e:
        logger.error("Validation error: %s", e)
        return f"Validation Error: {str(e)}"
    except Exception as e:
        logger.exception("Unexpected error occurred: %s", str(e))  # Logs full error message
        return f"Unexpected error: {str(e)}" 
