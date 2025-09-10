"""
News and sentiment analysis tools using Finnhub and Tavily.
"""

import finnhub
import asyncio
import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta

from .base_tools import NewsTool, SentimentTool, FundamentalsTool
from ..core.exceptions import APIError, DataError
from config import config


class FinnhubNewsTool(NewsTool):
    """Finnhub news data acquisition tool."""
    
    def __init__(self):
        super().__init__(
            name="finnhub_news",
            description="Fetch news from Finnhub API",
            cache_ttl=1800  # 30 minutes cache for news
        )
        self.api_key = config.get("finnhub_api_key")
        if not self.api_key:
            raise APIError("Finnhub API key not configured", "finnhub")
    
    async def _fetch_company_news(self, ticker: str, start_date: str, end_date: str) -> str:
        """Fetch company-specific news from Finnhub."""
        try:
            loop = asyncio.get_event_loop()
            client = finnhub.Client(api_key=self.api_key)
            
            # Convert dates to timestamps
            start_ts = datetime.strptime(start_date, "%Y-%m-%d").strftime("%Y-%m-%d")
            end_ts = datetime.strptime(end_date, "%Y-%m-%d").strftime("%Y-%m-%d")
            
            news_list = await loop.run_in_executor(
                None,
                lambda: client.company_news(ticker.upper(), _from=start_ts, to=end_ts)
            )
            
            if not news_list:
                return f"No news found for {ticker} between {start_date} and {end_date}"
            
            # Format news items
            news_items = []
            for news in news_list[:10]:  # Limit to 10 most recent
                news_items.append({
                    "headline": news.get('headline', ''),
                    "summary": news.get('summary', ''),
                    "source": news.get('source', ''),
                    "url": news.get('url', ''),
                    "datetime": datetime.fromtimestamp(news.get('datetime', 0)).isoformat(),
                    "sentiment": self._analyze_headline_sentiment(news.get('headline', ''))
                })
            
            # Create formatted output
            formatted_news = []
            for item in news_items:
                formatted_news.append(
                    f"Headline: {item['headline']}\n"
                    f"Summary: {item['summary']}\n"
                    f"Source: {item['source']}\n"
                    f"Date: {item['datetime']}\n"
                    f"Sentiment: {item['sentiment']}\n"
                )
            
            self.log_execution(True)
            return "\n\n".join(formatted_news) if formatted_news else "No relevant news found."
            
        except Exception as e:
            self.log_execution(False)
            raise APIError(f"Error fetching Finnhub news: {e}", "finnhub")
    
    async def _fetch_macro_news(self, trade_date: str) -> str:
        """Fetch general market news for the given date."""
        try:
            loop = asyncio.get_event_loop()
            client = finnhub.Client(api_key=self.api_key)
            
            # Get general market news
            news_list = await loop.run_in_executor(
                None,
                lambda: client.general_news('general')
            )
            
            if not news_list:
                return "No general market news available"
            
            # Filter and format news
            relevant_news = []
            for news in news_list[:5]:  # Limit to 5 items
                news_date = datetime.fromtimestamp(news.get('datetime', 0)).date()
                target_date = datetime.strptime(trade_date, "%Y-%m-%d").date()
                
                # Include news from the same day or 1 day before
                if abs((news_date - target_date).days) <= 1:
                    relevant_news.append(
                        f"Headline: {news.get('headline', '')}\n"
                        f"Summary: {news.get('summary', '')}\n"
                        f"Source: {news.get('source', '')}\n"
                        f"Date: {news_date}\n"
                    )
            
            self.log_execution(True)
            return "\n\n".join(relevant_news) if relevant_news else "No relevant macro news found."
            
        except Exception as e:
            self.log_execution(False)
            raise APIError(f"Error fetching macro news: {e}", "finnhub")
    
    def _analyze_headline_sentiment(self, headline: str) -> str:
        """Simple sentiment analysis of headlines."""
        if not headline:
            return "NEUTRAL"
        
        headline_lower = headline.lower()
        
        positive_words = ['up', 'rise', 'gain', 'bull', 'positive', 'growth', 'strong', 'beat', 'exceed']
        negative_words = ['down', 'fall', 'drop', 'bear', 'negative', 'decline', 'weak', 'miss', 'below']
        
        positive_count = sum(1 for word in positive_words if word in headline_lower)
        negative_count = sum(1 for word in negative_words if word in headline_lower)
        
        if positive_count > negative_count:
            return "POSITIVE"
        elif negative_count > positive_count:
            return "NEGATIVE"
        else:
            return "NEUTRAL"

    async def execute(self, **kwargs) -> str:
        """Execute the Finnhub news tool with flexible parameters."""
        try:
            # Default parameters
            ticker = kwargs.get('ticker', 'AAPL')
            start_date = kwargs.get('start_date', '2024-01-01')
            end_date = kwargs.get('end_date', '2024-12-31')
            news_type = kwargs.get('news_type', 'company')  # 'company' or 'macro'

            if news_type == 'macro':
                trade_date = kwargs.get('trade_date', end_date)
                return await self.get_macro_news(trade_date)
            else:
                return await self.get_company_news(ticker, start_date, end_date)

        except Exception as e:
            self.log_execution(False)
            raise APIError(f"Finnhub news tool execution failed: {e}", "finnhub")


