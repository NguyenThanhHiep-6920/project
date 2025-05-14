from fastapi import FastAPI
import asyncio

from app.middleware.prometheus import setup_metrics_middleware
from app.routes.metrics import setup_metrics_routes
from app.routes.service_quality import setup_service_quality_routes
from app.routes.alerts import router as alerts_router
from app.graphql.schema import setup_graphql
from app.metrics.qos_monitor import update_qos_metrics_task
from app.alerting.alerting import alerting_task

# Khởi tạo ứng dụng FastAPI
app = FastAPI(title="Cloud Service Monitoring System", 
              description="Monitoring system for cloud services using Prometheus and FastAPI")

# Cài đặt middleware
setup_metrics_middleware(app)

# Cài đặt các routes
setup_metrics_routes(app)
setup_service_quality_routes(app)

app.include_router(alerts_router)

# Cài đặt GraphQL
setup_graphql(app)

# Khởi động các background tasks
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(update_qos_metrics_task())
    asyncio.create_task(alerting_task())                 #internal alerting python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
