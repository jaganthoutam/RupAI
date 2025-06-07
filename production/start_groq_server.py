#!/usr/bin/env python3
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
