import logging
from flask import jsonify
from cerberus import Validator
from app.utils.customer_risk_assesment_openai.risk_assesment_openai_utils import get_openai_response

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

        # Build the prompt
        prompt = (
            f"You are an insurance risk assessment expert. Based on the following details, "
            f"explain the risk percentage ({data['riskPercentage']}%) with actionable insights. "
            f"Avoid technical jargon and make it relevant to Sri Lanka’s insurance industry.\n\n"
            f"- Age: {data['age']}\n"
            f"- Gender: {data['gender']}\n"
            f"- Vehicle Type: {data['vehicleType']}\n"
            f"- Total Claims: {data['totalClaims']}\n"
            f"- Reason for Claim: {data['reason']}\n"
            f"- Premium (LKR): {data['premium']}\n"
            f"- Claim Amount (LKR): {data['claimAmount']}\n"
            f"- Insured Period (Years): {data['insuredPeriod']}\n\n"
            f"Provide 5-6 sentences summarizing the key points and risk mitigation strategies."
        )

        # Generate response
        return get_openai_response(prompt)

    except ValueError as e:
        logger.error("Validation error: %s", e)
        return f"Validation Error: {str(e)}"
    except Exception as e:
        logger.exception("Unexpected error occurred: %s", str(e))  # Logs full error message
        return f"Unexpected error: {str(e)}" 
