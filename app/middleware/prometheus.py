from fastapi import FastAPI, Request, Response
from starlette.responses import JSONResponse
from starlette.responses import Response as StarletteResponse
import json
import time
from app.metrics.prometheus_metrics import (
    REQUEST_COUNT, REQUEST_LATENCY, REQUEST_IN_PROGRESS, 
    REQUEST_SIZE, RESPONSE_SIZE
)
from app.metrics.qos_monitor import qos_monitor
import logging

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def prometheus_middleware(request: Request, call_next):
    """
    Middleware để theo dõi các metrics của request HTTP
    """
    start_time = time.time()
    
    # Tăng số lượng request đang xử lý
    REQUEST_IN_PROGRESS.labels(method=request.method, endpoint=request.url.path).inc()
    
    # Đo kích thước request
    content_length = int(request.headers.get("content-length", 0))
    REQUEST_SIZE.labels(method=request.method, endpoint=request.url.path).observe(content_length)
    
    try:
        # Gọi route chính và lấy response
        response = await call_next(request)

        # Capture body từ response
        #raw_body = b"".join([section async for section in response.body_iterator])
        #full_response = StarletteResponse(content=raw_body, status_code=response.status_code, headers=dict(response.headers))
        
        # Ghi nhận thời gian xử lý
        process_time = time.time() - start_time
        REQUEST_LATENCY.labels(method=request.method, endpoint=request.url.path).observe(process_time)
        
        # Đếm số lượng request theo status code
        REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path, status_code=response.status_code).inc()
        
        # Đo kích thước response
        resp_size = int(response.headers.get("content-length", 0))
        RESPONSE_SIZE.labels(method=request.method, endpoint=request.url.path).observe(resp_size)
        
        is_error = response.status_code >= 400

        # # Nếu là lỗi ở /graphql và vẫn trả HTTP 200
        # if request.url.path == "/graphql" and response.status_code == 200:
        #     try:
        #         json_body = json.loads(raw_body.decode())
        #         if "errors" in json_body:
        #             error_message = json_body["errors"][0].get("message", "GraphQL Error")
        #             operation_name = json_body.get("errors")[0].get("path", ["anonymous"])[0]
        #             qos_monitor.record_request(
        #                 process_time,
        #                 is_error=True,
        #                 error_details={
        #                     "error_type": error_message,
        #                     "operation_name": str(operation_name),
        #                 }
        #             )
        #             return full_response
        #     except Exception as gql_parse_error:
        #         pass  # nếu không phân tích được thì bỏ qua

        qos_monitor.record_request(
            process_time,
            is_error,
            error_details={
                "error_type": str(response.status_code),
                "operation_name": request.url.path
            }
        )
        return response
    except Exception as e:
        qos_monitor.record_request(
            time.time() - start_time,
            True,
            error_details={
                "error_type": "UnhandledException",
                "operation_name": request.url.path
            }
        )
        logger.error(f"Unhandled exception: {str(e)}")
        raise
    finally:
        # Giảm số lượng request đang xử lý khi hoàn thành
        REQUEST_IN_PROGRESS.labels(method=request.method, endpoint=request.url.path).dec()

def setup_metrics_middleware(app: FastAPI):
    """
    Cài đặt middleware cho ứng dụng
    """
    app.middleware("http")(prometheus_middleware)











