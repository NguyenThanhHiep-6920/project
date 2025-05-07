# app/routes/__init__.py
from app.routes.metrics import setup_metrics_routes
from app.routes.service_quality import setup_service_quality_routes

__all__ = ["setup_metrics_routes", "setup_service_quality_routes"]