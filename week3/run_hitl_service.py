#!/usr/bin/env python3
"""Entry point for the HITL Queue FastAPI service."""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "hitl_service.main:app",
        host="0.0.0.0",
        port=8001,
        reload=False,
    )
