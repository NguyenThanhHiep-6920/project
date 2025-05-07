from fastapi import FastAPI, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

def setup_metrics_routes(app: FastAPI):
    """
    Cài đặt route /metrics cho Prometheus
    """
    @app.get("/metrics")
    def metrics():
        """
        Endpoint để Prometheus scrape metrics
        """
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)