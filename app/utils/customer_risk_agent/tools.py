from typing import Dict
import requests
from requests.exceptions import RequestException
from app.utils.customer_risk_agent.exception import RiskCalculationError, AssessmentAPIError
import logging
import backoff

logger = logging.getLogger(__name__)

def handle_api_error(response: requests.Response, error_class: Exception) -> None:
    """Handle API error responses"""
    try:
        error_detail = response.json()
    except ValueError:
        error_detail = response.text

    logger.error(f"API Error: {error_detail}")
    raise error_class(
        message=f"API request failed with status {response.status_code}",
        status_code=response.status_code,
        response=error_detail
    )

@backoff.on_exception(
    backoff.expo,
    (RequestException, RiskCalculationError),
    max_tries=3,
    max_time=30
)
def call_risk_api(data: Dict) -> Dict:
    """
    Calculate customer risk by sending data to the risk calculation endpoint
    with retry logic and error handling
    """
    try:
        response = requests.post(
            "http://127.0.0.1:5000/api/customer-risk",
            json=data,
            timeout=10
        )
        
        if response.status_code != 200:
            handle_api_error(response, RiskCalculationError)
            
        result = response.json()
        if "Risk_Percentage" not in result:
            raise RiskCalculationError(
                "Invalid response format: missing Risk_Percentage",
                response=result
            )
            
        return {"riskPercentage": result["Risk_Percentage"]}
        
    except RequestException as e:
        logger.error(f"Risk API request failed: {str(e)}")
        raise RiskCalculationError(f"Failed to connect to Risk API: {str(e)}")

@backoff.on_exception(
    backoff.expo,
    (RequestException, AssessmentAPIError),
    max_tries=3,
    max_time=30
)
def call_assessment_api(data: Dict) -> Dict:
    """
    Get risk assessment explanation with retry logic and error handling
    """
    try:
        response = requests.post(
            "http://127.0.0.1:5000/api/risk-assessment-llama",
            json=data,
            timeout=10
        )
        
        if response.status_code != 200:
            handle_api_error(response, AssessmentAPIError)
            
        result = response.json()
        if "analysis" not in result:
            raise AssessmentAPIError(
                "Invalid response format: missing analysis",
                response=result
            )
            
        return {"explanation": result["analysis"]}
        
    except RequestException as e:
        logger.error(f"Assessment API request failed: {str(e)}")
        raise AssessmentAPIError(f"Failed to connect to Assessment API: {str(e)}")