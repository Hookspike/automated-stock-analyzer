import unittest
from application.app import app
from application.alert.alert_system import AlertSystem
from fastapi.testclient import TestClient

class TestApplication(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.alert_system = AlertSystem()
    
    def test_root_endpoint(self):
        """测试根端点"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json())
        self.assertEqual(response.json()["message"], "Stock Analysis and Prediction System API")
    
    def test_health_check_endpoint(self):
        """测试健康检查端点"""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertIn("status", response.json())
        self.assertEqual(response.json()["status"], "healthy")
    
    def test_alert_system(self):
        """测试预警系统"""
        # Add an alert rule
        result = self.alert_system.add_alert_rule("600519", "rsi", 70, "above")
        self.assertIn("Alert rule added", result)
        
        # Check active rules
        rules = self.alert_system.get_active_rules()
        self.assertIn("600519", rules)
        self.assertEqual(len(rules["600519"]), 1)
        
        # Remove the alert rule
        result = self.alert_system.remove_alert_rule("600519", 0)
        self.assertIn("Alert rule removed", result)
        
        # Check active rules again
        rules = self.alert_system.get_active_rules()
        self.assertIn("600519", rules)
        self.assertEqual(len(rules["600519"]), 0)

if __name__ == "__main__":
    unittest.main()
