from fastapi import APIRouter
from app.alerting.alerting import alert_manager
from app.metrics.qos_monitor import qos_monitor

router = APIRouter()

@router.get("/alerts")
def get_alerts():
    """
    Trả về danh sách alert hiện tại (API REST cho admin kiểm tra nhanh)
    """
    metrics = qos_monitor.calculate_metrics()
    alerts = alert_manager.check_alerts(metrics)
    return {"alerts": alerts, "metrics": metrics}
