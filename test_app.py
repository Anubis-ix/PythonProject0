import unittest
from main import app
import json

class TestBuildingApp(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_index(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_analyze_endpoint(self):
        test_data = {
            "safety": {
                "span": 10,
                "depth": 0.2,
                "material": "concrete",
                "floors": 1
            },
            "components": {
                "slab": {"thickness": 100, "span": 5},
                "column": {"height": 4, "width": 200},
                "stair": {"riser": 170, "tread": 280},
                "roof": {"pitch": 30, "type": "pitched"}
            },
            "energy": {
                "area": 100,
                "insulation": "low"
            }
        }
        response = self.app.post('/analyze', 
                                 data=json.dumps(test_data),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Check safety
        self.assertEqual(data['safety']['status'], 'Warning')
        
        # Check components
        self.assertIn("components", data)
        self.assertIn("Warning", data['components']['slab'])
        self.assertIn("Safe", data['components']['stair'])
        
        # Check energy
        self.assertEqual(data['energy']['annual_energy_kwh'], 20000)

    def test_chat_endpoint(self):
        # Test basic message
        response = self.app.post('/chat', data={'message': 'Hello'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("response", data)
        self.assertIn("Hello", data['response'])

    def test_file_upload_analysis(self):
        # Test file upload
        import io
        data = {
            'message': 'Analyze this plan',
            'file': (io.BytesIO(b"dummy drawing data"), 'plan.dwg')
        }
        response = self.app.post('/chat', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("AI Agent Analysis", data['response'])
        self.assertIn("plan.dwg", data['response'])
        self.assertIn("Load-Bearing Walls", data['response'])

if __name__ == '__main__':
    unittest.main()
