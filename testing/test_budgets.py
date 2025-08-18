import pytest
import sys
import os
from fastapi.testclient import TestClient

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from routes.app import app
from config.snowflake import connection

client = TestClient(app)
class TestBudgetRoutes:
    
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        self.test_user_data = {
            "username": "testuser123",
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        client.post("/auth/register", json=self.test_user_data)
        login_response = client.post("/auth/login", json={
            "username": self.test_user_data["username"],
            "password": self.test_user_data["password"]
        })
        self.token = login_response.json()["token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
        
        yield
        
        try:
            from datetime import datetime
            current_month = datetime.now().strftime("%Y-%m")           
            db = connection.get_connection()
            cursor = db.cursor()
            cursor.execute("DELETE FROM PFT.BUDGET WHERE user_id = (SELECT id FROM PFT.USERS WHERE username = %s) AND budget_month = %s", (self.test_user_data["username"], current_month))
            cursor.execute("DELETE FROM PFT.USERS WHERE username = %s", (self.test_user_data["username"],))
            db.commit()
            cursor.close()
        except Exception as e:
            print(f"Cleanup error: {e}")

    def test_create_budget_success(self):
        from datetime import datetime
        current_month = datetime.now().strftime("%Y-%m")  
        budget_data = {
            "category_id": 1,
            "month": current_month,
            "amount": 1000.0,
            "user_id": 1
        }
        response = client.post("/budgets/add", json=budget_data, headers=self.headers)       
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["data"]["amount"] == '$1000.0'
        assert data["data"]["category_id"] == 1

    def test_create_budget_missing_fields(self):
        budget_data = {
            "category_id": 1,
        }
        response = client.post("/budgets/add", json=budget_data, headers=self.headers)       
        assert response.status_code == 422

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
