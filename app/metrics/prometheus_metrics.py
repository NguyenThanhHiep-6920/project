from prometheus_client import Counter, Histogram, Gauge, Summary

# Các metrics cơ bản cho HTTP requests
REQUEST_COUNT = Counter("http_requests_total", "Total HTTP Requests Count", ["method", "endpoint", "status_code"])
REQUEST_LATENCY = Histogram("http_request_duration_seconds", "HTTP Request Latency", ["method", "endpoint"])
REQUEST_IN_PROGRESS = Gauge("http_requests_in_progress", "HTTP Requests currently in progress", ["method", "endpoint"])
REQUEST_SIZE = Summary("http_request_size_bytes", "HTTP Request Size in bytes", ["method", "endpoint"])
RESPONSE_SIZE = Summary("http_response_size_bytes", "HTTP Response Size in bytes", ["method", "endpoint"])

# Các metrics cho GraphQL
GQL_QUERY_COUNT = Counter("graphql_query_total", "Total GraphQL Query Count", ["operation_name", "operation_type"])
GQL_QUERY_LATENCY = Histogram("graphql_query_duration_seconds", "GraphQL Query Latency", ["operation_name", "operation_type"])
GQL_ERRORS = Counter("graphql_errors_total", "Total GraphQL Errors", ["operation_name", "error_type"])
GQL_FIELDS_ACCESSED = Counter("graphql_fields_accessed_total", "GraphQL Fields Accessed Count", ["field_name"])



# Các metrics cho QoS (Quality of Service)
QOS_AVAILABILITY = Gauge("service_availability_percent", "Service Availability Percentage")
QOS_AVG_RESPONSE_TIME = Gauge("service_average_response_time_seconds", "Average Response Time")
QOS_P95_RESPONSE_TIME = Gauge("service_p95_response_time_seconds", "95th Percentile Response Time")
QOS_P99_RESPONSE_TIME = Gauge("service_p99_response_time_seconds", "99th Percentile Response Time")
QOS_ERROR_RATE = Gauge("service_error_rate", "Service Error Rate")
QOS_REQUEST_RATE = Gauge("service_request_rate", "Requests per Second")