class TavilySentimentTool(SentimentTool):
    """Tavily-based sentiment analysis tool."""
    
    def __init__(self):
        super().__init__(
            name="tavily_sentiment",
            description="Analyze sentiment using Tavily search",
            cache_ttl=1800  # 30 minutes cache
        )
        self.api_key = config.get("tavily_api_key")
        if not self.api_key:
            raise APIError("Tavily API key not configured", "tavily")
    
    async def _fetch_social_sentiment(self, ticker: str, trade_date: str) -> str:
        """Fetch social media sentiment using Tavily search."""
        try:
            from tavily import TavilyClient
            
            client = TavilyClient(api_key=self.api_key)
            
            # Search for social media discussions
            query = f"social media sentiment discussions {ticker} stock {trade_date}"
            
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                None,
                lambda: client.search(query, max_results=5)
            )
            
            if not results or 'results' not in results:
                return f"No social sentiment data found for {ticker}"
            
            # Process results
            sentiment_data = []
            for result in results['results']:
                sentiment_data.append({
                    "title": result.get('title', ''),
                    "content": result.get('content', '')[:500],  # Limit content length
                    "url": result.get('url', ''),
                    "sentiment": self._analyze_content_sentiment(result.get('content', ''))
                })
            
            # Format output
            formatted_sentiment = []
            for item in sentiment_data:
                formatted_sentiment.append(
                    f"Title: {item['title']}\n"
                    f"Content: {item['content']}\n"
                    f"Sentiment: {item['sentiment']}\n"
                    f"Source: {item['url']}\n"
                )
            
            self.log_execution(True)
            return "\n\n".join(formatted_sentiment) if formatted_sentiment else "No sentiment data available."
            
        except Exception as e:
            self.log_execution(False)
            raise APIError(f"Error fetching social sentiment: {e}", "tavily")
    
    def _analyze_content_sentiment(self, content: str) -> str:
        """Analyze sentiment of content."""
        if not content:
            return "NEUTRAL"
        
        content_lower = content.lower()
        
        # More comprehensive sentiment words
        positive_words = [
            'bullish', 'buy', 'long', 'positive', 'optimistic', 'strong', 'growth',
            'rally', 'moon', 'rocket', 'diamond hands', 'hodl', 'to the moon'
        ]
        
        negative_words = [
            'bearish', 'sell', 'short', 'negative', 'pessimistic', 'weak', 'decline',
            'crash', 'dump', 'paper hands', 'panic', 'fear'
        ]
        
        positive_count = sum(1 for word in positive_words if word in content_lower)
        negative_count = sum(1 for word in negative_words if word in content_lower)
        
        # Calculate sentiment score
        total_words = len(content_lower.split())
        positive_ratio = positive_count / max(total_words, 1)
        negative_ratio = negative_count / max(total_words, 1)
        
        if positive_ratio > negative_ratio * 1.5:
            return "VERY_POSITIVE"
        elif positive_ratio > negative_ratio:
            return "POSITIVE"
        elif negative_ratio > positive_ratio * 1.5:
            return "VERY_NEGATIVE"
        elif negative_ratio > positive_ratio:
            return "NEGATIVE"
        else:
            return "NEUTRAL"

    async def execute(self, **kwargs) -> str:
        """Execute the Tavily sentiment tool."""
        try:
            ticker = kwargs.get('ticker', 'AAPL')
            trade_date = kwargs.get('trade_date', '2024-01-01')
            return await self.get_social_sentiment(ticker, trade_date)
        except Exception as e:
            self.log_execution(False)
            raise APIError(f"Tavily sentiment tool execution failed: {e}", "tavily")


