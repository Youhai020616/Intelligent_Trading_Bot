"""
Base tool definitions and interfaces for data acquisition.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from datetime import datetime
import asyncio
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

from ..core.base import BaseTool
from ..core.exceptions import APIError, DataError, TimeoutError


class DataTool(BaseTool):
    """Base class for data acquisition tools."""
    
    def __init__(self, name: str, description: str = "", cache_ttl: int = 300):
        super().__init__(name, description)
        self.cache_ttl = cache_ttl  # Cache time-to-live in seconds
        self._cache = {}
    
    def _get_cache_key(self, **kwargs) -> str:
        """Generate cache key from parameters."""
        return f"{self.name}:{hash(str(sorted(kwargs.items())))}"
    
    def _is_cache_valid(self, cache_entry: Dict) -> bool:
        """Check if cache entry is still valid."""
        if not cache_entry:
            return False
        
        cache_time = cache_entry.get("timestamp", 0)
        return (datetime.now().timestamp() - cache_time) < self.cache_ttl
    
    async def get_cached_or_fetch(self, fetch_func, **kwargs) -> Any:
        """Get data from cache or fetch if not available/expired."""
        cache_key = self._get_cache_key(**kwargs)
        cache_entry = self._cache.get(cache_key)
        
        if self._is_cache_valid(cache_entry):
            self.logger.debug(f"Cache hit for {cache_key}")
            return cache_entry["data"]
        
        # Fetch new data
        try:
            data = await fetch_func(**kwargs)
            self._cache[cache_key] = {
                "data": data,
                "timestamp": datetime.now().timestamp()
            }
            self.logger.debug(f"Cache miss, fetched new data for {cache_key}")
            return data
        except Exception as e:
            self.log_execution(False)
            raise APIError(f"Failed to fetch data: {str(e)}", self.name)


class MarketDataTool(DataTool):
    """Tool for fetching market data."""
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def get_stock_data(self, symbol: str, start_date: str, end_date: str) -> str:
        """Get stock price data."""
        return await self.get_cached_or_fetch(
            self._fetch_stock_data,
            symbol=symbol,
            start_date=start_date,
            end_date=end_date
        )
    
    @abstractmethod
    async def _fetch_stock_data(self, symbol: str, start_date: str, end_date: str) -> str:
        """Implement actual data fetching."""
        pass


class TechnicalIndicatorTool(DataTool):
    """Tool for calculating technical indicators."""
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def get_technical_indicators(self, symbol: str, start_date: str, end_date: str) -> str:
        """Get technical indicators."""
        return await self.get_cached_or_fetch(
            self._calculate_indicators,
            symbol=symbol,
            start_date=start_date,
            end_date=end_date
        )
    
    @abstractmethod
    async def _calculate_indicators(self, symbol: str, start_date: str, end_date: str) -> str:
        """Implement indicator calculations."""
        pass


class NewsTool(DataTool):
    """Tool for fetching news data."""
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def get_company_news(self, ticker: str, start_date: str, end_date: str) -> str:
        """Get company-specific news."""
        return await self.get_cached_or_fetch(
            self._fetch_company_news,
            ticker=ticker,
            start_date=start_date,
            end_date=end_date
        )
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def get_macro_news(self, trade_date: str) -> str:
        """Get macroeconomic news."""
        return await self.get_cached_or_fetch(
            self._fetch_macro_news,
            trade_date=trade_date
        )
    
    @abstractmethod
    async def _fetch_company_news(self, ticker: str, start_date: str, end_date: str) -> str:
        """Implement company news fetching."""
        pass
    
    @abstractmethod
    async def _fetch_macro_news(self, trade_date: str) -> str:
        """Implement macro news fetching."""
        pass


class SentimentTool(DataTool):
    """Tool for sentiment analysis."""
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def get_social_sentiment(self, ticker: str, trade_date: str) -> str:
        """Get social media sentiment."""
        return await self.get_cached_or_fetch(
            self._fetch_social_sentiment,
            ticker=ticker,
            trade_date=trade_date
        )
    
    @abstractmethod
    async def _fetch_social_sentiment(self, ticker: str, trade_date: str) -> str:
        """Implement sentiment fetching."""
        pass


class FundamentalsTool(DataTool):
    """Tool for fundamental analysis data."""
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def get_fundamental_analysis(self, ticker: str, trade_date: str) -> str:
        """Get fundamental analysis data."""
        return await self.get_cached_or_fetch(
            self._fetch_fundamental_data,
            ticker=ticker,
            trade_date=trade_date
        )
    
    @abstractmethod
    async def _fetch_fundamental_data(self, ticker: str, trade_date: str) -> str:
        """Implement fundamental data fetching."""
        pass


class ToolRegistry:
    """Registry for managing all data acquisition tools."""
    
    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}
        self.logger = logging.getLogger("tool_registry")
    
    def register_tool(self, tool: BaseTool):
        """Register a tool."""
        self.tools[tool.name] = tool
        self.logger.info(f"Registered tool: {tool.name}")
    
    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Get a tool by name."""
        return self.tools.get(name)
    
    def list_tools(self) -> List[str]:
        """List all registered tool names."""
        return list(self.tools.keys())
    
    def get_tool_metrics(self) -> Dict[str, Any]:
        """Get metrics for all tools."""
        return {name: tool.get_metrics() for name, tool in self.tools.items()}
    
    async def health_check(self) -> Dict[str, bool]:
        """Check health of all tools."""
        health_status = {}
        
        for name, tool in self.tools.items():
            try:
                # Perform a simple health check
                # This could be overridden by specific tools
                health_status[name] = True
            except Exception as e:
                self.logger.error(f"Health check failed for {name}: {e}")
                health_status[name] = False
        
        return health_status


# Global tool registry instance
tool_registry = ToolRegistry()
