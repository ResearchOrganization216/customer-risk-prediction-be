from typing import Dict, TypedDict, Literal, Optional
from langgraph.graph import StateGraph, END
from app.utils.customer_risk_agent.tools import call_risk_api, call_assessment_api
from app.utils.customer_risk_agent.exception import RiskCalculationError, AssessmentAPIError, WorkflowError
import logging

logger = logging.getLogger(__name__)

class AgentState(TypedDict):
    risk_data: Dict
    assessment_data: Dict
    output: Dict
    path: str
    actions_required: list
    errors: Optional[list]  # Track any errors that occur

class RiskAgent:
    @staticmethod
    def calculate_risk_node(state: AgentState) -> AgentState:
        """Calculate initial risk with error handling"""
        try:
            risk_result = call_risk_api(state["risk_data"])
            state["risk_data"]["riskPercentage"] = risk_result["riskPercentage"]
        except RiskCalculationError as e:
            logger.error(f"Risk calculation failed: {str(e)}")
            if not state.get("errors"):
                state["errors"] = []
            state["errors"].append({
                "step": "risk_calculation",
                "error": str(e),
                "status_code": getattr(e, "status_code", None)
            })
            # Set a default risk percentage for fallback
            state["risk_data"]["riskPercentage"] = 0.0  # Middle ground as fallback
        return state

    @staticmethod
    def evaluate_risk_level(state: AgentState) -> Literal["high_risk", "medium_risk", "low_risk", "error"]:
        """Determine which path to take, including error handling"""
        if state.get("errors"):
            return "error"
            
        try:
            risk_percentage = state["risk_data"]["riskPercentage"]
            total_claims = state["risk_data"]["totalClaims"]
            
            if risk_percentage > 70:
                return "high_risk"
            elif risk_percentage > 30 and risk_percentage <= 70:
                return "medium_risk"
            else:
                return "low_risk"
        except KeyError as e:
            logger.error(f"Missing required data for risk evaluation: {str(e)}")
            if not state.get("errors"):
                state["errors"] = []
            state["errors"].append({
                "step": "risk_evaluation",
                "error": f"Missing required data: {str(e)}"
            })
            return "error"

    @staticmethod
    def handle_error(state: AgentState) -> AgentState:
        """Handle error cases"""
        state["path"] = "error"
        state["actions_required"] = [
            "Review error logs",
            "Contact technical support",
            "Manual risk assessment required"
        ]
        return state
    
    #LLM Assesment with enhanced fallbacks
    @staticmethod
    def perform_llm_assessment(state: AgentState) -> AgentState:
        """Dedicated node for LLM-based risk assessment with smart fallbacks"""
        try:
            # Attempt LLM assessment first
            assessment_result = call_assessment_api(state["risk_data"])
            state["assessment_data"] = assessment_result
            
            state["actions_required"].extend([
                "Review AI assessment results",
                "Validate AI recommendations"
            ])
            
        except AssessmentAPIError as e:
            logger.error(f"LLM assessment failed: {str(e)}")
            if not state.get("errors"):
                state["errors"] = []
            state["errors"].append({
                "step": "llm_assessment",
                "error": str(e),
                "status_code": getattr(e, "status_code", None)
            })
            
            # Generate a structured fallback assessment based on available data
            risk_data = state["risk_data"]
            risk_level = state.get("path", "unknown")
            vehicle_type = state.get("vehicle_type", "unknown")
            
            # Build a detailed fallback assessment
            fallback_explanation = []
            
            # Risk level assessment
            fallback_explanation.append(f"Risk Level: {risk_level.replace('_', ' ').title()}")
            
            # Claims analysis
            if "totalClaims" in risk_data:
                claims_assessment = (
                    "High claim frequency" if risk_data["totalClaims"] > 3
                    else "Moderate claim frequency" if risk_data["totalClaims"] > 1
                    else "Low claim frequency"
                )
                fallback_explanation.append(f"Claims Status: {claims_assessment}")
            
            # Vehicle type considerations
            vehicle_specifics = {
                "hiring": "Hiring vehicle requires additional licensing and fleet history verification.",
                "private": "Personal vehicle usage patterns should be validated."
            }
            fallback_explanation.append(vehicle_specifics.get(vehicle_type, "Vehicle type verification needed."))
            
            # Age-based assessment
            if "age" in risk_data:
                age = risk_data["age"]
                age_assessment = (
                    "Driver falls in younger age bracket requiring additional review."
                    if age < 25 else
                    "Driver falls in mature driver category."
                    if age < 65 else
                    "Senior driver category requires specialized assessment."
                )
                fallback_explanation.append(age_assessment)
            
            # Premium vs Claims ratio analysis
            if all(key in risk_data for key in ["premium", "claimAmount"]):
                claim_to_premium_ratio = risk_data["claimAmount"] / risk_data["premium"]
                ratio_assessment = (
                    "Claim amount significantly exceeds premium level."
                    if claim_to_premium_ratio > 2 else
                    "Claim amount is proportional to premium level."
                    if claim_to_premium_ratio <= 2 else
                    "Claim amount is below premium level."
                )
                fallback_explanation.append(ratio_assessment)
            
            # Insurance period assessment
            if "insuredPeriod" in risk_data:
                period_assessment = (
                    "New policy requiring standard monitoring."
                    if risk_data["insuredPeriod"] < 12 else
                    "Established policy with historical data available."
                )
                fallback_explanation.append(period_assessment)
            
            # Join all assessments with proper formatting
            detailed_assessment = " ".join(fallback_explanation)
            
            state["assessment_data"] = {
                "explanation": detailed_assessment,
                "fallback": True  # Flag to indicate this is a fallback assessment
            }
            
            # Add fallback-specific actions
            state["actions_required"].extend([
                "Manual verification of assessment",
                "Review system generated insights",
                "Schedule follow-up assessment when LLM service is available"
            ])
            
        return state
    @staticmethod
    def assess_commercial_vehicle(state: AgentState) -> AgentState:
        """Special assessment for hiring vehicles with error handling"""
        try:
            #assessment_result = call_assessment_api(state["risk_data"])
            #state["assessment_data"] = assessment_result
            state["vehicle_type"] = "hiring"
            state["actions_required"].extend([
                "Verify hiring license",
                "Check fleet history",
                "Review business usage patterns"
            ])
        except AssessmentAPIError as e:
            logger.error(f"Commercial vehicle assessment failed: {str(e)}")
            if not state.get("errors"):
                state["errors"] = []
            state["errors"].append({
                "step": "commercial_assessment",
                "error": str(e),
                "status_code": getattr(e, "status_code", None)
            })
            # Add fallback assessment
            state["assessment_data"] = {
                "explanation": "Assessment service unavailable. Manual review required."
            }
        return state

    @staticmethod
    def format_output(state: AgentState) -> AgentState:
        """Format final output with error handling"""
        try:
            risk_percent = state["risk_data"].get("riskPercentage", 0)
            assessment = state["assessment_data"].get("explanation", "Assessment unavailable")
            
            state["output"] = {
                "riskPercentage": risk_percent,
                "explanation": assessment,
                "riskLevel": state.get("path", "unknown"),
                "requiredActions": state.get("actions_required", []),
                "status": "error" if state.get("errors") else "success",
                "errors": state.get("errors", [])
            }
        except Exception as e:
            logger.error(f"Error formatting output: {str(e)}")
            state["output"] = {
                "status": "error",
                "error": "Failed to format output",
                "message": str(e)
            }
        return state
    
    @staticmethod
    def handle_high_risk(state: AgentState) -> AgentState:
        """Handle high-risk cases with error handling"""
        try:
            state["actions_required"] = [
                "Schedule immediate review",
                "Request additional documentation",
                "Flag for supervisor attention",
                "Conduct detailed claims history analysis",
                "Verify all submitted documentation"
            ]
            state["path"] = "high_risk"
        except Exception as e:
            logger.error(f"Error in high risk handling: {str(e)}")
            if not state.get("errors"):
                state["errors"] = []
            state["errors"].append({
                "step": "high_risk_handling",
                "error": str(e)
            })
        return state

    @staticmethod
    def handle_medium_risk(state: AgentState) -> AgentState:
        """Handle medium-risk cases with error handling"""
        try:
            state["actions_required"] = [
                "Schedule routine review",
                "Monitor claim frequency",
                "Review policy terms",
                "Check payment history"
            ]
            state["path"] = "medium_risk"
        except Exception as e:
            logger.error(f"Error in medium risk handling: {str(e)}")
            if not state.get("errors"):
                state["errors"] = []
            state["errors"].append({
                "step": "medium_risk_handling",
                "error": str(e)
            })
        return state

    @staticmethod
    def handle_low_risk(state: AgentState) -> AgentState:
        """Handle low-risk cases with error handling"""
        try:
            state["actions_required"] = [
                "Standard processing",
                "Consider loyalty rewards",
                "Schedule annual review",
                "Check for discount eligibility"
            ]
            state["path"] = "low_risk"
        except Exception as e:
            logger.error(f"Error in low risk handling: {str(e)}")
            if not state.get("errors"):
                state["errors"] = []
            state["errors"].append({
                "step": "low_risk_handling",
                "error": str(e)
            })
        return state

    @staticmethod
    def handle_error(state: AgentState) -> AgentState:
        """Handle error cases"""
        try:
            state["path"] = "error"
            state["actions_required"] = [
                "Review error logs",
                "Contact technical support",
                "Manual risk assessment required",
                "Escalate to supervisor",
                "Document system state at failure"
            ]
        except Exception as e:
            logger.error(f"Error in error handling: {str(e)}")
            if not state.get("errors"):
                state["errors"] = []
            state["errors"].append({
                "step": "error_handling",
                "error": str(e)
            })
        return state

    @staticmethod
    def check_vehicle_type(state: AgentState) -> Literal["hiring", "private"]:
        """Route based on vehicle type for different assessment rules"""
        try:
            return "hiring" if state["risk_data"]["vehicleType"].lower() == "hiring" else "private"
        except Exception as e:
            logger.error(f"Error in vehicle type checking: {str(e)}")
            # Default to private vehicle type if there's an error
            return "private"

    @staticmethod
    def assess_private_vehicle(state: AgentState) -> AgentState:
        """Standard assessment for private vehicles"""
        try:
            #assessment_result = call_assessment_api(state["risk_data"])
            #state["assessment_data"] = assessment_result
            state["vehicle_type"] = "private"
            # Add private vehicle specific checks
            state["actions_required"].extend([
                "Verify personal usage",
                "Check driver history",
                "Review insurance history",
                "Validate license status"
            ])
        except AssessmentAPIError as e:
            logger.error(f"Private vehicle assessment failed: {str(e)}")
            if not state.get("errors"):
                state["errors"] = []
            state["errors"].append({
                "step": "private_assessment",
                "error": str(e),
                "status_code": getattr(e, "status_code", None)
            })
            # Add fallback assessment
            state["assessment_data"] = {
                "explanation": "Assessment service unavailable. Manual review required."
            }
        return state
    @classmethod
    def create_workflow(cls) -> StateGraph:
        """Create and configure the workflow graph"""
        workflow = StateGraph(AgentState)
        
        # Add all nodes
        workflow.add_node("calculate_risk", cls.calculate_risk_node)
        workflow.add_node("high_risk", cls.handle_high_risk)
        workflow.add_node("medium_risk", cls.handle_medium_risk)
        workflow.add_node("low_risk", cls.handle_low_risk)
        workflow.add_node("error", cls.handle_error)  # Add error handling node
        workflow.add_node("assess_commercial", cls.assess_commercial_vehicle)
        workflow.add_node("assess_private", cls.assess_private_vehicle)
        workflow.add_node("llm_assessment", cls.perform_llm_assessment) 
        workflow.add_node("format_output", cls.format_output)

        # Add conditional edges based on risk level evaluation
        workflow.add_conditional_edges(
            "calculate_risk",
            cls.evaluate_risk_level,
            {
                "high_risk": "high_risk",
                "medium_risk": "medium_risk",
                "low_risk": "low_risk",
                "error": "error"  # Add error path
            }
        )

        for risk_level in ["high_risk", "medium_risk", "low_risk"]:
            workflow.add_conditional_edges(
                risk_level,
                cls.check_vehicle_type,
                {
                    "hiring": "assess_commercial",
                    "private": "assess_private"
                }
            )

        workflow.add_edge("assess_commercial", "llm_assessment")
        workflow.add_edge("assess_private", "llm_assessment")

        workflow.add_edge("llm_assessment", "format_output")
        # Error path goes directly to format_output
        workflow.add_edge("error", "format_output")

        # Add edges from assessment nodes to format_output
        #workflow.add_edge("assess_commercial", "format_output")
        #workflow.add_edge("assess_private", "format_output")
        workflow.add_edge("format_output", END)
        
        # Set the entry point
        workflow.set_entry_point("calculate_risk")
        
        return workflow.compile()