class TavilyFundamentalsTool(FundamentalsTool):
    """Tavily-based fundamental analysis tool."""
    
    def __init__(self):
        super().__init__(
            name="tavily_fundamentals",
            description="Get fundamental analysis using Tavily search",
            cache_ttl=3600  # 1 hour cache for fundamentals
        )
        self.api_key = config.get("tavily_api_key")
        if not self.api_key:
            raise APIError("Tavily API key not configured", "tavily")
    
    async def _fetch_fundamental_data(self, ticker: str, trade_date: str) -> str:
        """Fetch fundamental analysis data using Tavily search."""
        try:
            from tavily import TavilyClient
            
            client = TavilyClient(api_key=self.api_key)
            
            # Search for fundamental analysis
            query = f"fundamental analysis financial metrics {ticker} stock earnings revenue {trade_date}"
            
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                None,
                lambda: client.search(query, max_results=5)
            )
            
            if not results or 'results' not in results:
                return f"No fundamental analysis data found for {ticker}"
            
            # Process results
            fundamental_data = []
            for result in results['results']:
                fundamental_data.append({
                    "title": result.get('title', ''),
                    "content": result.get('content', '')[:800],  # Limit content length
                    "url": result.get('url', ''),
                    "relevance_score": result.get('score', 0)
                })
            
            # Sort by relevance
            fundamental_data.sort(key=lambda x: x['relevance_score'], reverse=True)
            
            # Format output
            formatted_data = []
            for item in fundamental_data:
                formatted_data.append(
                    f"Title: {item['title']}\n"
                    f"Analysis: {item['content']}\n"
                    f"Source: {item['url']}\n"
                    f"Relevance: {item['relevance_score']:.2f}\n"
                )
            
            self.log_execution(True)
            return "\n\n".join(formatted_data) if formatted_data else "No fundamental analysis available."
            
        except Exception as e:
            self.log_execution(False)
            raise APIError(f"Error fetching fundamental analysis: {e}", "tavily")

    async def execute(self, **kwargs) -> str:
        """Execute the Tavily fundamentals tool."""
        try:
            ticker = kwargs.get('ticker', 'AAPL')
            trade_date = kwargs.get('trade_date', '2024-01-01')
            return await self.get_fundamental_analysis(ticker, trade_date)
        except Exception as e:
            self.log_execution(False)
            raise APIError(f"Tavily fundamentals tool execution failed: {e}", "tavily")


class NewsAndSentimentAggregator:
    """Aggregates news and sentiment data from multiple sources."""
    
    def __init__(self):
        self.finnhub_tool = FinnhubNewsTool()
        self.tavily_sentiment_tool = TavilySentimentTool()
        self.tavily_fundamentals_tool = TavilyFundamentalsTool()
        self.logger = logging.getLogger("news_sentiment_aggregator")
    
    async def get_comprehensive_analysis(self, ticker: str, trade_date: str) -> dict:
        """Get comprehensive news and sentiment analysis."""
        try:
            # Calculate date range (past week)
            end_date = datetime.strptime(trade_date, "%Y-%m-%d")
            start_date = end_date - timedelta(days=7)
            
            start_date_str = start_date.strftime("%Y-%m-%d")
            end_date_str = end_date.strftime("%Y-%m-%d")
            
            # Fetch data concurrently
            tasks = [
                self.finnhub_tool.get_company_news(ticker, start_date_str, end_date_str),
                self.finnhub_tool.get_macro_news(trade_date),
                self.tavily_sentiment_tool.get_social_sentiment(ticker, trade_date),
                self.tavily_fundamentals_tool.get_fundamental_analysis(ticker, trade_date)
            ]
            
            company_news, macro_news, social_sentiment, fundamentals = await asyncio.gather(*tasks)
            
            return {
                "ticker": ticker.upper(),
                "analysis_date": trade_date,
                "company_news": company_news,
                "macro_news": macro_news,
                "social_sentiment": social_sentiment,
                "fundamental_analysis": fundamentals,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error aggregating news and sentiment for {ticker}: {e}")
            raise DataError(f"Failed to aggregate news and sentiment: {e}")
