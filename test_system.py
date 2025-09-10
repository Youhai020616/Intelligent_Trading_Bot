"""
Test script for the Intelligent Trading Bot system.
"""

import asyncio
import sys
from pathlib import Path

# Add src directory to Python path
sys.path.append(str(Path(__file__).parent / "src"))

from config import config
from src.tools.toolkit import toolkit
from src.agents.analysts import analyst_team


async def test_configuration():
    """Test system configuration."""
    print("🔧 Testing Configuration...")
    
    # Validate API keys
    validation = config.validate_api_keys()
    for service, is_valid in validation.items():
        status = "✅" if is_valid else "❌"
        print(f"  {status} {service}")
    
    return all(validation.values())


async def test_toolkit():
    """Test the data acquisition toolkit."""
    print("\n🛠️ Testing Toolkit...")
    
    try:
        # Test health check
        health = await toolkit.health_check()
        print(f"  Overall Health: {'✅' if health['overall_health'] else '❌'}")
        
        # Test with a sample stock
        print("  Testing with AAPL...")
        snapshot = await toolkit.get_market_snapshot("AAPL")
        
        if "error" not in snapshot:
            print("  ✅ Market data retrieval successful")
        else:
            print(f"  ❌ Market data error: {snapshot['error']}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Toolkit test failed: {e}")
        return False


async def test_analysts():
    """Test the analyst team."""
    print("\n👥 Testing Analyst Team...")
    
    try:
        # Test individual analysts
        from datetime import datetime
        test_date = datetime.now().strftime("%Y-%m-%d")
        
        print("  Testing market analyst...")
        market_report = await analyst_team.market_analyst.analyze("AAPL", test_date)
        print(f"    ✅ Market analysis completed (confidence: {market_report['confidence']:.2f})")
        
        print("  Testing sentiment analyst...")
        sentiment_report = await analyst_team.sentiment_analyst.analyze("AAPL", test_date)
        print(f"    ✅ Sentiment analysis completed (confidence: {sentiment_report['confidence']:.2f})")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Analyst test failed: {e}")
        return False


async def test_full_analysis():
    """Test full analysis workflow."""
    print("\n🔍 Testing Full Analysis Workflow...")
    
    try:
        from datetime import datetime
        test_date = datetime.now().strftime("%Y-%m-%d")
        
        print("  Running team analysis for AAPL...")
        team_summary = await analyst_team.get_team_summary("AAPL", test_date)
        
        print(f"    ✅ Team analysis completed")
        print(f"    📊 Average confidence: {team_summary['team_summary']['average_confidence']:.2f}")
        print(f"    📈 Analysts completed: {team_summary['team_summary']['analysts_completed']}/4")
        
        # Show some findings
        findings = team_summary['team_summary']['key_findings'][:3]
        print("    🔍 Top findings:")
        for i, finding in enumerate(findings, 1):
            print(f"      {i}. {finding}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Full analysis test failed: {e}")
        return False


async def main():
    """Run all tests."""
    print("🤖 Intelligent Trading Bot - System Test")
    print("=" * 50)
    
    # Test configuration
    config_ok = await test_configuration()
    
    if not config_ok:
        print("\n❌ Configuration test failed. Please check your .env file.")
        print("Required API keys:")
        print("- OPENAI_API_KEY")
        print("- FINNHUB_API_KEY") 
        print("- TAVILY_API_KEY")
        return False
    
    # Test toolkit
    toolkit_ok = await test_toolkit()
    
    if not toolkit_ok:
        print("\n❌ Toolkit test failed. Check API connections.")
        return False
    
    # Test analysts
    analysts_ok = await test_analysts()
    
    if not analysts_ok:
        print("\n❌ Analyst test failed.")
        return False
    
    # Test full workflow
    workflow_ok = await test_full_analysis()
    
    if not workflow_ok:
        print("\n❌ Full workflow test failed.")
        return False
    
    print("\n🎉 All tests passed! System is ready.")
    print("\n📋 Next steps:")
    print("1. Implement research team and debate mechanism")
    print("2. Add trading execution and risk management")
    print("3. Integrate LangGraph workflow")
    print("4. Add memory and learning systems")
    
    return True


if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Unexpected error: {e}")
        sys.exit(1)
