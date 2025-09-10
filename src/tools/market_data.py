"""
Market data acquisition tools using yfinance and other sources.
"""

import yfinance as yf
import pandas as pd
from typing import Optional
from datetime import datetime, timedelta
import asyncio
import logging

from .base_tools import MarketDataTool, TechnicalIndicatorTool
from ..core.exceptions import DataError, APIError


class YFinanceDataTool(MarketDataTool):
    """Yahoo Finance data acquisition tool."""
    
    def __init__(self):
        super().__init__(
            name="yfinance_data",
            description="Fetch stock data from Yahoo Finance",
            cache_ttl=300  # 5 minutes cache
        )
    
    async def _fetch_stock_data(self, symbol: str, start_date: str, end_date: str) -> str:
        """Fetch stock data from Yahoo Finance."""
        try:
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            ticker = yf.Ticker(symbol.upper())
            
            data = await loop.run_in_executor(
                None,
                lambda: ticker.history(start=start_date, end=end_date)
            )
            
            if data.empty:
                raise DataError(f"No data found for symbol '{symbol}' between {start_date} and {end_date}")
            
            self.log_execution(True)
            return data.to_csv()
            
        except Exception as e:
            self.log_execution(False)
            raise APIError(f"Error fetching Yahoo Finance data: {e}", "yfinance")
    
    async def get_current_price(self, symbol: str) -> Optional[float]:
        """Get current stock price."""
        try:
            loop = asyncio.get_event_loop()
            ticker = yf.Ticker(symbol.upper())
            
            info = await loop.run_in_executor(None, lambda: ticker.info)
            return info.get('currentPrice') or info.get('regularMarketPrice')
            
        except Exception as e:
            self.logger.error(f"Error fetching current price for {symbol}: {e}")
            return None
    
    async def get_company_info(self, symbol: str) -> dict:
        """Get company information."""
        try:
            loop = asyncio.get_event_loop()
            ticker = yf.Ticker(symbol.upper())
            
            info = await loop.run_in_executor(None, lambda: ticker.info)
            
            # Extract key information
            return {
                "symbol": symbol.upper(),
                "company_name": info.get("longName", ""),
                "sector": info.get("sector", ""),
                "industry": info.get("industry", ""),
                "market_cap": info.get("marketCap", 0),
                "pe_ratio": info.get("trailingPE", 0),
                "dividend_yield": info.get("dividendYield", 0),
                "beta": info.get("beta", 0),
                "52_week_high": info.get("fiftyTwoWeekHigh", 0),
                "52_week_low": info.get("fiftyTwoWeekLow", 0),
            }
            
        except Exception as e:
            self.logger.error(f"Error fetching company info for {symbol}: {e}")
            return {}

    async def execute(self, **kwargs) -> str:
        """Execute the Yahoo Finance data tool with flexible parameters."""
        try:
            symbol = kwargs.get('symbol', 'AAPL')
            start_date = kwargs.get('start_date', '2024-01-01')
            end_date = kwargs.get('end_date', '2024-12-31')
            data_type = kwargs.get('data_type', 'stock_data')  # 'stock_data' or 'company_info'

            if data_type == 'company_info':
                info = await self.get_company_info(symbol)
                return str(info)  # Convert dict to string
            else:
                return await self.get_stock_data(symbol, start_date, end_date)

        except Exception as e:
            self.log_execution(False)
            raise APIError(f"YFinance data tool execution failed: {e}", "yfinance")


