from flask import Blueprint, request, jsonify
from app.services.customer_risk_prediction.customer_risk_service import predict_risk

customer_risk_bp = Blueprint('customer_risk', __name__)

@customer_risk_bp.route('/customer-risk', methods=['POST'])
def customer_risk_prediction():
    try:
        # Parse JSON input
        input_data = request.get_json()

        transformed_data = {
            "Age": input_data.get("age"),
            "Gender": input_data.get("gender"),
            "Vehicle Type": input_data.get("vehicleType"),
            "Total Claims": input_data.get("totalClaims"),
            "Reason": input_data.get("reason"),
            "Premium (LKR)": input_data.get("premium"),
            "Claim Amount (LKR)": input_data.get("claimAmount"),
            "Insured Period (Years)": input_data.get("insuredPeriod")
        }

        # Perform prediction
        prediction = predict_risk(transformed_data)

        # Return prediction as JSON
        return jsonify({'Risk_Percentage': prediction})
    except Exception as e:
        # Return error message
        return jsonify({'error': str(e)})
