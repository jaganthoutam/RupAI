#!/usr/bin/env python3
"""
Groq AI Setup Script for MCP Payments Server
Automated installation and configuration of Groq AI integration.
"""

import os
import sys
import subprocess
import asyncio
from pathlib import Path

def print_banner():
    """Print setup banner."""
    print("🚀 Groq AI Integration Setup for MCP Payments Server")
    print("=" * 60)

def check_python_version():
    """Check Python version compatibility."""
    if sys.version_info < (3, 11):
        print("❌ Python 3.11+ required")
        print(f"   Current version: {sys.version}")
        return False
    
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def install_dependencies():
    """Install required dependencies."""
    print("\n📦 Installing Dependencies...")
    
    requirements = [
        "groq>=0.4.2",
        "httpx>=0.26.0", 
        "fastapi>=0.104.0",
        "uvicorn>=0.24.0",
        "pydantic>=2.5.0"
    ]
    
    for req in requirements:
        try:
            print(f"   Installing {req}...")
            subprocess.run([sys.executable, "-m", "pip", "install", req], 
                         check=True, capture_output=True, text=True)
            print(f"   ✅ {req} installed")
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Failed to install {req}: {e}")
            return False
    
    return True

def setup_environment():
    """Setup environment configuration."""
    print("\n🔧 Environment Setup...")
    
    env_file = Path(".env.groq")
    
    if env_file.exists():
        print("   .env.groq file already exists")
        return True
    
    env_content = """# Groq AI Configuration for MCP Payments
# Get your API key from: https://console.groq.com/

# Groq Configuration
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.1-8b-instant

# MCP Configuration  
MCP_ENDPOINT=http://localhost:8000/mcp

# FastAPI Server Configuration
HOST=0.0.0.0
PORT=8001
ENVIRONMENT=production
LOG_LEVEL=info
WORKERS=1

# Optional: Advanced Configuration
GROQ_TIMEOUT=30.0
GROQ_MAX_TOKENS=500
GROQ_TEMPERATURE=0.1
"""
    
    try:
        env_file.write_text(env_content)
        print(f"   ✅ Created {env_file}")
        print("   📝 Please edit .env.groq and add your Groq API key")
        return True
    except Exception as e:
        print(f"   ❌ Failed to create .env.groq: {e}")
        return False

async def test_mcp_connection():
    """Test MCP server connection."""
    print("\n🔗 Testing MCP Connection...")
    
    try:
        import httpx
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post("http://localhost:8000/mcp", json={
                "jsonrpc": "2.0",
                "id": "test",
                "method": "tools/list",
                "params": {}
            })
            
            if response.status_code == 200:
                result = response.json()
                tools_count = len(result.get("result", {}).get("tools", []))
                print(f"   ✅ MCP server connected ({tools_count} tools available)")
                return True
            else:
                print(f"   ❌ MCP server error: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"   ❌ MCP connection failed: {str(e)}")
        print("   💡 Make sure MCP server is running on localhost:8000")
        return False

async def test_groq_integration():
    """Test Groq integration."""
    print("\n🧠 Testing Groq Integration...")
    
    try:
        from groq_ai_integration import GroqProductionAI, PaymentContext, Currency, PaymentMethod
        
        # Test with demo mode (no API key required)
        async with GroqProductionAI() as groq_ai:
            test_context = PaymentContext(
                customer_id="test_customer",
                amount=100.00,
                currency=Currency.USD,
                method=PaymentMethod.CARD
            )
            
            decision = await groq_ai.process_payment_with_ai(test_context)
            
            print(f"   ✅ Groq integration test successful")
            print(f"   📊 Result: {'APPROVED' if decision.approve else 'BLOCKED'}")
            print(f"   ⚡ Processing time: {decision.processing_time_ms:.1f}ms")
            
            return True
            
    except Exception as e:
        print(f"   ❌ Groq integration test failed: {str(e)}")
        return False

def create_start_script():
    """Create start script for easy server launch."""
    print("\n📝 Creating Start Scripts...")
    
    start_script = Path("start_groq_server.py")
    script_content = """#!/usr/bin/env python3
import os
import uvicorn
from pathlib import Path

# Load environment variables
env_file = Path(".env.groq")
if env_file.exists():
    from dotenv import load_dotenv
    load_dotenv(env_file)

# Start server
if __name__ == "__main__":
    config = {
        "app": "groq_fastapi_server:app",
        "host": os.getenv("HOST", "0.0.0.0"), 
        "port": int(os.getenv("PORT", 8001)),
        "log_level": os.getenv("LOG_LEVEL", "info"),
        "reload": os.getenv("ENVIRONMENT") == "development"
    }
    
    print("🚀 Starting Groq AI FastAPI Server")
    print(f"   URL: http://{config['host']}:{config['port']}")
    print(f"   Environment: {os.getenv('ENVIRONMENT', 'production')}")
    
    uvicorn.run(**config)
"""
    
    try:
        start_script.write_text(script_content)
        start_script.chmod(0o755)
        print(f"   ✅ Created {start_script}")
        return True
    except Exception as e:
        print(f"   ❌ Failed to create start script: {e}")
        return False

def print_next_steps():
    """Print next steps for user."""
    print("\n✨ Setup Complete!")
    print("=" * 40)
    print("\n🎯 Next Steps:")
    print("1. Get your Groq API key from: https://console.groq.com/")
    print("2. Edit .env.groq and replace 'your_groq_api_key_here' with your actual key")
    print("3. Start the MCP payments server (if not already running)")
    print("4. Test the integration:")
    print("   python3 groq_ai_integration.py")
    print("5. Start the Groq FastAPI server:")
    print("   python3 start_groq_server.py")
    print("\n🌐 API Endpoints (after starting server):")
    print("   Health Check: http://localhost:8001/health")
    print("   Process Payment: http://localhost:8001/payments/process")
    print("   Batch Process: http://localhost:8001/payments/batch")
    print("   Analytics: http://localhost:8001/analytics/metrics")
    print("\n📚 Documentation:")
    print("   Read: GROQ_INTEGRATION_GUIDE.md")
    print("\n🎉 Happy Processing!")

async def main():
    """Main setup function."""
    print_banner()
    
    # Check prerequisites
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Dependency installation failed")
        sys.exit(1)
    
    # Setup environment
    if not setup_environment():
        print("❌ Environment setup failed")
        sys.exit(1)
    
    # Test MCP connection
    mcp_ok = await test_mcp_connection()
    
    # Test Groq integration
    groq_ok = await test_groq_integration()
    
    # Create start scripts
    script_ok = create_start_script()
    
    # Print results
    print("\n📋 Setup Summary:")
    print(f"   Dependencies: ✅ Installed")
    print(f"   Environment: ✅ Configured")
    print(f"   MCP Connection: {'✅ Connected' if mcp_ok else '⚠️  Check MCP server'}")
    print(f"   Groq Integration: {'✅ Working' if groq_ok else '❌ Check setup'}")
    print(f"   Start Scripts: {'✅ Created' if script_ok else '❌ Failed'}")
    
    if mcp_ok and groq_ok and script_ok:
        print("\n🎯 Status: READY FOR PRODUCTION!")
    else:
        print("\n⚠️  Status: Setup incomplete - see messages above")
    
    print_next_steps()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Setup cancelled by user")
    except Exception as e:
        print(f"\n❌ Setup failed: {str(e)}")
        sys.exit(1) 