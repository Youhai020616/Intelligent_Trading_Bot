# 🤖 Intelligent Trading Bot

A sophisticated multi-agent quantitative trading system built with LangGraph, featuring collaborative AI agents that simulate a real investment firm's decision-making process.

## 🌟 Features

- **Multi-Agent Architecture**: Specialized agents for market analysis, research, trading, and risk management
- **Adversarial Debate System**: Bull vs Bear researchers engage in structured debates for balanced decision-making
- **Long-term Memory**: ChromaDB-powered memory system for learning from past decisions
- **Real-time Data Integration**: Multiple data sources including market data, news, and social sentiment
- **Risk Management**: Multi-perspective risk assessment with conservative, aggressive, and neutral viewpoints
- **Comprehensive Evaluation**: Multi-dimensional system performance assessment

## 🏗️ System Architecture

```
Portfolio Manager (Supervisor)
├── Research Team
│   ├── Market Analyst (Technical indicators)
│   ├── Social Media Analyst (Sentiment analysis)
│   ├── News Analyst (News & macro events)
│   └── Fundamentals Analyst (Company financials)
├── Investment Team
│   ├── Bull Researcher (Optimistic perspective)
│   ├── Bear Researcher (Pessimistic perspective)
│   └── Research Manager (Synthesis & decision)
├── Trading Team
│   └── Trader (Execution planning)
└── Risk Management Team
    ├── Risky Analyst (Aggressive approach)
    ├── Safe Analyst (Conservative approach)
    └── Neutral Analyst (Balanced approach)
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- API keys for:
  - [OpenAI](https://platform.openai.com/api-keys)
  - [Finnhub](https://finnhub.io/register)
  - [Tavily](https://tavily.com/)
  - [LangSmith](https://smith.langchain.com/) (optional but recommended)

### Installation

1. **Clone and setup the project:**
   ```bash
   git clone <repository-url>
   cd Intelligent_Trading_Bot
   python setup.py
   ```

2. **Configure your API keys:**
   ```bash
   # Edit the .env file with your actual API keys
   cp .env.example .env
   nano .env  # or use your preferred editor
   ```

3. **Run the system:**
   ```bash
   python main.py
   ```

## 📊 Usage Examples

### Basic Trading Analysis

```python
from src.trading_system import TradingSystem

# Initialize the system
trading_system = TradingSystem()

# Analyze a stock
result = await trading_system.analyze_stock(
    ticker="NVDA",
    trade_date="2024-12-06"
)

print(f"Trading Signal: {result['final_signal']}")
print(f"Decision Rationale: {result['decision_rationale']}")
```

### Custom Agent Configuration

```python
from src.agents import create_custom_analyst

# Create a specialized crypto analyst
crypto_analyst = create_custom_analyst(
    name="crypto_analyst",
    specialization="cryptocurrency",
    tools=["crypto_data", "defi_metrics", "social_sentiment"]
)

# Add to the system
trading_system.add_agent(crypto_analyst)
```

## 🔧 Configuration

Key configuration options in `.env`:

```bash
# Model Configuration
DEEP_THINK_LLM=gpt-4o          # For complex reasoning
QUICK_THINK_LLM=gpt-4o-mini    # For data processing

# System Behavior
MAX_DEBATE_ROUNDS=2            # Bull vs Bear debate rounds
MAX_RISK_DISCUSS_ROUNDS=1      # Risk management discussions
ONLINE_TOOLS=true              # Use real-time data vs cache

# Performance Tuning
USE_CACHE=true                 # Enable intelligent caching
LLM_TEMPERATURE=0.1            # Lower = more deterministic
```

## 📈 System Workflow

1. **Data Collection**: Parallel gathering of market data, news, sentiment, and fundamentals
2. **Research Phase**: Bull and Bear researchers engage in structured debate
3. **Strategy Formation**: Research manager synthesizes perspectives into investment thesis
4. **Execution Planning**: Trader converts strategy into actionable plan
5. **Risk Assessment**: Multi-perspective risk evaluation and mitigation
6. **Final Decision**: Portfolio manager makes binding trading decision
7. **Learning**: System stores experience for future reference

## 🧪 Testing

```bash
# Run unit tests
pytest tests/

# Run integration tests
pytest tests/integration/

# Run with coverage
pytest --cov=src tests/
```

## 📊 Monitoring & Evaluation

The system includes comprehensive evaluation mechanisms:

- **LLM-as-a-Judge**: Qualitative assessment of decision reasoning
- **Ground Truth Comparison**: Performance against actual market outcomes
- **Fact Checking**: Validation of data accuracy and consistency

View results in the LangSmith dashboard for detailed execution traces.

## 🛡️ Risk Management

- **Position Sizing**: Automated risk-adjusted position calculations
- **Stop Losses**: Dynamic stop-loss and take-profit levels
- **Exposure Limits**: Portfolio-level risk constraints
- **Scenario Analysis**: Multi-perspective risk assessment

## 🔄 Continuous Learning

The system learns from each decision through:

- **Memory Storage**: ChromaDB vector database for experience retention
- **Pattern Recognition**: Identification of successful strategies
- **Performance Feedback**: Integration of actual trading outcomes
- **Strategy Refinement**: Continuous improvement of decision-making

## 📚 Documentation

- [Architecture Guide](docs/architecture.md)
- [Agent Development](docs/agents.md)
- [API Reference](docs/api.md)
- [Deployment Guide](docs/deployment.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## ⚠️ Disclaimer

This system is for educational and research purposes. Always:
- Validate all trading decisions independently
- Start with paper trading
- Understand the risks involved
- Comply with applicable regulations

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Built with:
- [LangGraph](https://github.com/langchain-ai/langgraph) - Multi-agent orchestration
- [LangChain](https://github.com/langchain-ai/langchain) - LLM framework
- [ChromaDB](https://github.com/chroma-core/chroma) - Vector database
- [yfinance](https://github.com/ranaroussi/yfinance) - Market data
