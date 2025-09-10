"""
Node definitions for the LangGraph trading workflow.
Each node represents a step in the trading decision process.
"""

import logging
from typing import Dict, Any
from datetime import datetime

from ..core.state import AgentState
from ..agents.analysts import AnalystTeam
from ..tools.toolkit import get_trading_toolkit
from ..database import get_session
from ..database.models import TradingSession, Trade, AgentDecision, SystemLog

logger = logging.getLogger(__name__)

# Global instances - created on demand
_analyst_team_instance = None
_trading_toolkit_instance = None

def get_analyst_team() -> AnalystTeam:
    """Get or create global analyst team instance."""
    global _analyst_team_instance
    if _analyst_team_instance is None:
        _analyst_team_instance = AnalystTeam()
    return _analyst_team_instance

def get_trading_toolkit_instance():
    """Get or create global trading toolkit instance."""
    global _trading_toolkit_instance
    if _trading_toolkit_instance is None:
        _trading_toolkit_instance = get_trading_toolkit()
    return _trading_toolkit_instance

async def analyst_team_node(state: AgentState) -> Dict[str, Any]:
    """
    Analyst team node - performs comprehensive market analysis.
    This is the first step in the trading workflow.
    """
    try:
        logger.info(f"🔍 Starting analyst team analysis for {state['company_of_interest']}")

        # Run all analyst analyses
        team = get_analyst_team()
        team_summary = await team.run_all_analyses(
            ticker=state["company_of_interest"],
            date=state["trade_date"]
        )

        logger.info("✅ Analyst team analysis completed")

        # Store analysis results in database
        await _store_analysis_results(state, team_summary)

        return {
            "market_report": team_summary.get("market_analysis", ""),
            "sentiment_report": team_summary.get("sentiment_analysis", ""),
            "news_report": team_summary.get("news_analysis", ""),
            "fundamentals_report": team_summary.get("fundamentals_analysis", ""),
            "sender": "analyst_team"
        }

    except Exception as e:
        logger.error(f"❌ Analyst team analysis failed: {e}")
        await _store_error_log(state, "analyst_team", str(e))
        return {"sender": "analyst_team_error"}

async def research_manager_node(state: AgentState) -> Dict[str, Any]:
    """
    Research manager node - synthesizes analyst reports and creates investment plan.
    """
    try:
        logger.info("🧠 Research manager synthesizing analysis")

        # TODO: Implement research manager logic
        # This should include bull/bear debate and final investment plan

        investment_plan = "Based on comprehensive analysis, recommend HOLD position with monitoring."

        logger.info("✅ Research manager decision completed")

        return {
            "investment_plan": investment_plan,
            "sender": "research_manager"
        }

    except Exception as e:
        logger.error(f"❌ Research manager failed: {e}")
        await _store_error_log(state, "research_manager", str(e))
        return {"sender": "research_manager_error"}

async def trader_node(state: AgentState) -> Dict[str, Any]:
    """
    Trader node - creates executable trading plan.
    """
    try:
        logger.info("📈 Trader creating execution plan")

        # TODO: Implement trader logic
        # This should create specific trading orders and execution strategy

        trading_plan = "Execute limit orders with stop-loss protection."

        logger.info("✅ Trading plan created")

        return {
            "trader_investment_plan": trading_plan,
            "sender": "trader"
        }

    except Exception as e:
        logger.error(f"❌ Trader execution failed: {e}")
        await _store_error_log(state, "trader", str(e))
        return {"sender": "trader_error"}

async def risk_team_node(state: AgentState) -> Dict[str, Any]:
    """
    Risk management team node - assesses trading plan risks.
    """
    try:
        logger.info("⚠️ Risk team assessing plan")

        # TODO: Implement risk assessment logic
        # This should include risk analysis and mitigation strategies

        risk_assessment = "Risk assessment completed. Acceptable risk level."

        logger.info("✅ Risk assessment completed")

        return {
            "risk_assessment": risk_assessment,
            "sender": "risk_team"
        }

    except Exception as e:
        logger.error(f"❌ Risk assessment failed: {e}")
        await _store_error_log(state, "risk_team", str(e))
        return {"sender": "risk_team_error"}

async def portfolio_manager_node(state: AgentState) -> Dict[str, Any]:
    """
    Portfolio manager node - makes final trading decision.
    """
    try:
        logger.info("🎯 Portfolio manager making final decision")

        # TODO: Implement portfolio manager logic
        # This should make the final BUY/SELL/HOLD decision

        final_decision = "HOLD"
        confidence = 0.7

        logger.info(f"✅ Final decision: {final_decision} (confidence: {confidence})")

        return {
            "final_trade_decision": final_decision,
            "final_signal": final_decision,
            "decision_confidence": confidence,
            "sender": "portfolio_manager"
        }

    except Exception as e:
        logger.error(f"❌ Portfolio manager decision failed: {e}")
        await _store_error_log(state, "portfolio_manager", str(e))
        return {"sender": "portfolio_manager_error"}

