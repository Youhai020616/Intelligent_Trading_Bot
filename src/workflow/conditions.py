"""
Conditional routing functions for the LangGraph workflow.
These functions determine the flow of execution based on state conditions.
"""

import logging
from typing import Literal
from ..core.state import AgentState

logger = logging.getLogger(__name__)

def should_continue_debate(state: AgentState) -> Literal["continue_debate", "make_decision"]:
    """
    Determine if the investment debate should continue or move to decision making.

    Returns:
        "continue_debate": Continue the bull/bear debate
        "make_decision": Move to research manager decision
    """
    try:
        debate_count = state["investment_debate_state"]["count"]

        # Continue debate for up to 3 rounds
        if debate_count < 3:
            logger.info(f"🔄 Continuing debate (round {debate_count + 1}/3)")
            return "continue_debate"
        else:
            logger.info("🎯 Debate complete, moving to decision")
            return "make_decision"

    except Exception as e:
        logger.error(f"❌ Error in debate condition: {e}")
        return "make_decision"  # Default to decision on error

def should_execute_trade(state: AgentState) -> Literal["execute_trade", "skip_trade"]:
    """
    Determine if a trade should be executed based on risk assessment.

    Returns:
        "execute_trade": Proceed with trade execution
        "skip_trade": Skip trade due to risk concerns
    """
    try:
        # TODO: Implement risk-based trade decision logic
        # This should analyze the risk assessment and decide whether to proceed

        risk_assessment = state.get("risk_assessment", "").lower()

        # Simple risk check - can be made more sophisticated
        if "high risk" in risk_assessment or "unacceptable" in risk_assessment:
            logger.warning("⚠️ High risk detected, skipping trade")
            return "skip_trade"
        else:
            logger.info("✅ Risk assessment passed, proceeding with trade")
            return "execute_trade"

    except Exception as e:
        logger.error(f"❌ Error in trade execution condition: {e}")
        return "skip_trade"  # Default to skip on error for safety

def should_store_results(state: AgentState) -> Literal["store_results", "end_workflow"]:
    """
    Determine if results should be stored.

    Returns:
        "store_results": Store results in database
        "end_workflow": End workflow without storage
    """
    try:
        # Always store results for now, but can add conditions later
        # e.g., only store if confidence > threshold

        confidence = state.get("decision_confidence", 0.0)
        if confidence > 0.5:  # Only store high-confidence decisions
            logger.info("💾 Storing high-confidence results")
            return "store_results"
        else:
            logger.info("⏭️ Skipping storage for low-confidence decision")
            return "end_workflow"

    except Exception as e:
        logger.error(f"❌ Error in storage condition: {e}")
        return "store_results"  # Default to store on error

def validate_workflow_state(state: AgentState) -> bool:
    """
    Validate that the workflow state is in a valid condition to proceed.

    Returns:
        True if state is valid, False otherwise
    """
    try:
        required_fields = [
            "company_of_interest",
            "trade_date",
            "market_report",
            "sentiment_report",
            "news_report",
            "fundamentals_report"
        ]

        for field in required_fields:
            if not state.get(field):
                logger.warning(f"⚠️ Missing required field: {field}")
                return False

        logger.info("✅ Workflow state validation passed")
        return True

    except Exception as e:
        logger.error(f"❌ Error validating workflow state: {e}")
        return False

def get_workflow_status(state: AgentState) -> str:
    """
    Get a human-readable status of the current workflow state.

    Returns:
        Status string describing current workflow position
    """
    try:
        sender = state.get("sender", "unknown")

        status_map = {
            "analyst_team": "Analysis Phase",
            "research_manager": "Research Synthesis",
            "trader": "Trade Planning",
            "risk_team": "Risk Assessment",
            "portfolio_manager": "Final Decision",
            "data_storage": "Data Storage",
            "system": "Initialization",
            "unknown": "Unknown State"
        }

        status = status_map.get(sender, f"Processing ({sender})")

        # Add confidence if available
        confidence = state.get("decision_confidence")
        if confidence is not None:
            status += f" - Confidence: {confidence:.1%}"

        return status

    except Exception as e:
        logger.error(f"❌ Error getting workflow status: {e}")
        return "Error State"