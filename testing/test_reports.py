import pytest
import sys
import os
from fastapi.testclient import TestClient

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from routes.app import app
from config.snowflake import connection

client = TestClient(app)

class TestReportRoutes:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        self.user_data = {
            "username": "testuser123",
            "email": "test@example.com",
            "password": "testpassword123"
        }

        client.post("/auth/register", json=self.user_data)
        login_response = client.post("/auth/login", json={
            "username": self.user_data["username"],
            "password": self.user_data["password"]
        })
        self.token = login_response.json()["token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
        yield
        try:
            db = connection.get_connection()
            cursor = db.cursor()
            cursor.execute("DELETE FROM PFT.USER_TRANSACTIONS WHERE user_id = (SELECT id FROM PFT.USERS WHERE username = %s)", (self.user_data["username"],))
            cursor.execute("DELETE FROM PFT.BUDGET WHERE user_id = (SELECT id FROM PFT.USERS WHERE username = %s)", (self.user_data["username"],))
            cursor.execute("DELETE FROM PFT.USERS WHERE username = %s", (self.user_data["username"],))
            db.commit()
            cursor.close()
        except Exception as e:
            print(f"Cleanup error: {e}")

    def get_category_monthly_report_success(self):
        response = client.get("/reports/gcm?page=1&limit=10", headers=self.headers)      
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "data" in data

    def get_transaction_by_month_success(self):
        response = client.get("/reports/gtbm/2024-08", headers=self.headers)       
        assert response.status_code in [200, 404]        
        if response.status_code == 200:
            data = response.json()
            assert data["success"] == True

    def get_transaction_by_month_invalid_format(self):
        response = client.get("/reports/gtbm/invalid-month", headers=self.headers)       
        assert response.status_code in [400, 404, 500]

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
