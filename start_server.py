#!/usr/bin/env python3
"""Start the API server"""
import uvicorn
from src.api.main import app

if __name__ == "__main__":
    print("🚀 Starting Retail Meme Stock Analyzer API Server...")
    print("📡 Server will be available at: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("\n🌐 To view the dashboard:")
    print("   1. Keep this server running")
    print("   2. Open src/dashboard/simple_dashboard.html in your browser")
    print("\n⚡ Press Ctrl+C to stop the server\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)