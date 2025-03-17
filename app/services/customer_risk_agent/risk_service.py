from typing import Dict
from app.utils.customer_risk_agent.tools import calculate_risk, get_risk_assessment

class RiskService:
    @staticmethod
    def process_risk_analysis(customer_data: Dict) -> Dict:
        # Calculate risk
        risk_result = calculate_risk(customer_data)
        customer_data["riskPercentage"] = risk_result["riskPercentage"]
        
        # Get assessment
        assessment_result = get_risk_assessment(customer_data)
        
        # Format output
        output = {
            "riskPercentage": customer_data["riskPercentage"],
            "explanation": assessment_result["explanation"],
            #"originalData": customer_data
        }
        
        return output