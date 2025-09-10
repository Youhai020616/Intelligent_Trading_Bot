"""
LangGraph workflow definition for the Intelligent Trading Bot.
This creates the complete trading decision workflow graph.
"""

import logging
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableConfig

from ..core.state import AgentState, create_initial_agent_state
from .nodes import (
    analyst_team_node,
    research_manager_node,
    trader_node,
    risk_team_node,
    portfolio_manager_node,
    data_storage_node
)
from .conditions import (
    should_continue_debate,
    should_execute_trade,
    should_store_results,
    validate_workflow_state
)

logger = logging.getLogger(__name__)

def create_trading_workflow() -> StateGraph:
    """
    Create the complete trading decision workflow graph.

    Workflow Structure:
    1. Analyst Team Analysis
    2. Research Manager Synthesis
    3. Trader Plan Creation
    4. Risk Team Assessment
    5. Portfolio Manager Decision
    6. Data Storage
    """
    logger.info("🔧 Creating trading workflow graph")

    # Create the workflow graph
    workflow = StateGraph(AgentState)

    # Add nodes to the graph
    workflow.add_node("analyst_team", analyst_team_node)
    workflow.add_node("research_manager", research_manager_node)
    workflow.add_node("trader", trader_node)
    workflow.add_node("risk_team", risk_team_node)
    workflow.add_node("portfolio_manager", portfolio_manager_node)
    workflow.add_node("data_storage", data_storage_node)

    # Define the workflow edges
    workflow.set_entry_point("analyst_team")

    # Linear flow: analyst -> research_manager -> trader -> risk_team -> portfolio_manager
    workflow.add_edge("analyst_team", "research_manager")
    workflow.add_edge("research_manager", "trader")
    workflow.add_edge("trader", "risk_team")
    workflow.add_edge("risk_team", "portfolio_manager")

    # Conditional edge: portfolio_manager -> data_storage or END
    workflow.add_conditional_edges(
        "portfolio_manager",
        should_store_results,
        {
            "store_results": "data_storage",
            "end_workflow": END
        }
    )

    # Final edge: data_storage -> END
    workflow.add_edge("data_storage", END)

    logger.info("✅ Trading workflow graph created successfully")
    return workflow

def create_workflow_app():
    """
    Create the compiled workflow application ready for execution.

    Returns:
        Compiled LangGraph app
    """
    try:
        workflow = create_trading_workflow()
        app = workflow.compile()

        logger.info("✅ Trading workflow app compiled successfully")
        return app

    except Exception as e:
        logger.error(f"❌ Failed to create workflow app: {e}")
        raise

async def run_trading_workflow(ticker: str, trade_date: str, config: RunnableConfig = None) -> Dict[str, Any]:
    """
    Run the complete trading workflow for a given stock and date.

    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL')
        trade_date: Date for analysis (YYYY-MM-DD format)
        config: Optional LangGraph configuration

    Returns:
        Final workflow state with all analysis results
    """
    try:
        logger.info(f"🚀 Starting trading workflow for {ticker} on {trade_date}")

        # Create initial state
        initial_state = create_initial_agent_state(ticker, trade_date)

        # Validate initial state
        if not validate_workflow_state(initial_state):
            raise ValueError("Invalid initial workflow state")

        # Create and run workflow
        app = create_workflow_app()

        # Run the workflow
        final_state = await app.ainvoke(initial_state, config=config)

        logger.info(f"✅ Trading workflow completed for {ticker}")
        logger.info(f"📊 Final decision: {final_state.get('final_signal', 'UNKNOWN')}")

        return final_state

    except Exception as e:
        logger.error(f"❌ Trading workflow failed: {e}")
        raise

def get_workflow_status(state: AgentState) -> Dict[str, Any]:
    """
    Get comprehensive status information about the current workflow state.

    Args:
        state: Current workflow state

    Returns:
        Dictionary with status information
    """
    try:
        from .conditions import get_workflow_status

        status_info = {
            "current_phase": get_workflow_status(state),
            "company": state.get("company_of_interest", "Unknown"),
            "date": state.get("trade_date", "Unknown"),
            "final_signal": state.get("final_signal", "PENDING"),
            "confidence": state.get("decision_confidence", 0.0),
            "completed": state.get("storage_completed", False),
            "processing_time": state.get("processing_time"),
            "last_sender": state.get("sender", "system")
        }

        # Add analysis completion status
        analysis_fields = ["market_report", "sentiment_report", "news_report", "fundamentals_report"]
        status_info["analysis_complete"] = all(state.get(field) for field in analysis_fields)

        # Add decision completion status
        decision_fields = ["investment_plan", "trader_investment_plan", "final_trade_decision"]
        status_info["decision_complete"] = all(state.get(field) for field in decision_fields)

        return status_info

    except Exception as e:
        logger.error(f"❌ Error getting workflow status: {e}")
        return {"error": str(e)}

# Convenience functions for testing and development
async def run_quick_analysis(ticker: str, trade_date: str = None) -> Dict[str, Any]:
    """
    Run a quick analysis workflow (analyst team only).

    Args:
        ticker: Stock ticker symbol
        trade_date: Optional analysis date (defaults to today)

    Returns:
        Analysis results
    """
    try:
        from datetime import datetime

        if not trade_date:
            trade_date = datetime.now().strftime("%Y-%m-%d")

        logger.info(f"🔍 Running quick analysis for {ticker}")

        # Create minimal workflow with just analyst team
        workflow = StateGraph(AgentState)
        workflow.add_node("analyst_team", analyst_team_node)
        workflow.set_entry_point("analyst_team")
        workflow.add_edge("analyst_team", END)

        app = workflow.compile()
        initial_state = create_initial_agent_state(ticker, trade_date)

        result = await app.ainvoke(initial_state)
        logger.info(f"✅ Quick analysis completed for {ticker}")

        return result

    except Exception as e:
        logger.error(f"❌ Quick analysis failed: {e}")
        raise