"""
Analyst agents for market analysis, sentiment analysis, news analysis, and fundamentals.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage

from ..core.base import BaseAnalyst
from ..core.state import AnalysisReport
from ..core.exceptions import AgentError, DataError
from ..tools.toolkit import toolkit
from config import config


class MarketAnalyst(BaseAnalyst):
    """Market analyst specializing in technical analysis and price data."""
    
    def __init__(self, llm: ChatOpenAI = None):
        super().__init__(
            name="market_analyst",
            specialization="market",
            tools=["yfinance_data", "technical_indicators"]
        )
        self.llm = llm or ChatOpenAI(
            model=config.get("quick_think_llm", "gpt-4o-mini"),
            temperature=config.get("temperature", 0.1)
        )
        
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are a professional market analyst specializing in technical analysis. 
            Your role is to analyze stock price data, technical indicators, and market trends to provide 
            actionable insights for trading decisions.
            
            Focus on:
            - Price action and trend analysis
            - Technical indicator signals (RSI, MACD, Moving Averages, etc.)
            - Support and resistance levels
            - Volume analysis
            - Market momentum and volatility
            
            Provide clear, concise analysis with specific data points and actionable recommendations.
            Current date: {current_date}
            Stock being analyzed: {ticker}"""),
            ("human", "Analyze the following market data and provide a comprehensive technical analysis:\n\n{market_data}")
        ])
    
    async def analyze(self, ticker: str, date: str, context: Dict[str, Any] = None) -> AnalysisReport:
        """Perform technical market analysis."""
        try:
            # Calculate date range (30 days of data)
            end_date = datetime.strptime(date, "%Y-%m-%d")
            start_date = end_date - timedelta(days=30)
            
            start_date_str = start_date.strftime("%Y-%m-%d")
            end_date_str = end_date.strftime("%Y-%m-%d")
            
            # Get market data
            market_data = await toolkit.get_comprehensive_market_data(ticker, start_date_str, end_date_str)
            
            # Format data for analysis
            data_summary = self._format_market_data(market_data)
            
            # Generate analysis using LLM
            prompt = self.prompt_template.format_messages(
                current_date=date,
                ticker=ticker,
                market_data=data_summary
            )
            
            response = await self.llm.ainvoke(prompt)
            analysis_text = response.content
            
            # Extract key findings
            key_findings = self._extract_key_findings(analysis_text, market_data)
            
            return AnalysisReport(
                analyst_type="market",
                ticker=ticker,
                analysis_date=date,
                summary=analysis_text,
                key_findings=key_findings,
                data_sources=["Yahoo Finance", "Technical Indicators"],
                confidence=self._calculate_confidence(market_data),
                recommendations=self._extract_recommendations(analysis_text),
                risks=self._identify_risks(analysis_text, market_data),
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            self.logger.error(f"Market analysis failed: {e}")
            raise AgentError(f"Market analysis failed: {e}", self.name)
    
    def _format_market_data(self, market_data: Dict[str, Any]) -> str:
        """Format market data for LLM analysis."""
        try:
            signal_summary = market_data.get("signal_summary", {})
            company_info = market_data.get("company_info", {})
            
            formatted = f"""
COMPANY INFORMATION:
- Symbol: {company_info.get('symbol', 'N/A')}
- Company: {company_info.get('company_name', 'N/A')}
- Sector: {company_info.get('sector', 'N/A')}
- Market Cap: ${company_info.get('market_cap', 0):,}
- P/E Ratio: {company_info.get('pe_ratio', 'N/A')}
- Beta: {company_info.get('beta', 'N/A')}

CURRENT MARKET DATA:
- Current Price: ${signal_summary.get('price', 0):.2f}
- Volume: {signal_summary.get('volume', 0):,}
- 52-Week High: ${company_info.get('52_week_high', 0):.2f}
- 52-Week Low: ${company_info.get('52_week_low', 0):.2f}

TECHNICAL SIGNALS:
"""
            
            signals = signal_summary.get('signals', {})
            for indicator, signal in signals.items():
                formatted += f"- {indicator.upper()}: {signal}\n"
            
            # Add raw data samples
            stock_data = market_data.get("stock_data", "")
            if stock_data:
                formatted += f"\nRECENT PRICE DATA (Last 5 days):\n{stock_data[-500:]}"
            
            indicators_data = market_data.get("technical_indicators", "")
            if indicators_data:
                formatted += f"\nTECHNICAL INDICATORS (Last 5 days):\n{indicators_data[-500:]}"
            
            return formatted
            
        except Exception as e:
            self.logger.warning(f"Error formatting market data: {e}")
            return str(market_data)
    
    def _extract_key_findings(self, analysis: str, market_data: Dict[str, Any]) -> List[str]:
        """Extract key findings from analysis."""
        findings = []
        
        # Add signal-based findings
        signals = market_data.get("signal_summary", {}).get("signals", {})
        for indicator, signal in signals.items():
            if signal in ["BULLISH", "VERY_POSITIVE"]:
                findings.append(f"{indicator.upper()} shows bullish signal")
            elif signal in ["BEARISH", "VERY_NEGATIVE"]:
                findings.append(f"{indicator.upper()} shows bearish signal")
        
        # Add price-based findings
        company_info = market_data.get("company_info", {})
        current_price = market_data.get("signal_summary", {}).get("price", 0)
        high_52 = company_info.get("52_week_high", 0)
        low_52 = company_info.get("52_week_low", 0)
        
        if high_52 and current_price:
            price_position = (current_price - low_52) / (high_52 - low_52) if high_52 != low_52 else 0
            if price_position > 0.8:
                findings.append("Stock trading near 52-week high")
            elif price_position < 0.2:
                findings.append("Stock trading near 52-week low")
        
        return findings[:5]  # Limit to top 5 findings
    
    def _calculate_confidence(self, market_data: Dict[str, Any]) -> float:
        """Calculate confidence score based on data quality."""
        confidence = 0.5  # Base confidence
        
        # Increase confidence based on available data
        if market_data.get("stock_data"):
            confidence += 0.2
        if market_data.get("technical_indicators"):
            confidence += 0.2
        if market_data.get("signal_summary"):
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _extract_recommendations(self, analysis: str) -> List[str]:
        """Extract recommendations from analysis text."""
        recommendations = []
        
        analysis_lower = analysis.lower()
        
        if any(word in analysis_lower for word in ["buy", "bullish", "positive"]):
            recommendations.append("Consider long position")
        if any(word in analysis_lower for word in ["sell", "bearish", "negative"]):
            recommendations.append("Consider short position or exit")
        if any(word in analysis_lower for word in ["hold", "neutral", "sideways"]):
            recommendations.append("Hold current position")
        if "stop loss" in analysis_lower:
            recommendations.append("Implement stop-loss strategy")
        if "volume" in analysis_lower:
            recommendations.append("Monitor volume for confirmation")
        
        return recommendations[:3]  # Limit to top 3
    
    def _identify_risks(self, analysis: str, market_data: Dict[str, Any]) -> List[str]:
        """Identify risks from analysis and data."""
        risks = []
        
        # Volatility-based risks
        company_info = market_data.get("company_info", {})
        beta = company_info.get("beta", 1.0)
        if beta > 1.5:
            risks.append("High volatility stock (Beta > 1.5)")
        
        # Technical risks
        signals = market_data.get("signal_summary", {}).get("signals", {})
        if signals.get("rsi") == "OVERBOUGHT":
            risks.append("RSI indicates overbought conditions")
        elif signals.get("rsi") == "OVERSOLD":
            risks.append("RSI indicates oversold conditions")
        
        # Market cap risks
        market_cap = company_info.get("market_cap", 0)
        if market_cap < 2_000_000_000:  # Less than $2B
            risks.append("Small-cap stock with higher volatility risk")
        
        return risks[:3]  # Limit to top 3 risks


class SentimentAnalyst(BaseAnalyst):
    """Sentiment analyst specializing in social media and public sentiment."""
    
    def __init__(self, llm: ChatOpenAI = None):
        super().__init__(
            name="sentiment_analyst",
            specialization="sentiment",
            tools=["social_media_sentiment"]
        )
        self.llm = llm or ChatOpenAI(
            model=config.get("quick_think_llm", "gpt-4o-mini"),
            temperature=config.get("temperature", 0.1)
        )
        
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are a professional sentiment analyst specializing in social media and public sentiment analysis.
            Your role is to analyze social media discussions, public sentiment, and market psychology to provide 
            insights for trading decisions.
            
            Focus on:
            - Social media sentiment trends
            - Public perception and market psychology
            - Sentiment momentum and shifts
            - Contrarian indicators
            - Retail vs institutional sentiment
            
            Provide clear analysis of sentiment trends and their potential impact on stock price.
            Current date: {current_date}
            Stock being analyzed: {ticker}"""),
            ("human", "Analyze the following sentiment data and provide comprehensive sentiment analysis:\n\n{sentiment_data}")
        ])
    
    async def analyze(self, ticker: str, date: str, context: Dict[str, Any] = None) -> AnalysisReport:
        """Perform sentiment analysis."""
        try:
            # Get sentiment data
            sentiment_data = await toolkit.get_social_media_sentiment(ticker, date)
            
            # Generate analysis using LLM
            prompt = self.prompt_template.format_messages(
                current_date=date,
                ticker=ticker,
                sentiment_data=sentiment_data
            )
            
            response = await self.llm.ainvoke(prompt)
            analysis_text = response.content
            
            # Extract key findings
            key_findings = self._extract_sentiment_findings(sentiment_data)
            
            return AnalysisReport(
                analyst_type="sentiment",
                ticker=ticker,
                analysis_date=date,
                summary=analysis_text,
                key_findings=key_findings,
                data_sources=["Social Media", "Tavily Search"],
                confidence=self._calculate_sentiment_confidence(sentiment_data),
                recommendations=self._extract_sentiment_recommendations(analysis_text),
                risks=self._identify_sentiment_risks(analysis_text),
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            self.logger.error(f"Sentiment analysis failed: {e}")
            raise AgentError(f"Sentiment analysis failed: {e}", self.name)
    
    def _extract_sentiment_findings(self, sentiment_data: str) -> List[str]:
        """Extract key sentiment findings."""
        findings = []
        
        if not sentiment_data or "No sentiment data" in sentiment_data:
            findings.append("Limited social media sentiment data available")
            return findings
        
        sentiment_lower = sentiment_data.lower()
        
        # Count sentiment indicators
        positive_indicators = sentiment_lower.count("positive") + sentiment_lower.count("bullish")
        negative_indicators = sentiment_lower.count("negative") + sentiment_lower.count("bearish")
        
        if positive_indicators > negative_indicators:
            findings.append("Overall positive social media sentiment")
        elif negative_indicators > positive_indicators:
            findings.append("Overall negative social media sentiment")
        else:
            findings.append("Mixed social media sentiment")
        
        # Look for specific sentiment patterns
        if "very_positive" in sentiment_lower:
            findings.append("Strong positive sentiment detected")
        if "very_negative" in sentiment_lower:
            findings.append("Strong negative sentiment detected")
        
        return findings[:3]
    
    def _calculate_sentiment_confidence(self, sentiment_data: str) -> float:
        """Calculate confidence based on sentiment data quality."""
        if not sentiment_data or "No sentiment data" in sentiment_data:
            return 0.3
        
        # Base confidence
        confidence = 0.5
        
        # Increase based on data richness
        if len(sentiment_data) > 500:
            confidence += 0.2
        if "sentiment:" in sentiment_data.lower():
            confidence += 0.2
        
        return min(confidence, 0.9)  # Cap at 0.9 for sentiment analysis
    
    def _extract_sentiment_recommendations(self, analysis: str) -> List[str]:
        """Extract sentiment-based recommendations."""
        recommendations = []
        
        analysis_lower = analysis.lower()
        
        if "positive sentiment" in analysis_lower:
            recommendations.append("Positive sentiment supports bullish outlook")
        if "negative sentiment" in analysis_lower:
            recommendations.append("Negative sentiment suggests caution")
        if "contrarian" in analysis_lower:
            recommendations.append("Consider contrarian approach")
        
        return recommendations[:2]
    
    def _identify_sentiment_risks(self, analysis: str) -> List[str]:
        """Identify sentiment-related risks."""
        risks = []
        
        analysis_lower = analysis.lower()
        
        if "extreme" in analysis_lower:
            risks.append("Extreme sentiment may indicate reversal risk")
        if "hype" in analysis_lower or "fomo" in analysis_lower:
            risks.append("FOMO-driven sentiment may be unsustainable")
        
        return risks[:2]


class NewsAnalyst(BaseAnalyst):
    """News analyst specializing in news analysis and macroeconomic events."""

    def __init__(self, llm: ChatOpenAI = None):
        super().__init__(
            name="news_analyst",
            specialization="news",
            tools=["finnhub_news", "macroeconomic_news"]
        )
        self.llm = llm or ChatOpenAI(
            model=config.get("quick_think_llm", "gpt-4o-mini"),
            temperature=config.get("temperature", 0.1)
        )

        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are a professional news analyst specializing in financial news and macroeconomic analysis.
            Your role is to analyze company-specific news, macroeconomic events, and market-moving developments
            to provide insights for trading decisions.

            Focus on:
            - Company-specific news and developments
            - Macroeconomic events and policy changes
            - Market-moving news and catalysts
            - Earnings and financial announcements
            - Regulatory and industry developments

            Provide clear analysis of news impact and potential market implications.
            Current date: {current_date}
            Stock being analyzed: {ticker}"""),
            ("human", "Analyze the following news data and provide comprehensive news analysis:\n\n{news_data}")
        ])

    async def analyze(self, ticker: str, date: str, context: Dict[str, Any] = None) -> AnalysisReport:
        """Perform news analysis."""
        try:
            # Calculate date range for news
            end_date = datetime.strptime(date, "%Y-%m-%d")
            start_date = end_date - timedelta(days=7)  # Past week

            start_date_str = start_date.strftime("%Y-%m-%d")
            end_date_str = end_date.strftime("%Y-%m-%d")

            # Get news data
            company_news = await toolkit.get_finnhub_news(ticker, start_date_str, end_date_str)
            macro_news = await toolkit.get_macroeconomic_news(date)

            # Combine news data
            combined_news = f"COMPANY NEWS:\n{company_news}\n\nMACROECONOMIC NEWS:\n{macro_news}"

            # Generate analysis using LLM
            prompt = self.prompt_template.format_messages(
                current_date=date,
                ticker=ticker,
                news_data=combined_news
            )

            response = await self.llm.ainvoke(prompt)
            analysis_text = response.content

            # Extract key findings
            key_findings = self._extract_news_findings(company_news, macro_news)

            return AnalysisReport(
                analyst_type="news",
                ticker=ticker,
                analysis_date=date,
                summary=analysis_text,
                key_findings=key_findings,
                data_sources=["Finnhub News", "Macroeconomic Data"],
                confidence=self._calculate_news_confidence(company_news, macro_news),
                recommendations=self._extract_news_recommendations(analysis_text),
                risks=self._identify_news_risks(analysis_text, company_news),
                timestamp=datetime.now().isoformat()
            )

        except Exception as e:
            self.logger.error(f"News analysis failed: {e}")
            raise AgentError(f"News analysis failed: {e}", self.name)

    def _extract_news_findings(self, company_news: str, macro_news: str) -> List[str]:
        """Extract key news findings."""
        findings = []

        # Analyze company news
        if company_news and "No news found" not in company_news:
            company_lower = company_news.lower()

            if any(word in company_lower for word in ["earnings", "revenue", "profit"]):
                findings.append("Recent earnings or financial announcements")
            if any(word in company_lower for word in ["acquisition", "merger", "deal"]):
                findings.append("M&A activity or strategic deals")
            if any(word in company_lower for word in ["partnership", "contract", "agreement"]):
                findings.append("New partnerships or contracts announced")

            # Sentiment analysis of headlines
            positive_count = company_lower.count("positive") + company_lower.count("beat") + company_lower.count("strong")
            negative_count = company_lower.count("negative") + company_lower.count("miss") + company_lower.count("weak")

            if positive_count > negative_count:
                findings.append("Generally positive news sentiment")
            elif negative_count > positive_count:
                findings.append("Generally negative news sentiment")
        else:
            findings.append("Limited company-specific news available")

        # Analyze macro news
        if macro_news and "No" not in macro_news:
            macro_lower = macro_news.lower()

            if any(word in macro_lower for word in ["fed", "interest rate", "monetary policy"]):
                findings.append("Federal Reserve or monetary policy news")
            if any(word in macro_lower for word in ["inflation", "cpi", "ppi"]):
                findings.append("Inflation-related economic data")
            if any(word in macro_lower for word in ["gdp", "employment", "jobs"]):
                findings.append("Economic growth or employment data")

        return findings[:5]

    def _calculate_news_confidence(self, company_news: str, macro_news: str) -> float:
        """Calculate confidence based on news data quality."""
        confidence = 0.4  # Base confidence

        # Increase based on available news
        if company_news and "No news found" not in company_news:
            confidence += 0.3
        if macro_news and "No" not in macro_news:
            confidence += 0.2

        # Increase based on news richness
        total_length = len(company_news) + len(macro_news)
        if total_length > 1000:
            confidence += 0.1

        return min(confidence, 1.0)

    def _extract_news_recommendations(self, analysis: str) -> List[str]:
        """Extract news-based recommendations."""
        recommendations = []

        analysis_lower = analysis.lower()

        if any(word in analysis_lower for word in ["positive", "bullish", "strong"]):
            recommendations.append("News supports positive outlook")
        if any(word in analysis_lower for word in ["negative", "bearish", "weak"]):
            recommendations.append("News suggests caution")
        if "earnings" in analysis_lower:
            recommendations.append("Monitor upcoming earnings announcements")
        if any(word in analysis_lower for word in ["fed", "interest", "policy"]):
            recommendations.append("Consider macroeconomic policy impacts")

        return recommendations[:3]

    def _identify_news_risks(self, analysis: str, company_news: str) -> List[str]:
        """Identify news-related risks."""
        risks = []

        analysis_lower = analysis.lower()
        news_lower = company_news.lower()

        if any(word in news_lower for word in ["lawsuit", "investigation", "regulatory"]):
            risks.append("Legal or regulatory risks identified")
        if any(word in news_lower for word in ["competition", "competitor", "market share"]):
            risks.append("Competitive pressure risks")
        if "uncertainty" in analysis_lower:
            risks.append("Market uncertainty from news events")

        return risks[:3]