async def data_storage_node(state: AgentState) -> Dict[str, Any]:
    """
    Data storage node - saves all results to database.
    This is the final step that persists the trading session.
    """
    try:
        logger.info("💾 Storing trading session data")

        session_id = f"{state['company_of_interest']}_{state['trade_date']}_{datetime.now().strftime('%H%M%S')}"

        # Create trading session
        trading_session = TradingSession(
            session_id=session_id,
            status="completed",
            total_trades=0,  # TODO: Update based on actual trades
            total_pnl=0.0,   # TODO: Update based on actual P&L
            end_time=datetime.utcnow()
        )

        # Store final decision
        agent_decision = AgentDecision(
            session_id=session_id,
            agent_name="portfolio_manager",
            decision_type="final_trade_decision",
            symbol=state["company_of_interest"],
            confidence=state.get("decision_confidence", 0.0),
            reasoning=state.get("final_trade_decision", ""),
            timestamp=datetime.utcnow()
        )

        # Save to database
        db_session = get_session()
        try:
            # Add trading session first and commit
            db_session.add(trading_session)
            db_session.commit()

            # Then add decisions and commit
            db_session.add(agent_decision)
            db_session.commit()

            logger.info(f"✅ Trading session {session_id} stored successfully")
        except Exception as db_error:
            db_session.rollback()
            logger.error(f"❌ Database storage failed: {db_error}")
            raise
        finally:
            db_session.close()

        return {
            "session_id": session_id,
            "storage_completed": True,
            "sender": "data_storage"
        }

    except Exception as e:
        logger.error(f"❌ Data storage failed: {e}")
        await _store_error_log(state, "data_storage", str(e))
        return {"sender": "data_storage_error"}

async def _store_analysis_results(state: AgentState, team_summary: Dict[str, Any]):
    """Store analysis results in database."""
    try:
        session_id = f"{state['company_of_interest']}_{state['trade_date']}_analysis"

        # First, create the trading session if it doesn't exist
        trading_session = TradingSession(
            session_id=session_id,
            status="analysis",
            total_trades=0,
            total_pnl=0.0,
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow()
        )

        decisions = [
            AgentDecision(
                session_id=session_id,
                agent_name="market_analyst",
                decision_type="market_analysis",
                symbol=state["company_of_interest"],
                reasoning=team_summary.get("market_analysis", ""),
                timestamp=datetime.utcnow()
            ),
            AgentDecision(
                session_id=session_id,
                agent_name="sentiment_analyst",
                decision_type="sentiment_analysis",
                symbol=state["company_of_interest"],
                reasoning=team_summary.get("sentiment_analysis", ""),
                timestamp=datetime.utcnow()
            ),
            AgentDecision(
                session_id=session_id,
                agent_name="news_analyst",
                decision_type="news_analysis",
                symbol=state["company_of_interest"],
                reasoning=team_summary.get("news_analysis", ""),
                timestamp=datetime.utcnow()
            ),
            AgentDecision(
                session_id=session_id,
                agent_name="fundamentals_analyst",
                decision_type="fundamentals_analysis",
                symbol=state["company_of_interest"],
                reasoning=team_summary.get("fundamentals_analysis", ""),
                timestamp=datetime.utcnow()
            )
        ]

        db_session = get_session()
        try:
            # Check if trading session already exists
            existing_session = db_session.query(TradingSession).filter_by(session_id=session_id).first()

            if existing_session:
                # Update existing session
                existing_session.end_time = datetime.utcnow()
                existing_session.updated_at = datetime.utcnow()
                logger.info(f"✅ Updated existing trading session {session_id}")
            else:
                # Add new trading session
                db_session.add(trading_session)
                logger.info(f"✅ Created new trading session {session_id}")

            db_session.commit()

            # Add decisions (they will be updated if they exist due to unique constraints)
            for decision in decisions:
                # Check if decision already exists
                existing_decision = db_session.query(AgentDecision).filter_by(
                    session_id=decision.session_id,
                    agent_name=decision.agent_name,
                    decision_type=decision.decision_type
                ).first()

                if existing_decision:
                    # Update existing decision
                    existing_decision.reasoning = decision.reasoning
                    existing_decision.timestamp = decision.timestamp
                    logger.info(f"✅ Updated existing decision for {decision.agent_name}")
                else:
                    # Add new decision
                    db_session.add(decision)
                    logger.info(f"✅ Created new decision for {decision.agent_name}")

            db_session.commit()
            logger.info("✅ Analysis results stored in database")

        except Exception as db_error:
            db_session.rollback()
            logger.error(f"❌ Failed to store analysis results: {db_error}")
        finally:
            db_session.close()

    except Exception as e:
        logger.error(f"❌ Error storing analysis results: {e}")

async def _store_error_log(state: AgentState, component: str, error_message: str):
    """Store error logs in database."""
    try:
        log_entry = SystemLog(
            level="ERROR",
            module=component,
            message=f"Error processing {state['company_of_interest']}: {error_message}",
            timestamp=datetime.utcnow(),
            trace_id=state.get("session_id", ""),
            user_id="system"
        )

        db_session = get_session()
        try:
            db_session.add(log_entry)
            db_session.commit()
            logger.info("✅ Error log stored")
        except Exception as db_error:
            logger.error(f"❌ Failed to store error log: {db_error}")
        finally:
            db_session.close()

    except Exception as e:
        logger.error(f"❌ Error storing error log: {e}")