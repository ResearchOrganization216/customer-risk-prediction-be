from flask import Blueprint, request, jsonify
from app.services.customer_risk_assesment_openai.risk_assesment_openai import generate_content_with_prompt

risk_assessment_openai_bp = Blueprint('risk_assessment_openai_bp', __name__)

@risk_assessment_openai_bp.route('/risk-assessment-openai', methods=['POST'])
def generate_content_route():
    data = request.json
    required_fields = ['age', 'gender', 'vehicleType', 'totalClaims', 'reason', 'premium', 'claimAmount', 'insuredPeriod', 'riskPercentage']

    # Validate required fields
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({"error": f"Missing fields: {', '.join(missing_fields)}"}), 400

    try:
        output = generate_content_with_prompt(data)
        if "Error" in output:
            return jsonify({"error": output}), 400
        return jsonify({"analysis": output})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
