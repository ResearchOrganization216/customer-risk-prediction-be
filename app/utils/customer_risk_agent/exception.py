from typing import Optional, Any, Dict

class RiskAPIError(Exception):
    """Base exception for Risk API related errors"""
    def __init__(self, message: str, status_code: Optional[int] = None, response: Optional[Dict] = None):
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(self.message)

class RiskCalculationError(RiskAPIError):
    """Raised when risk calculation fails"""
    pass

class AssessmentAPIError(RiskAPIError):
    """Raised when risk assessment fails"""
    pass

class WorkflowError(Exception):
    """Raised when workflow execution fails"""
    def __init__(self, message: str, state: Optional[Dict] = None):
        self.message = message
        self.state = state
        super().__init__(self.message)