#!/usr/bin/env python
"""Wrapper script to run FastAPI server with proper import paths"""

import sys
import os
import uvicorn

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    uvicorn.run("src.monitoring.api:app", host="127.0.0.1", port=8000, reload=False)
