import functools
import time
from app.metrics.prometheus_metrics import (
    GQL_QUERY_COUNT, GQL_QUERY_LATENCY, GQL_ERRORS, GQL_FIELDS_ACCESSED
)

from app.metrics.qos_monitor import qos_monitor

def gql_metrics_decorator(resolver_func):
    """
    Decorator để đo lường metrics cho GraphQL resolvers
    """
    @functools.wraps(resolver_func)
    async def wrapper(obj, info, **kwargs):
        # Lấy thông tin về operation
        operation_name = "anonymous"
        operation_type = "query"
        
        if info.operation and hasattr(info.operation, "name") and info.operation.name:
            operation_name = info.operation.name.value
        
        if info.operation and hasattr(info.operation, "operation"):
            operation_type = info.operation.operation.value
            
        field_name = info.field_name
        
        # Đếm truy cập field
        GQL_FIELDS_ACCESSED.labels(field_name=field_name).inc()
        
        # Đếm số lượng query
        GQL_QUERY_COUNT.labels(operation_name=operation_name, operation_type=operation_type).inc()
        
        start_time = time.time()
        try:
            # Gọi resolver gốc
            result = await resolver_func(obj, info, **kwargs)
            return result
        except Exception as e:
            # Ghi nhận lỗi
            error_type = e.__class__.__name__
            GQL_ERRORS.labels(operation_name=operation_name, error_type=error_type).inc()

            # Ghi chi tiết lỗi vào QoS Monitor
            qos_monitor.record_request(
                response_time=time.time() - start_time,
                is_error=True,
                error_details={
                    "error_type": error_type,
                    "operation_name": operation_name
                }
            )
            raise
        finally:
            # Ghi nhận thời gian xử lý
            execution_time = time.time() - start_time
            GQL_QUERY_LATENCY.labels(operation_name=operation_name, operation_type=operation_type).observe(execution_time)
            
    return wrapper

def monitor_gql_container(container_class):
    """
    Decorator để giám sát GraphQL container
    """
    original_init = container_class.__init__
    
    @functools.wraps(original_init)
    def new_init(self, *args, **kwargs):
        # Gọi hàm khởi tạo gốc
        original_init(self, *args, **kwargs)
        
        # Áp dụng metrics decorator cho tất cả các phương thức resolver
        for attr_name in dir(self):
            if attr_name.startswith('resolve_'):
                attr = getattr(self, attr_name)
                if callable(attr):
                    setattr(self, attr_name, gql_metrics_decorator(attr))
    
    container_class.__init__ = new_init
    return container_class