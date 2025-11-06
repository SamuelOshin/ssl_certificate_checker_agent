"""
Routes package - exports all API routers
"""
from app.routes.general_routes import router as general_router

__all__ = ["general_router"]