class TechnicalIndicatorCalculator(TechnicalIndicatorTool):
    """Calculate technical indicators using stockstats."""
    
    def __init__(self):
        super().__init__(
            name="technical_indicators",
            description="Calculate technical indicators",
            cache_ttl=300  # 5 minutes cache
        )
    
    async def _calculate_indicators(self, symbol: str, start_date: str, end_date: str) -> str:
        """Calculate technical indicators."""
        try:
            # First get the stock data
            yfinance_tool = YFinanceDataTool()
            stock_data_csv = await yfinance_tool._fetch_stock_data(symbol, start_date, end_date)
            
            # Convert CSV back to DataFrame
            from io import StringIO
            df = pd.read_csv(StringIO(stock_data_csv), index_col=0, parse_dates=True)
            
            if df.empty:
                raise DataError("No data available for indicator calculation")
            
            # Calculate indicators using stockstats
            from stockstats import wrap as stockstats_wrap
            
            loop = asyncio.get_event_loop()
            stock_df = await loop.run_in_executor(None, lambda: stockstats_wrap(df))
            
            # Calculate key indicators
            indicators = await loop.run_in_executor(None, self._compute_indicators, stock_df)
            
            self.log_execution(True)
            return indicators.tail(10).to_csv()  # Return last 10 days
            
        except Exception as e:
            self.log_execution(False)
            raise APIError(f"Error calculating technical indicators: {e}", "stockstats")
    
    def _compute_indicators(self, stock_df):
        """Compute technical indicators synchronously."""
        try:
            # Key technical indicators
            indicators_df = stock_df[[
                'close',  # Closing price
                'volume',  # Volume
            ]].copy()
            
            # Moving averages
            indicators_df['sma_20'] = stock_df['close_20_sma']
            indicators_df['sma_50'] = stock_df['close_50_sma']
            indicators_df['sma_200'] = stock_df['close_200_sma']
            
            # RSI
            indicators_df['rsi_14'] = stock_df['rsi_14']
            
            # MACD
            indicators_df['macd'] = stock_df['macd']
            indicators_df['macd_signal'] = stock_df['macds']
            indicators_df['macd_histogram'] = stock_df['macdh']
            
            # Bollinger Bands
            indicators_df['bb_upper'] = stock_df['boll_ub']
            indicators_df['bb_middle'] = stock_df['boll']
            indicators_df['bb_lower'] = stock_df['boll_lb']
            
            # Stochastic
            indicators_df['stoch_k'] = stock_df['kdjk']
            indicators_df['stoch_d'] = stock_df['kdjd']
            
            # Williams %R
            indicators_df['williams_r'] = stock_df['wr_14']
            
            # Average True Range
            indicators_df['atr'] = stock_df['atr_14']
            
            return indicators_df
            
        except Exception as e:
            # If some indicators fail, return what we can
            self.logger.warning(f"Some indicators failed to calculate: {e}")
            return stock_df[['close', 'volume']].copy()
    
    async def get_signal_summary(self, symbol: str, start_date: str, end_date: str) -> dict:
        """Get a summary of technical signals."""
        try:
            indicators_csv = await self.get_technical_indicators(symbol, start_date, end_date)
            
            # Parse the CSV
            from io import StringIO
            df = pd.read_csv(StringIO(indicators_csv), index_col=0, parse_dates=True)
            
            if df.empty:
                return {"error": "No data available"}
            
            latest = df.iloc[-1]
            
            # Generate signals
            signals = {
                "symbol": symbol,
                "date": df.index[-1].strftime("%Y-%m-%d"),
                "price": latest.get('close', 0),
                "volume": latest.get('volume', 0),
                "signals": {}
            }
            
            # RSI signals
            rsi = latest.get('rsi_14', 50)
            if rsi > 70:
                signals["signals"]["rsi"] = "OVERBOUGHT"
            elif rsi < 30:
                signals["signals"]["rsi"] = "OVERSOLD"
            else:
                signals["signals"]["rsi"] = "NEUTRAL"
            
            # Moving average signals
            price = latest.get('close', 0)
            sma_20 = latest.get('sma_20', 0)
            sma_50 = latest.get('sma_50', 0)
            
            if price > sma_20 > sma_50:
                signals["signals"]["trend"] = "BULLISH"
            elif price < sma_20 < sma_50:
                signals["signals"]["trend"] = "BEARISH"
            else:
                signals["signals"]["trend"] = "NEUTRAL"
            
            # MACD signals
            macd = latest.get('macd', 0)
            macd_signal = latest.get('macd_signal', 0)
            
            if macd > macd_signal:
                signals["signals"]["macd"] = "BULLISH"
            else:
                signals["signals"]["macd"] = "BEARISH"
            
            return signals
            
        except Exception as e:
            self.logger.error(f"Error generating signal summary: {e}")
            return {"error": str(e)}

    async def execute(self, **kwargs) -> str:
        """Execute the technical indicators tool."""
        try:
            symbol = kwargs.get('symbol', 'AAPL')
            start_date = kwargs.get('start_date', '2024-01-01')
            end_date = kwargs.get('end_date', '2024-12-31')
            operation = kwargs.get('operation', 'indicators')  # 'indicators' or 'signals'

            if operation == 'signals':
                signals = await self.get_signal_summary(symbol, start_date, end_date)
                return str(signals)  # Convert dict to string
            else:
                return await self.get_technical_indicators(symbol, start_date, end_date)

        except Exception as e:
            self.log_execution(False)
            raise APIError(f"Technical indicators tool execution failed: {e}", "technical")


class MarketDataAggregator:
    """Aggregates data from multiple market data sources."""
    
    def __init__(self):
        self.yfinance_tool = YFinanceDataTool()
        self.technical_tool = TechnicalIndicatorCalculator()
        self.logger = logging.getLogger("market_data_aggregator")
    
    async def get_comprehensive_data(self, symbol: str, start_date: str, end_date: str) -> dict:
        """Get comprehensive market data including price, indicators, and company info."""
        try:
            # Fetch data concurrently
            tasks = [
                self.yfinance_tool.get_stock_data(symbol, start_date, end_date),
                self.technical_tool.get_technical_indicators(symbol, start_date, end_date),
                self.yfinance_tool.get_company_info(symbol),
                self.technical_tool.get_signal_summary(symbol, start_date, end_date)
            ]
            
            stock_data, indicators, company_info, signals = await asyncio.gather(*tasks)
            
            return {
                "symbol": symbol.upper(),
                "period": f"{start_date} to {end_date}",
                "stock_data": stock_data,
                "technical_indicators": indicators,
                "company_info": company_info,
                "signal_summary": signals,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error aggregating market data for {symbol}: {e}")
            raise DataError(f"Failed to aggregate market data: {e}")
    
    async def get_quick_snapshot(self, symbol: str) -> dict:
        """Get a quick market snapshot for today."""
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        
        try:
            current_price = await self.yfinance_tool.get_current_price(symbol)
            signals = await self.technical_tool.get_signal_summary(symbol, start_date, end_date)
            
            return {
                "symbol": symbol.upper(),
                "current_price": current_price,
                "signals": signals,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting quick snapshot for {symbol}: {e}")
            return {"error": str(e)}
