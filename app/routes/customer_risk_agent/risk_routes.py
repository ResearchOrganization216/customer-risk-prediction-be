from flask import Blueprint, request, jsonify
from app.agents.customer_risk_agent.risk_agent import RiskAgent
from app.utils.customer_risk_agent.models import CustomerData
from app.utils.customer_risk_agent.exception import RiskAPIError, WorkflowError
from pydantic import ValidationError
import logging

logger = logging.getLogger(__name__)

risk_bp = Blueprint('risk', __name__)

@risk_bp.route('/analyze', methods=['POST'])
def analyze_risk():
    try:
        # Validate the input data
        data = request.get_json()
        if not data:
            return jsonify({
                "error": "Invalid request",
                "message": "Request body is empty"
            }), 400
            
        CustomerData(**data)  # Validate but don't store the model
        
        # Initialize the workflow
        workflow = RiskAgent.create_workflow()
        
        # Initialize the state
        initial_state = {
            "risk_data": data,
            "assessment_data": {},
            "output": {},
            "path": "",
            "actions_required": [],
            "errors": []
        }
        
        # Run the workflow
        result = workflow.invoke(initial_state)
        
        # Check for errors in the result
        if result["output"].get("status") == "error":
            return jsonify(result["output"]), 500
            
        return jsonify(result["output"])
        
    except ValidationError as e:
        logger.error(f"Validation error: {str(e)}")
        return jsonify({
            "error": "Validation error",
            "details": e.errors()
        }), 400
    except RiskAPIError as e:
        logger.error(f"Risk API error: {str(e)}")
        return jsonify({
            "error": "Risk API error",
            "message": str(e),
            "status_code": getattr(e, "status_code", None)
        }), getattr(e, "status_code", 500)
    except WorkflowError as e:
        logger.error(f"Workflow error: {str(e)}")
        return jsonify({
            "error": "Workflow error",
            "message": str(e),
            "state": getattr(e, "state", None)
        }), 500
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "message": str(e),
            "type": type(e).__name__
        }), 500