class FundamentalsAnalyst(BaseAnalyst):
    """Fundamentals analyst specializing in company financial analysis."""

    def __init__(self, llm: ChatOpenAI = None):
        super().__init__(
            name="fundamentals_analyst",
            specialization="fundamentals",
            tools=["fundamental_analysis"]
        )
        self.llm = llm or ChatOpenAI(
            model=config.get("quick_think_llm", "gpt-4o-mini"),
            temperature=config.get("temperature", 0.1)
        )

        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are a professional fundamental analyst specializing in company financial analysis.
            Your role is to analyze company fundamentals, financial health, valuation metrics, and business prospects
            to provide insights for investment decisions.

            Focus on:
            - Financial statement analysis
            - Valuation metrics and ratios
            - Business model and competitive position
            - Growth prospects and profitability
            - Balance sheet strength and cash flow

            Provide clear analysis of fundamental strengths and weaknesses.
            Current date: {current_date}
            Stock being analyzed: {ticker}"""),
            ("human", "Analyze the following fundamental data and provide comprehensive fundamental analysis:\n\n{fundamental_data}")
        ])

    async def analyze(self, ticker: str, date: str, context: Dict[str, Any] = None) -> AnalysisReport:
        """Perform fundamental analysis."""
        try:
            # Get fundamental data
            fundamental_data = await toolkit.get_fundamental_analysis(ticker, date)

            # Generate analysis using LLM
            prompt = self.prompt_template.format_messages(
                current_date=date,
                ticker=ticker,
                fundamental_data=fundamental_data
            )

            response = await self.llm.ainvoke(prompt)
            analysis_text = response.content

            # Extract key findings
            key_findings = self._extract_fundamental_findings(fundamental_data)

            return AnalysisReport(
                analyst_type="fundamentals",
                ticker=ticker,
                analysis_date=date,
                summary=analysis_text,
                key_findings=key_findings,
                data_sources=["Fundamental Analysis", "Financial Data"],
                confidence=self._calculate_fundamental_confidence(fundamental_data),
                recommendations=self._extract_fundamental_recommendations(analysis_text),
                risks=self._identify_fundamental_risks(analysis_text),
                timestamp=datetime.now().isoformat()
            )

        except Exception as e:
            self.logger.error(f"Fundamental analysis failed: {e}")
            raise AgentError(f"Fundamental analysis failed: {e}", self.name)

    def _extract_fundamental_findings(self, fundamental_data: str) -> List[str]:
        """Extract key fundamental findings."""
        findings = []

        if not fundamental_data or "No fundamental analysis" in fundamental_data:
            findings.append("Limited fundamental data available")
            return findings

        data_lower = fundamental_data.lower()

        # Look for key financial metrics mentions
        if any(word in data_lower for word in ["revenue", "sales", "income"]):
            findings.append("Revenue and income data available")
        if any(word in data_lower for word in ["earnings", "eps", "profit"]):
            findings.append("Earnings and profitability metrics")
        if any(word in data_lower for word in ["debt", "cash", "balance sheet"]):
            findings.append("Balance sheet and financial position data")
        if any(word in data_lower for word in ["growth", "expansion", "market"]):
            findings.append("Growth and market position analysis")
        if any(word in data_lower for word in ["valuation", "pe", "price"]):
            findings.append("Valuation metrics and ratios")

        return findings[:4]

    def _calculate_fundamental_confidence(self, fundamental_data: str) -> float:
        """Calculate confidence based on fundamental data quality."""
        if not fundamental_data or "No fundamental analysis" in fundamental_data:
            return 0.3

        confidence = 0.5  # Base confidence

        # Increase based on data richness
        if len(fundamental_data) > 800:
            confidence += 0.2
        if any(word in fundamental_data.lower() for word in ["financial", "earnings", "revenue"]):
            confidence += 0.2

        return min(confidence, 0.9)

    def _extract_fundamental_recommendations(self, analysis: str) -> List[str]:
        """Extract fundamental-based recommendations."""
        recommendations = []

        analysis_lower = analysis.lower()

        if any(word in analysis_lower for word in ["strong", "solid", "healthy"]):
            recommendations.append("Strong fundamental position")
        if any(word in analysis_lower for word in ["weak", "poor", "concerning"]):
            recommendations.append("Fundamental concerns identified")
        if "undervalued" in analysis_lower:
            recommendations.append("Potential undervaluation opportunity")
        if "overvalued" in analysis_lower:
            recommendations.append("Possible overvaluation risk")

        return recommendations[:3]

    def _identify_fundamental_risks(self, analysis: str) -> List[str]:
        """Identify fundamental risks."""
        risks = []

        analysis_lower = analysis.lower()

        if any(word in analysis_lower for word in ["debt", "leverage", "financial stress"]):
            risks.append("Financial leverage or debt concerns")
        if any(word in analysis_lower for word in ["competition", "market share", "competitive"]):
            risks.append("Competitive position risks")
        if "valuation" in analysis_lower and "high" in analysis_lower:
            risks.append("Valuation concerns")

        return risks[:3]


class AnalystTeam:
    """Manages the team of analyst agents."""

    def __init__(self):
        self.market_analyst = MarketAnalyst()
        self.sentiment_analyst = SentimentAnalyst()
        self.news_analyst = NewsAnalyst()
        self.fundamentals_analyst = FundamentalsAnalyst()

        self.analysts = {
            "market": self.market_analyst,
            "sentiment": self.sentiment_analyst,
            "news": self.news_analyst,
            "fundamentals": self.fundamentals_analyst
        }

        self.logger = logging.getLogger("analyst_team")

    async def run_all_analyses(self, ticker: str, date: str) -> Dict[str, AnalysisReport]:
        """Run all analyses concurrently."""
        try:
            # Run all analyses in parallel
            tasks = [
                self.market_analyst.analyze(ticker, date),
                self.sentiment_analyst.analyze(ticker, date),
                self.news_analyst.analyze(ticker, date),
                self.fundamentals_analyst.analyze(ticker, date)
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results
            analysis_results = {}
            analyst_names = ["market", "sentiment", "news", "fundamentals"]

            for i, result in enumerate(results):
                analyst_name = analyst_names[i]
                if isinstance(result, Exception):
                    self.logger.error(f"{analyst_name} analysis failed: {result}")
                    # Create a fallback report
                    analysis_results[analyst_name] = self._create_fallback_report(
                        analyst_name, ticker, date, str(result)
                    )
                else:
                    analysis_results[analyst_name] = result

            return analysis_results

        except Exception as e:
            self.logger.error(f"Team analysis failed: {e}")
            raise AgentError(f"Analyst team execution failed: {e}", "analyst_team")

    def _create_fallback_report(self, analyst_type: str, ticker: str, date: str, error: str) -> AnalysisReport:
        """Create a fallback report when analysis fails."""
        return AnalysisReport(
            analyst_type=analyst_type,
            ticker=ticker,
            analysis_date=date,
            summary=f"Analysis failed due to: {error}",
            key_findings=[f"{analyst_type.title()} analysis unavailable"],
            data_sources=[],
            confidence=0.0,
            recommendations=["Unable to provide recommendations due to analysis failure"],
            risks=["Analysis failure risk"],
            timestamp=datetime.now().isoformat()
        )

    async def get_team_summary(self, ticker: str, date: str) -> Dict[str, Any]:
        """Get a comprehensive summary from all analysts."""
        try:
            analyses = await self.run_all_analyses(ticker, date)

            # Aggregate findings
            all_findings = []
            all_recommendations = []
            all_risks = []
            total_confidence = 0

            for analyst_type, report in analyses.items():
                all_findings.extend(report["key_findings"])
                all_recommendations.extend(report["recommendations"])
                all_risks.extend(report["risks"])
                total_confidence += report["confidence"]

            average_confidence = total_confidence / len(analyses)

            return {
                "ticker": ticker,
                "analysis_date": date,
                "individual_analyses": analyses,
                "team_summary": {
                    "key_findings": all_findings[:10],  # Top 10 findings
                    "recommendations": all_recommendations[:8],  # Top 8 recommendations
                    "risks": all_risks[:8],  # Top 8 risks
                    "average_confidence": average_confidence,
                    "analysts_completed": len([r for r in analyses.values() if r["confidence"] > 0])
                },
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Team summary failed: {e}")
            raise AgentError(f"Team summary generation failed: {e}", "analyst_team")

    def get_team_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for the analyst team."""
        metrics = {}

        for name, analyst in self.analysts.items():
            metrics[name] = analyst.get_metrics()

        return {
            "individual_metrics": metrics,
            "team_size": len(self.analysts),
            "timestamp": datetime.now().isoformat()
        }


# Global analyst team instance
analyst_team = AnalystTeam()
