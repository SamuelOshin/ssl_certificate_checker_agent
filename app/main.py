"""
SSL Certificate Checker Agent - Main Application

FastAPI application for AI-powered SSL certificate checking via A2A protocol.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.general_routes import router as general_router
from app.routes.a2a_routes import router as a2a_router

# Create FastAPI application
app = FastAPI(
    title="SSL Certificate Checker Agent",
    description="AI-powered SSL certificate checking agent with A2A protocol support",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(general_router, prefix="", tags=["general"])
app.include_router(a2a_router, prefix="", tags=["a2a"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001)