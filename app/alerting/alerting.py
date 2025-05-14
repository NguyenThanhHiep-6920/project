# app/alerting/alerting.py

import time
import logging
import asyncio
from app.metrics.qos_monitor import qos_monitor

logger = logging.getLogger("alerting")

class AlertingRule:
    def __init__(self, name, metric_key, threshold, comparison, description):
        self.name = name
        self.metric_key = metric_key
        self.threshold = threshold
        self.comparison = comparison  # 'gt' or 'lt'
        self.description = description

    def evaluate(self, metrics):
        value = metrics.get(self.metric_key, None)
        if value is None:
            return False, f"Metric {self.metric_key} not found"
        
        if self.comparison == 'gt' and value > self.threshold:
            return True, f"{self.name} breached: {value} > {self.threshold} ({self.description})"
        elif self.comparison == 'lt' and value < self.threshold:
            return True, f"{self.name} breached: {value} < {self.threshold} ({self.description})"
        
        return False, ""

class AlertManager:
    def __init__(self):
        self.rules = []

    def add_rule(self, rule):
        self.rules.append(rule)

    def check_alerts(self, metrics):
        alerts = []
        for rule in self.rules:
            triggered, message = rule.evaluate(metrics)
            if triggered:
                alerts.append(message)
        return alerts

alert_manager = AlertManager()

# Định nghĩa SLO threshold
alert_manager.add_rule(AlertingRule("Availability SLO", "availability", 99.0, 'lt', "Service availability below 99%"))
alert_manager.add_rule(AlertingRule("Error Rate SLO", "error_rate", 0.01, 'gt', "Error rate above 1%"))
alert_manager.add_rule(AlertingRule("P95 Latency SLO", "p95_response_time", 1.0, 'gt', "P95 latency above 1 second"))

async def alerting_task():
    while True:
        try:
            metrics = qos_monitor.calculate_metrics()
            alerts = alert_manager.check_alerts(metrics)
            
            for alert in alerts:
                logger.warning(f"ALERT: {alert}")
            
            if not alerts:
                logger.info("All SLO within expected thresholds")
                
        except Exception as e:
            logger.error(f"Error in alerting task: {str(e)}")
        
        await asyncio.sleep(30)  # Check every 30 seconds
