from fastapi import FastAPI
from app.metrics.qos_monitor import qos_monitor

def setup_service_quality_routes(app: FastAPI):
    """
    Cài đặt routes liên quan đến chất lượng dịch vụ
    """
    @app.get("/service-quality")
    def get_service_quality():
        """
        Endpoint để lấy metrics về chất lượng dịch vụ hiện tại
        """
        return qos_monitor.calculate_metrics()
    
    @app.get("/health")
    def health_check():
        """
        Endpoint kiểm tra sức khỏe của service
        """
        metrics = qos_monitor.calculate_metrics()
        is_healthy = metrics["availability"] >= 99.0  # Ngưỡng tính khả dụng
        
        if is_healthy:
            return {"status": "healthy", "metrics": metrics}
        else:
            return {"status": "unhealthy", "metrics": metrics}