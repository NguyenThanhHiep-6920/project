import time
import statistics
import asyncio
from typing import List, Dict, Tuple, Any, Optional
import logging
from app.metrics.prometheus_metrics import (
    QOS_AVAILABILITY, QOS_AVG_RESPONSE_TIME, QOS_P95_RESPONSE_TIME,
    QOS_P99_RESPONSE_TIME, QOS_ERROR_RATE, QOS_REQUEST_RATE,
)

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ServiceQualityMonitor:
    """
    Lớp giám sát chất lượng dịch vụ dựa trên các metrics
    """
    def __init__(self, availability_window: int = 60 * 5):
        """
        Khởi tạo monitor với các thông số mặc định
        
        Args:
            availability_window: Cửa sổ thời gian để tính toán metrics, mặc định là 5 phút
        """
        self.response_times: List[float] = []
        self.error_counts: int = 0
        self.request_counts: int = 0
        self.availability_window: int = availability_window
        self.response_time_with_timestamp: List[Tuple[float, float]] = []  # (timestamp, response_time)
        self.last_check_time = time.time()
        #update error details với format (timestamp, error_type, operation_name)
        self.error_details: List[Tuple[float, str, str]] = [] 
    
    def record_request(self, response_time: float, is_error: bool, 
                       error_details: Optional[Dict[str, Any]] = None):
        """
        Ghi nhận thông tin về một request với chi tiết lỗi nếu có
        
        Args:
            response_time: Thời gian phản hồi của request (ms)
            is_error: Cờ đánh dấu request có bị lỗi không
            error_details: Chi tiết lỗi nếu có, với các khóa như code, endpoint, method, message
        """
        current_time = time.time()
        self.response_times.append(response_time)
        self.response_time_with_timestamp.append((current_time, response_time))
        self.request_counts += 1
        
        if is_error and error_details:
            error_type = error_details.get("error_type", "unknown")
            operation_name = error_details.get("operation_name", "unknown")
            self.error_details.append((current_time, error_type, operation_name))

        
        # Định kỳ dọn dẹp dữ liệu cũ
        if current_time - self.last_check_time > 60:  # Kiểm tra mỗi phút
            self.cleanup_old_data()
            self.last_check_time = current_time
    
    def cleanup_old_data(self):
        """
        Loại bỏ dữ liệu cũ ngoài cửa sổ thời gian
        """
        cutoff_time = time.time() - self.availability_window
        
        # Loại bỏ dữ liệu phản hồi cũ dựa trên timestamp
        new_data = [(ts, rt) for ts, rt in self.response_time_with_timestamp if ts >= cutoff_time]
        
        # Loại bỏ dữ liệu lỗi cũ dựa trên timestamp
        new_errors = [(ts, etype, opname) for ts, etype, opname in self.error_details if ts >= cutoff_time]

        self.response_time_with_timestamp = new_data
        self.response_times = [rt for _, rt in new_data]
        self.error_details = new_errors
        self.error_counts = len(new_errors)
        self.request_counts = len(new_data)

            
    
    def calculate_metrics(self) -> Dict:
        """
        Tính toán các metrics chất lượng dịch vụ với phân tích chi tiết về lỗi
        
        Returns:
            Dict chứa các metrics và phân tích về lỗi
        """
        if not self.response_times:
            return {
                "availability": 100.0,
                "average_response_time": 0,
                "p95_response_time": 0,
                "p99_response_time": 0,
                "error_rate": 0,
                "request_rate": 0,
                "latest_errors": []
            }
        
        # Tính toán các metrics
        availability = 100.0 * (1 - self.error_counts / max(1, self.request_counts))
        avg_response_time = statistics.mean(self.response_times)
        
        # Tính percentiles
        sorted_times = sorted(self.response_times)
        p95_index = int(0.95 * len(sorted_times))
        p99_index = int(0.99 * len(sorted_times))
        
        p95_response_time = sorted_times[p95_index] if p95_index < len(sorted_times) else sorted_times[-1]
        p99_response_time = sorted_times[p99_index] if p99_index < len(sorted_times) else sorted_times[-1]
        
        error_rate = self.error_counts / max(1, self.request_counts)
        request_rate = self.request_counts / self.availability_window
        
        latest_errors = [{
            "timestamp": ts,
            "error_type": etype,
            "operation_name": opname
        } for ts, etype, opname in sorted(self.error_details, key=lambda x: x[0], reverse=True)[:10]]
        
        return {
            "availability": availability,
            "average_response_time": avg_response_time,
            "p95_response_time": p95_response_time,
            "p99_response_time": p99_response_time,
            "error_rate": error_rate,
            "request_rate": request_rate,
            "latest_errors": latest_errors
        }

# Khởi tạo monitor toàn cục
qos_monitor = ServiceQualityMonitor()

async def update_qos_metrics_task():
    """
    Task nền để cập nhật metrics QoS trong Prometheus
    """
    while True:
        try:
            metrics = qos_monitor.calculate_metrics()
            
            # Cập nhật các metrics cơ bản vào Prometheus
            QOS_AVAILABILITY.set(metrics["availability"])
            QOS_AVG_RESPONSE_TIME.set(metrics["average_response_time"])
            QOS_P95_RESPONSE_TIME.set(metrics["p95_response_time"])
            QOS_P99_RESPONSE_TIME.set(metrics["p99_response_time"])
            QOS_ERROR_RATE.set(metrics["error_rate"])
            QOS_REQUEST_RATE.set(metrics["request_rate"])
            logger.info(f"Updated QoS metrics: {metrics}")
        except Exception as e:
            logger.error(f"Error updating QoS metrics: {str(e)}")
        await asyncio.sleep(15)