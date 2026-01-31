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
                "stair": {"riser": 170, "tread": 280}
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
        self.assertIn("Warning", data['components']['One-way Slab'])
        self.assertIn("Safe", data['components']['Stair'])
        
        # Check energy (OpenBEM logic)
        self.assertIn("sap_rating", data['energy'])
        self.assertGreater(data['energy']['annual_energy_kwh'], 0)

    def test_new_components(self):
        test_data = {
            "safety": {"span": 5, "depth": 0.5, "material": "concrete", "floors": 1},
            "components": {
                "slab": {"thickness": 200, "span": 4},
                "flat_slab": {"thickness": 150, "span": 6},
                "ribbed_slab": {"depth": 400, "span": 10},
                "beam": {"depth": 600, "span": 6},
                "wide_beam": {"width": 1200, "depth": 400},
                "column": {"height": 3, "width": 400},
                "wall": {"height": 4, "base": 1.0},
                "stair": {"riser": 170, "tread": 280}
            },
            "energy": {"area": 100, "insulation": "medium"}
        }
        response = self.app.post('/analyze', 
                                 data=json.dumps(test_data),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        comps = data['components']
        self.assertIn("One-way Slab", comps)
        self.assertIn("Flat Slab", comps)
        self.assertIn("Ribbed Slab", comps)
        self.assertIn("Retaining Wall", comps)
        
        self.assertIn("Warning", comps['Flat Slab'])
        self.assertIn("Warning", comps['Ribbed Slab'])
        self.assertIn("Warning", comps['Retaining Wall'])

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
