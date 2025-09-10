# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a sophisticated multi-agent quantitative trading system that simulates an investment firm's decision-making process using LangGraph for AI agent orchestration. The system combines Python backend processing with a React TypeScript frontend for a complete trading intelligence platform.

## Development Commands

### Backend Development
```bash
# Install dependencies and setup
python setup.py

# Run the main system
python main.py

# Run tests
pytest tests/
pytest tests/integration/
pytest --cov=src tests/

# Run with specific test categories
pytest -v tests/unit/
pytest -v tests/integration/
```

### Frontend Development
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Development server
npm run dev

# Build for production
npm run build

# Run tests
npm test
npm run test:coverage
npm run test:ui

# Linting
npm run lint

# Preview production build
npm run preview
```

### Code Quality
```bash
# Backend type checking (if mypy is added)
mypy src/

# Frontend type checking
cd frontend && npm run build  # Includes TypeScript compilation

# Linting
cd frontend && npm run lint
```

## Architecture Overview

### Multi-Agent System Architecture
The system implements a hierarchical multi-agent workflow that mirrors a real investment firm:

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

### Backend Structure (Python)
- **Entry Point**: `main.py` - System initialization and validation
- **Configuration**: `config.py` - Environment-based configuration with API key management
- **Core Modules**: 
  - `src/workflow/graph.py` - LangGraph workflow orchestration
  - `src/database/models.py` - SQLAlchemy ORM models
  - `src/agents/` - Individual agent implementations
  - `src/tools/` - Data acquisition and analysis tools
  - `src/memory/` - ChromaDB vector database integration

### Frontend Structure (React/TypeScript)
- **Build Tool**: Vite with TypeScript
- **UI Framework**: Material-UI v6 with Tailwind CSS
- **State Management**: Redux Toolkit
- **Routing**: React Router DOM
- **Charts**: Recharts + MUI X Charts
- **Real-time**: Socket.io client for live updates

## Key Technical Components

### LangGraph Workflow System
The trading decision workflow follows a structured sequence:
1. **Analyst Team Analysis** - Parallel data collection from multiple sources
2. **Research Manager Synthesis** - Bull vs Bear debate and strategy formation
3. **Trader Plan Creation** - Convert strategy to executable plans
4. **Risk Team Assessment** - Multi-perspective risk evaluation
5. **Portfolio Manager Decision** - Final binding trading decision
6. **Data Storage** - Store results and learn from outcomes

### Database Models (SQLAlchemy)
- **TradingSession**: Manages trading sessions with P&L tracking
- **Trade**: Individual trade records with order details
- **MarketData**: Historical market data storage
- **AgentDecision**: Logs all AI agent decisions for auditability
- **SystemLog**: Comprehensive system logging

### Configuration Management
- **Environment-based config** with .env file support
- **API Key management** for OpenAI, Finnhub, Tavily, and LangSmith
- **Tunable parameters**: debate rounds, risk tolerance, model selection
- **Directory management** with auto-creation

## Development Guidelines

### Working with Agents
- Each agent has specific tools and responsibilities
- Agents communicate through structured messages in the LangGraph workflow
- Agent decisions are logged for auditability and learning
- Use the existing agent patterns when creating new specialists

### Data Flow Patterns
- Market data flows through Finnhub and Yahoo Finance APIs
- News and sentiment analysis via Tavily API
- Long-term memory stored in ChromaDB vector database
- Real-time updates through WebSocket connections

### Frontend Development
- Use Material-UI components with Tailwind CSS for styling
- Implement responsive design with mobile-first approach
- Use Redux Toolkit for state management
- Follow the established component structure in `frontend/src/components/`

### Backend Development
- Use SQLAlchemy ORM for database operations
- Implement async/await patterns for API calls
- Use Pydantic models for data validation
- Follow LangGraph patterns for agent workflows

## Configuration Requirements

### Required API Keys
- **OpenAI API Key**: For LLM reasoning (GPT-4o for deep thinking, GPT-4o-mini for quick tasks)
- **Finnhub API Key**: Real-time market data and financial information
- **Tavily API Key**: News search and web content analysis
- **LangSmith API Key**: Optional but recommended for observability

### Environment Variables
Key configuration options in `.env`:
```bash
# Model Configuration
DEEP_THINK_LLM=gpt-4o
QUICK_THINK_LLM=gpt-4o-mini

# System Behavior
MAX_DEBATE_ROUNDS=2
MAX_RISK_DISCUSS_ROUNDS=1
ONLINE_TOOLS=true
USE_CACHE=true
LLM_TEMPERATURE=0.1
```

## Testing Strategy

### Backend Testing
- Use pytest for unit and integration tests
- Test agent workflows and decision-making logic
- Mock external API calls for reliable testing
- Validate database models and operations

### Frontend Testing
- Use Vitest with React Testing Library
- Test component rendering and user interactions
- Test Redux store state management
- Implement integration tests for API calls

## Common Development Patterns

### Adding New Agents
1. Create agent class in `src/agents/`
2. Define specialized tools and capabilities
3. Register agent in the LangGraph workflow
4. Add corresponding frontend UI components

### Working with Market Data
1. Use existing data acquisition tools in `src/tools/`
2. Implement caching strategies for performance
3. Handle API rate limits and errors gracefully
4. Store historical data in the database

### Frontend-Backend Integration
1. Use RESTful API patterns for data exchange
2. Implement WebSocket connections for real-time updates
3. Handle loading states and error conditions
4. Use TypeScript interfaces for type safety

## File Structure Conventions

### Backend
- `src/agents/` - Individual agent implementations
- `src/tools/` - Data acquisition and analysis tools
- `src/workflow/` - LangGraph workflow definitions
- `src/database/` - Database models and operations
- `src/memory/` - ChromaDB integration for long-term memory
- `tests/` - Test files organized by component

### Frontend
- `frontend/src/components/` - Reusable UI components
- `frontend/src/pages/` - Route-level components
- `frontend/src/store/` - Redux state management
- `frontend/src/utils/` - Utility functions and helpers
- `frontend/src/lib/` - External library integrations

## Performance Considerations

### Backend Optimization
- Use async/await for non-blocking operations
- Implement intelligent caching for API calls
- Optimize database queries with proper indexing
- Use connection pooling for database connections

### Frontend Optimization
- Implement code splitting for large components
- Use React.memo for expensive components
- Optimize chart rendering with virtualization
- Implement proper error boundaries

## Security Considerations

- Never commit API keys or sensitive configuration
- Use environment variables for all secrets
- Implement proper input validation for user data
- Use HTTPS for all API communications
- Implement rate limiting for external API calls