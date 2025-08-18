import pytest
import sys
import os
from fastapi.testclient import TestClient

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from routes.app import app

client = TestClient(app)

class TestAppRoutes:

    def root_endpoint(self):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data

    def auth_root_endpoint(self):
        response = client.get("/auth/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
