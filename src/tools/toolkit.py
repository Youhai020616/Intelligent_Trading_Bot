"""
Integrated toolkit for all data acquisition tools.
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from .market_data import MarketDataAggregator
from .news_sentiment import NewsAndSentimentAggregator
from .base_tools import tool_registry
from ..core.exceptions import DataError, APIError
from config import config


class TradingToolkit:
    """
    Comprehensive toolkit that integrates all data acquisition tools.
    This is the main interface for agents to access market data, news, and sentiment.
    """
    
    def __init__(self):
        self.market_data = MarketDataAggregator()
        self.news_sentiment = NewsAndSentimentAggregator()
        self.logger = logging.getLogger("trading_toolkit")
        self.config = config
        
        # Initialize tools
        self._initialize_tools()
    
    def _initialize_tools(self):
        """Initialize and register all tools."""
        try:
            # Register market data tools
            tool_registry.register_tool(self.market_data.yfinance_tool)
            tool_registry.register_tool(self.market_data.technical_tool)
            
            # Register news and sentiment tools
            tool_registry.register_tool(self.news_sentiment.finnhub_tool)
            tool_registry.register_tool(self.news_sentiment.tavily_sentiment_tool)
            tool_registry.register_tool(self.news_sentiment.tavily_fundamentals_tool)
            
            self.logger.info("All tools initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing tools: {e}")
            raise APIError(f"Failed to initialize toolkit: {e}")
    
    # Market Data Methods
    async def get_yfinance_data(self, symbol: str, start_date: str, end_date: str) -> str:
        """Get stock data from Yahoo Finance."""
        try:
            return await self.market_data.yfinance_tool.get_stock_data(symbol, start_date, end_date)
        except Exception as e:
            self.logger.error(f"Error getting yfinance data: {e}")
            raise
    
    async def get_technical_indicators(self, symbol: str, start_date: str, end_date: str) -> str:
        """Get technical indicators for a stock."""
        try:
            return await self.market_data.technical_tool.get_technical_indicators(symbol, start_date, end_date)
        except Exception as e:
            self.logger.error(f"Error getting technical indicators: {e}")
            raise
    
    async def get_market_snapshot(self, symbol: str) -> Dict[str, Any]:
        """Get a quick market snapshot."""
        try:
            return await self.market_data.get_quick_snapshot(symbol)
        except Exception as e:
            self.logger.error(f"Error getting market snapshot: {e}")
            return {"error": str(e)}
    
    # News and Sentiment Methods
    async def get_finnhub_news(self, ticker: str, start_date: str, end_date: str) -> str:
        """Get company news from Finnhub."""
        try:
            return await self.news_sentiment.finnhub_tool.get_company_news(ticker, start_date, end_date)
        except Exception as e:
            self.logger.error(f"Error getting Finnhub news: {e}")
            raise
    
    async def get_social_media_sentiment(self, ticker: str, trade_date: str) -> str:
        """Get social media sentiment analysis."""
        try:
            return await self.news_sentiment.tavily_sentiment_tool.get_social_sentiment(ticker, trade_date)
        except Exception as e:
            self.logger.error(f"Error getting social sentiment: {e}")
            raise
    
    async def get_fundamental_analysis(self, ticker: str, trade_date: str) -> str:
        """Get fundamental analysis data."""
        try:
            return await self.news_sentiment.tavily_fundamentals_tool.get_fundamental_analysis(ticker, trade_date)
        except Exception as e:
            self.logger.error(f"Error getting fundamental analysis: {e}")
            raise
    
    async def get_macroeconomic_news(self, trade_date: str) -> str:
        """Get macroeconomic news."""
        try:
            return await self.news_sentiment.finnhub_tool.get_macro_news(trade_date)
        except Exception as e:
            self.logger.error(f"Error getting macro news: {e}")
            raise
    
    # Comprehensive Analysis Methods
    async def get_comprehensive_market_data(self, symbol: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get comprehensive market data including all indicators and company info."""
        try:
            return await self.market_data.get_comprehensive_data(symbol, start_date, end_date)
        except Exception as e:
            self.logger.error(f"Error getting comprehensive market data: {e}")
            raise
    
    async def get_comprehensive_news_sentiment(self, ticker: str, trade_date: str) -> Dict[str, Any]:
        """Get comprehensive news and sentiment analysis."""
        try:
            return await self.news_sentiment.get_comprehensive_analysis(ticker, trade_date)
        except Exception as e:
            self.logger.error(f"Error getting comprehensive news/sentiment: {e}")
            raise
    
    async def get_full_analysis(self, ticker: str, trade_date: str) -> Dict[str, Any]:
        """Get complete analysis including market data, news, and sentiment."""
        try:
            # Calculate date range
            from datetime import datetime, timedelta
            end_date = datetime.strptime(trade_date, "%Y-%m-%d")
            start_date = end_date - timedelta(days=30)  # 30 days of data
            
            start_date_str = start_date.strftime("%Y-%m-%d")
            end_date_str = end_date.strftime("%Y-%m-%d")
            
            # Fetch all data concurrently
            tasks = [
                self.get_comprehensive_market_data(ticker, start_date_str, end_date_str),
                self.get_comprehensive_news_sentiment(ticker, trade_date)
            ]
            
            market_data, news_sentiment = await asyncio.gather(*tasks)
            
            return {
                "ticker": ticker.upper(),
                "analysis_date": trade_date,
                "market_data": market_data,
                "news_sentiment": news_sentiment,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting full analysis: {e}")
            raise DataError(f"Failed to get full analysis: {e}")
    
    # Health and Monitoring Methods
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on all tools."""
        try:
            health_status = await tool_registry.health_check()
            
            # Add API key validation
            api_status = {
                "openai_configured": bool(self.config.get("openai_api_key")),
                "finnhub_configured": bool(self.config.get("finnhub_api_key")),
                "tavily_configured": bool(self.config.get("tavily_api_key")),
            }
            
            return {
                "tools": health_status,
                "apis": api_status,
                "overall_health": all(health_status.values()) and all(api_status.values()),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return {
                "error": str(e),
                "overall_health": False,
                "timestamp": datetime.now().isoformat()
            }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for all tools."""
        try:
            return {
                "tool_metrics": tool_registry.get_tool_metrics(),
                "toolkit_info": {
                    "tools_registered": len(tool_registry.list_tools()),
                    "available_tools": tool_registry.list_tools()
                },
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error getting metrics: {e}")
            return {"error": str(e)}
    
    # Utility Methods
    def validate_configuration(self) -> Dict[str, bool]:
        """Validate that all required configurations are present."""
        required_configs = {
            "openai_api_key": "OpenAI API Key",
            "finnhub_api_key": "Finnhub API Key",
            "tavily_api_key": "Tavily API Key"
        }
        
        validation_results = {}
        for key, description in required_configs.items():
            value = self.config.get(key)
            validation_results[description] = bool(value and value.strip())
        
        return validation_results
    
    async def test_all_tools(self, test_symbol: str = "AAPL") -> Dict[str, Any]:
        """Test all tools with a sample symbol."""
        test_results = {}
        test_date = datetime.now().strftime("%Y-%m-%d")
        
        # Test market data tools
        try:
            await self.get_market_snapshot(test_symbol)
            test_results["market_data"] = "PASS"
        except Exception as e:
            test_results["market_data"] = f"FAIL: {str(e)}"
        
        # Test news tools
        try:
            await self.get_macroeconomic_news(test_date)
            test_results["news"] = "PASS"
        except Exception as e:
            test_results["news"] = f"FAIL: {str(e)}"
        
        # Test sentiment tools
        try:
            await self.get_social_media_sentiment(test_symbol, test_date)
            test_results["sentiment"] = "PASS"
        except Exception as e:
            test_results["sentiment"] = f"FAIL: {str(e)}"
        
        # Test fundamental analysis
        try:
            await self.get_fundamental_analysis(test_symbol, test_date)
            test_results["fundamentals"] = "PASS"
        except Exception as e:
            test_results["fundamentals"] = f"FAIL: {str(e)}"
        
        return {
            "test_symbol": test_symbol,
            "test_date": test_date,
            "results": test_results,
            "overall_status": "PASS" if all("PASS" in result for result in test_results.values()) else "FAIL",
            "timestamp": datetime.now().isoformat()
        }


# Global toolkit instance
toolkit = TradingToolkit()
