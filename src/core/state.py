"""
Core state definitions for the Intelligent Trading Bot system.
"""

from typing import Annotated, List, Dict, Any, Optional
from typing_extensions import TypedDict
from langgraph.graph import MessagesState
from datetime import datetime


class InvestmentDebateState(TypedDict):
    """State for investment research team debate."""
    bull_history: str          # Bull analyst's argument history
    bear_history: str          # Bear analyst's argument history
    history: str               # Complete debate record
    current_response: str      # Most recent argument
    judge_decision: str        # Research manager's final decision
    count: int                 # Debate round counter


class RiskDebateState(TypedDict):
    """State for risk management team debate."""
    risky_history: str         # Aggressive analyst's history
    safe_history: str          # Conservative analyst's history
    neutral_history: str       # Neutral analyst's history
    history: str               # Complete risk discussion record
    latest_speaker: str        # Track last speaker
    current_risky_response: str
    current_safe_response: str
    current_neutral_response: str
    judge_decision: str        # Portfolio manager's final decision
    count: int                 # Risk discussion round counter


class AgentState(MessagesState):
    """
    Main state that flows through the entire trading system graph.
    Inherits from MessagesState to include chat history.
    """
    # Basic trading context
    company_of_interest: str          # Stock ticker being analyzed
    trade_date: str                   # Analysis date (YYYY-MM-DD format)
    sender: str                       # Track which agent last modified state
    
    # Analysis reports from different teams
    market_report: str                # Technical analysis and price data
    sentiment_report: str             # Social media sentiment analysis
    news_report: str                  # News and macroeconomic analysis
    fundamentals_report: str          # Company fundamentals analysis
    
    # Investment research and debate
    investment_debate_state: InvestmentDebateState
    investment_plan: str              # Research manager's investment plan
    
    # Trading execution
    trader_investment_plan: str       # Trader's executable plan
    
    # Risk management
    risk_debate_state: RiskDebateState
    
    # Final decisions and outputs
    final_trade_decision: str         # Portfolio manager's final decision
    final_signal: str                 # Extracted trading signal (BUY/SELL/HOLD)
    
    # Evaluation and learning
    evaluation_score: Optional[float] # System performance score
    learning_completed: Optional[bool] # Learning phase completion flag
    
    # Metadata
    timestamp: Optional[str]          # Processing timestamp
    processing_time: Optional[float]  # Total processing time in seconds


class TradingSignal(TypedDict):
    """Structured trading signal output."""
    signal: str                       # BUY, SELL, or HOLD
    confidence: float                 # Confidence score (0-1)
    position_size: Optional[float]    # Recommended position size
    stop_loss: Optional[float]        # Stop loss level
    take_profit: Optional[float]      # Take profit level
    reasoning: str                    # Decision reasoning
    risk_level: str                   # LOW, MEDIUM, HIGH
    timestamp: str                    # Signal generation time


class AnalysisReport(TypedDict):
    """Standard format for analysis reports."""
    analyst_type: str                 # Type of analyst (market, news, etc.)
    ticker: str                       # Stock ticker
    analysis_date: str                # Analysis date
    summary: str                      # Executive summary
    key_findings: List[str]           # Key insights
    data_sources: List[str]           # Data sources used
    confidence: float                 # Analyst confidence (0-1)
    recommendations: List[str]        # Specific recommendations
    risks: List[str]                  # Identified risks
    timestamp: str                    # Report generation time


class DebateArgument(TypedDict):
    """Structure for debate arguments."""
    speaker: str                      # Agent name
    position: str                     # BULL, BEAR, or NEUTRAL
    argument: str                     # The argument text
    supporting_evidence: List[str]    # Evidence supporting the argument
    counter_points: List[str]         # Acknowledged counter-points
    confidence: float                 # Confidence in argument (0-1)
    timestamp: str                    # Argument timestamp


class RiskAssessment(TypedDict):
    """Risk assessment structure."""
    risk_type: str                    # Type of risk (market, credit, etc.)
    severity: str                     # LOW, MEDIUM, HIGH, CRITICAL
    probability: float                # Probability of occurrence (0-1)
    impact: float                     # Potential impact (0-1)
    mitigation: str                   # Mitigation strategy
    monitoring: str                   # Monitoring approach


class MemoryEntry(TypedDict):
    """Structure for memory system entries."""
    situation: str                    # Situation description
    recommendation: str               # Learned recommendation
    outcome: Optional[str]            # Actual outcome if available
    performance: Optional[float]      # Performance metric
    timestamp: str                    # Entry timestamp
    agent_type: str                   # Which agent type this applies to


class SystemMetrics(TypedDict):
    """System performance metrics."""
    total_decisions: int              # Total decisions made
    successful_decisions: int         # Successful decisions
    accuracy_rate: float              # Success rate
    average_processing_time: float    # Average processing time
    api_calls_made: int               # Total API calls
    cost_per_decision: float          # Cost per decision
    last_updated: str                 # Last metrics update


def create_initial_investment_debate_state() -> InvestmentDebateState:
    """Create initial investment debate state."""
    return InvestmentDebateState(
        bull_history="",
        bear_history="",
        history="",
        current_response="",
        judge_decision="",
        count=0
    )


def create_initial_risk_debate_state() -> RiskDebateState:
    """Create initial risk debate state."""
    return RiskDebateState(
        risky_history="",
        safe_history="",
        neutral_history="",
        history="",
        latest_speaker="",
        current_risky_response="",
        current_safe_response="",
        current_neutral_response="",
        judge_decision="",
        count=0
    )


def create_initial_agent_state(ticker: str, trade_date: str) -> AgentState:
    """Create initial agent state for a trading analysis."""
    return AgentState(
        messages=[],
        company_of_interest=ticker,
        trade_date=trade_date,
        sender="system",
        market_report="",
        sentiment_report="",
        news_report="",
        fundamentals_report="",
        investment_debate_state=create_initial_investment_debate_state(),
        investment_plan="",
        trader_investment_plan="",
        risk_debate_state=create_initial_risk_debate_state(),
        final_trade_decision="",
        final_signal="",
        evaluation_score=None,
        learning_completed=None,
        timestamp=datetime.now().isoformat(),
        processing_time=None
    )
