import time
import threading
from analysis.analysis_manager import AnalysisManager

class AlertSystem:
    def __init__(self):
        self.analysis_manager = AnalysisManager()
        self.alert_rules = {}
        self.alert_history = []
        self.running = False
        self.check_interval = 60  # Check every 60 seconds
    
    def add_alert_rule(self, symbol, rule_type, threshold, direction):
        """添加预警规则"""
        if symbol not in self.alert_rules:
            self.alert_rules[symbol] = []
        
        rule = {
            "rule_type": rule_type,
            "threshold": threshold,
            "direction": direction,
            "last_triggered": None
        }
        
        self.alert_rules[symbol].append(rule)
        return f"Alert rule added for {symbol}: {rule_type} {direction} {threshold}"
    
    def remove_alert_rule(self, symbol, rule_index):
        """移除预警规则"""
        if symbol in self.alert_rules and 0 <= rule_index < len(self.alert_rules[symbol]):
            self.alert_rules[symbol].pop(rule_index)
            return f"Alert rule removed for {symbol}"
        return f"Invalid alert rule index for {symbol}"
    
    def check_alerts(self):
        """检查预警条件"""
        for symbol, rules in self.alert_rules.items():
            try:
                # Get technical analysis results
                analysis_result = self.analysis_manager.technical_analysis(symbol)
                
                for rule in rules:
                    rule_type = rule["rule_type"]
                    threshold = rule["threshold"]
                    direction = rule["direction"]
                    
                    # Check if the rule condition is met
                    if self._check_rule_condition(analysis_result, rule_type, threshold, direction):
                        alert_message = f"ALERT: {symbol} - {rule_type} {direction} {threshold} at {time.strftime('%Y-%m-%d %H:%M:%S')}"
                        self.alert_history.append(alert_message)
                        self._send_alert(alert_message)
                        rule["last_triggered"] = time.time()
            except Exception as e:
                print(f"Error checking alerts for {symbol}: {e}")
    
    def _check_rule_condition(self, analysis_result, rule_type, threshold, direction):
        """检查规则条件是否满足"""
        if rule_type not in analysis_result:
            return False
        
        value = analysis_result[rule_type]
        
        if direction == "above":
            return value > threshold
        elif direction == "below":
            return value < threshold
        elif direction == "cross_above":
            # Need historical data to check cross above
            return False
        elif direction == "cross_below":
            # Need historical data to check cross below
            return False
        return False
    
    def _send_alert(self, message):
        """发送预警消息"""
        # In a real system, this could send emails, SMS, or push notifications
        print(f"SENDING ALERT: {message}")
        # For demonstration purposes, we'll just print the alert
    
    def start_monitoring(self):
        """开始监控"""
        if not self.running:
            self.running = True
            self.monitoring_thread = threading.Thread(target=self._monitoring_loop)
            self.monitoring_thread.daemon = True
            self.monitoring_thread.start()
            return "Alert system started"
        return "Alert system is already running"
    
    def stop_monitoring(self):
        """停止监控"""
        if self.running:
            self.running = False
            self.monitoring_thread.join()
            return "Alert system stopped"
        return "Alert system is not running"
    
    def _monitoring_loop(self):
        """监控循环"""
        while self.running:
            self.check_alerts()
            time.sleep(self.check_interval)
    
    def get_alert_history(self, limit=10):
        """获取预警历史"""
        return self.alert_history[-limit:]
    
    def get_active_rules(self):
        """获取活跃的预警规则"""
        return self.alert_rules
