"""
Setup script for the Intelligent Trading Bot system.
"""

import os
import sys
import subprocess
from pathlib import Path
from config import config

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required.")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version}")
    return True

def install_dependencies():
    """Install required Python packages."""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def setup_environment():
    """Setup environment configuration."""
    print("\n🔧 Setting up environment...")
    
    # Check if .env file exists
    if not Path(".env").exists():
        if Path(".env.example").exists():
            print("📝 Creating .env file from .env.example...")
            print("⚠️  Please edit .env file with your actual API keys!")
            
            # Copy .env.example to .env
            with open(".env.example", "r") as src, open(".env", "w") as dst:
                dst.write(src.read())
        else:
            print("❌ .env.example file not found!")
            return False
    
    # Validate API keys
    print("\n🔑 Validating API keys...")
    validation_results = config.validate_api_keys()
    
    all_valid = True
    for service, is_valid in validation_results.items():
        status = "✅" if is_valid else "❌"
        print(f"{status} {service}: {'Configured' if is_valid else 'Missing'}")
        if not is_valid:
            all_valid = False
    
    if not all_valid:
        print("\n⚠️  Some API keys are missing. Please update your .env file.")
        print("Required API keys:")
        print("- OpenAI API Key: https://platform.openai.com/api-keys")
        print("- Finnhub API Key: https://finnhub.io/register")
        print("- Tavily API Key: https://tavily.com/")
        print("- LangSmith API Key (optional): https://smith.langchain.com/")
    
    return True

def create_project_structure():
    """Create necessary project directories and files."""
    print("\n📁 Creating project structure...")
    
    directories = [
        "src",
        "src/agents",
        "src/tools", 
        "src/memory",
        "src/evaluation",
        "tests",
        "examples",
        "docs",
        "logs",
        "results",
        "data_cache",
        "memory_db"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        
        # Create __init__.py files for Python packages
        if directory.startswith("src"):
            init_file = Path(directory) / "__init__.py"
            if not init_file.exists():
                init_file.touch()
    
    print("✅ Project structure created.")
    return True

def create_main_entry_point():
    """Create the main entry point for the application."""
    main_content = '''"""
Main entry point for the Intelligent Trading Bot system.
"""

import asyncio
from pathlib import Path
import sys

# Add src directory to Python path
sys.path.append(str(Path(__file__).parent / "src"))

from config import config

def main():
    """Main entry point."""
    print("🤖 Intelligent Trading Bot System")
    print("=" * 50)
    
    # Setup LangSmith if configured
    config.setup_langsmith()
    
    # Validate configuration
    validation_results = config.validate_api_keys()
    missing_keys = [k for k, v in validation_results.items() if not v]
    
    if missing_keys:
        print("❌ Missing required API keys:")
        for key in missing_keys:
            print(f"   - {key}")
        print("\\nPlease update your .env file and try again.")
        return
    
    print("✅ Configuration validated successfully.")
    print("\\n🚀 System ready to start!")
    
    # TODO: Add actual system startup logic here
    print("\\n📝 Next steps:")
    print("1. Implement core data structures")
    print("2. Build data acquisition tools")
    print("3. Create agent implementations")
    print("4. Setup LangGraph workflow")

if __name__ == "__main__":
    main()
'''
    
    with open("main.py", "w") as f:
        f.write(main_content)
    
    print("✅ Main entry point created.")

def main():
    """Main setup function."""
    print("🤖 Intelligent Trading Bot - Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Install dependencies
    if not install_dependencies():
        return False
    
    # Setup environment
    if not setup_environment():
        return False
    
    # Create project structure
    if not create_project_structure():
        return False
    
    # Create main entry point
    create_main_entry_point()
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit .env file with your API keys")
    print("2. Run: python main.py")
    print("3. Start developing your trading agents!")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
