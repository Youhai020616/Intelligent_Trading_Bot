"""
Base classes and interfaces for the Intelligent Trading Bot system.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from datetime import datetime
import logging

from .state import AgentState, AnalysisReport, TradingSignal
from .exceptions import AgentError


class BaseAgent(ABC):
    """Base class for all trading system agents."""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.logger = logging.getLogger(f"agent.{name}")
        self.created_at = datetime.now()
        self.call_count = 0
        self.error_count = 0
    
    @abstractmethod
    async def execute(self, state: AgentState) -> Dict[str, Any]:
        """Execute the agent's main functionality."""
        pass
    
    def log_execution(self, success: bool, execution_time: float = None):
        """Log agent execution metrics."""
        self.call_count += 1
        if not success:
            self.error_count += 1
        
        if execution_time:
            self.logger.info(f"Agent {self.name} executed in {execution_time:.2f}s")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get agent performance metrics."""
        success_rate = (self.call_count - self.error_count) / max(self.call_count, 1)
        return {
            "name": self.name,
            "call_count": self.call_count,
            "error_count": self.error_count,
            "success_rate": success_rate,
            "created_at": self.created_at.isoformat()
        }


class BaseAnalyst(BaseAgent):
    """Base class for analyst agents."""
    
    def __init__(self, name: str, specialization: str, tools: List[str] = None):
        super().__init__(name, f"Analyst specialized in {specialization}")
        self.specialization = specialization
        self.tools = tools or []
    
    @abstractmethod
    async def analyze(self, ticker: str, date: str, context: Dict[str, Any] = None) -> AnalysisReport:
        """Perform analysis and return structured report."""
        pass
    
    async def execute(self, state: AgentState) -> Dict[str, Any]:
        """Execute analysis and update state."""
        try:
            start_time = datetime.now()
            
            report = await self.analyze(
                ticker=state["company_of_interest"],
                date=state["trade_date"],
                context={"state": state}
            )
            
            execution_time = (datetime.now() - start_time).total_seconds()
            self.log_execution(True, execution_time)
            
            # Return state update based on analyst type
            field_mapping = {
                "market": "market_report",
                "sentiment": "sentiment_report", 
                "news": "news_report",
                "fundamentals": "fundamentals_report"
            }
            
            field_name = field_mapping.get(self.specialization, f"{self.specialization}_report")
            return {
                field_name: report["summary"],
                "sender": self.name
            }
            
        except Exception as e:
            self.log_execution(False)
            raise AgentError(f"Analysis failed: {str(e)}", self.name)


class BaseResearcher(BaseAgent):
    """Base class for research agents (Bull/Bear)."""
    
    def __init__(self, name: str, position: str, memory_system=None):
        super().__init__(name, f"{position} researcher")
        self.position = position  # "BULL" or "BEAR"
        self.memory_system = memory_system
    
    @abstractmethod
    async def research(self, context: Dict[str, Any]) -> str:
        """Conduct research and return argument."""
        pass
    
    async def execute(self, state: AgentState) -> Dict[str, Any]:
        """Execute research and update debate state."""
        try:
            start_time = datetime.now()
            
            argument = await self.research({
                "market_report": state["market_report"],
                "sentiment_report": state["sentiment_report"],
                "news_report": state["news_report"],
                "fundamentals_report": state["fundamentals_report"],
                "debate_history": state["investment_debate_state"]["history"]
            })
            
            execution_time = (datetime.now() - start_time).total_seconds()
            self.log_execution(True, execution_time)
            
            # Update debate state
            debate_state = state["investment_debate_state"].copy()
            debate_state["history"] += f"\n{self.name}: {argument}"
            debate_state["current_response"] = argument
            debate_state["count"] += 1
            
            if self.position == "BULL":
                debate_state["bull_history"] += f"\n{argument}"
            else:
                debate_state["bear_history"] += f"\n{argument}"
            
            return {
                "investment_debate_state": debate_state,
                "sender": self.name
            }
            
        except Exception as e:
            self.log_execution(False)
            raise AgentError(f"Research failed: {str(e)}", self.name)


class BaseTrader(BaseAgent):
    """Base class for trading agents."""
    
    def __init__(self, name: str, trading_style: str = "balanced"):
        super().__init__(name, f"Trader with {trading_style} style")
        self.trading_style = trading_style
    
    @abstractmethod
    async def create_trading_plan(self, investment_analysis: str, context: Dict[str, Any]) -> str:
        """Create executable trading plan."""
        pass
    
    async def execute(self, state: AgentState) -> Dict[str, Any]:
        """Execute trading plan creation."""
        try:
            start_time = datetime.now()
            
            plan = await self.create_trading_plan(
                investment_analysis=state["investment_plan"],
                context={"state": state}
            )
            
            execution_time = (datetime.now() - start_time).total_seconds()
            self.log_execution(True, execution_time)
            
            return {
                "trader_investment_plan": plan,
                "sender": self.name
            }
            
        except Exception as e:
            self.log_execution(False)
            raise AgentError(f"Trading plan creation failed: {str(e)}", self.name)


class BaseRiskAnalyst(BaseAgent):
    """Base class for risk management agents."""
    
    def __init__(self, name: str, risk_perspective: str):
        super().__init__(name, f"Risk analyst with {risk_perspective} perspective")
        self.risk_perspective = risk_perspective  # "risky", "safe", "neutral"
    
    @abstractmethod
    async def assess_risk(self, trading_plan: str, context: Dict[str, Any]) -> str:
        """Assess risk and provide recommendations."""
        pass
    
    async def execute(self, state: AgentState) -> Dict[str, Any]:
        """Execute risk assessment."""
        try:
            start_time = datetime.now()
            
            assessment = await self.assess_risk(
                trading_plan=state["trader_investment_plan"],
                context={"state": state}
            )
            
            execution_time = (datetime.now() - start_time).total_seconds()
            self.log_execution(True, execution_time)
            
            # Update risk debate state
            risk_state = state["risk_debate_state"].copy()
            risk_state["history"] += f"\n{self.name}: {assessment}"
            risk_state["latest_speaker"] = self.name
            risk_state["count"] += 1
            
            # Update specific response field
            if self.risk_perspective == "risky":
                risk_state["current_risky_response"] = assessment
            elif self.risk_perspective == "safe":
                risk_state["current_safe_response"] = assessment
            else:
                risk_state["current_neutral_response"] = assessment
            
            return {
                "risk_debate_state": risk_state,
                "sender": self.name
            }
            
        except Exception as e:
            self.log_execution(False)
            raise AgentError(f"Risk assessment failed: {str(e)}", self.name)


class BaseManager(BaseAgent):
    """Base class for manager agents (Research Manager, Portfolio Manager)."""
    
    def __init__(self, name: str, management_scope: str):
        super().__init__(name, f"Manager for {management_scope}")
        self.management_scope = management_scope
    
    @abstractmethod
    async def make_decision(self, context: Dict[str, Any]) -> str:
        """Make final decision based on team input."""
        pass


class BaseTool(ABC):
    """Base class for data acquisition tools."""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.logger = logging.getLogger(f"tool.{name}")
        self.call_count = 0
        self.error_count = 0
    
    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """Execute the tool's functionality."""
        pass
    
    def log_execution(self, success: bool):
        """Log tool execution metrics."""
        self.call_count += 1
        if not success:
            self.error_count += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get tool performance metrics."""
        success_rate = (self.call_count - self.error_count) / max(self.call_count, 1)
        return {
            "name": self.name,
            "call_count": self.call_count,
            "error_count": self.error_count,
            "success_rate": success_rate
        }
