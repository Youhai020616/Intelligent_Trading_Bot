"""
Custom exceptions for the Intelligent Trading Bot system.
"""


class TradingBotException(Exception):
    """Base exception for all trading bot errors."""
    pass


class ConfigurationError(TradingBotException):
    """Raised when there's a configuration issue."""
    pass


class APIError(TradingBotException):
    """Raised when external API calls fail."""
    def __init__(self, message: str, api_name: str = None, status_code: int = None):
        super().__init__(message)
        self.api_name = api_name
        self.status_code = status_code


class DataError(TradingBotException):
    """Raised when there's an issue with data quality or availability."""
    pass


class AgentError(TradingBotException):
    """Raised when an agent fails to complete its task."""
    def __init__(self, message: str, agent_name: str = None):
        super().__init__(message)
        self.agent_name = agent_name


class DebateError(TradingBotException):
    """Raised when debate process fails."""
    pass


class MemoryError(TradingBotException):
    """Raised when memory system operations fail."""
    pass


class EvaluationError(TradingBotException):
    """Raised when evaluation process fails."""
    pass


class WorkflowError(TradingBotException):
    """Raised when workflow execution fails."""
    pass


class ValidationError(TradingBotException):
    """Raised when data validation fails."""
    pass


class TimeoutError(TradingBotException):
    """Raised when operations timeout."""
    pass


class RateLimitError(APIError):
    """Raised when API rate limits are exceeded."""
    def __init__(self, message: str, api_name: str = None, retry_after: int = None):
        super().__init__(message, api_name)
        self.retry_after = retry_after


class InsufficientDataError(DataError):
    """Raised when insufficient data is available for analysis."""
    pass


class InvalidSignalError(TradingBotException):
    """Raised when trading signal is invalid or unparseable."""
    pass
