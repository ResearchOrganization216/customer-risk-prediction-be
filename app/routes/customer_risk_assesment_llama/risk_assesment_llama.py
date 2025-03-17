from flask import Blueprint, request, jsonify
from app.services.customer_risk_assesment_llama.risk_assesment_llama import generate_content_with_prompt

risk_assesment_llama_bp = Blueprint('risk_assesment_llama_bp', __name__)

@risk_assesment_llama_bp.route('/risk-assessment-llama', methods=['POST'])
def generate_content_route():
    data = request.json
    required_fields = [
        'age', 'gender', 'vehicleType', 'totalClaims', 'reason', 'premium', 'claimAmount', 'insuredPeriod', 'riskPercentage'
    ]

    # Validate required fields
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({"error": f"Missing fields: {', '.join(missing_fields)}"}), 400

    try:
        # Generate content using the service
        output = generate_content_with_prompt(data)
        return jsonify({"analysis": output})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
