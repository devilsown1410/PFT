import pytest
import sys
import os
from fastapi.testclient import TestClient

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from routes.app import app
from config.snowflake import connection

client = TestClient(app)
class TestTransactionRoutes:
    
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
            from datetime import datetime
            current_month = datetime.now().strftime("%Y-%m")          
            db = connection.get_connection()
            cursor = db.cursor()
            cursor.execute("DELETE FROM PFT.USER_TRANSACTIONS WHERE user_id = (SELECT id FROM PFT.USERS WHERE username = %s)", (self.user_data["username"],))
            cursor.execute("DELETE FROM PFT.BUDGET WHERE user_id = (SELECT id FROM PFT.USERS WHERE username = %s) AND budget_month = %s", (self.user_data["username"], current_month))
            cursor.execute("DELETE FROM PFT.USERS WHERE username = %s", (self.user_data["username"],))
            db.commit()
            cursor.close()
        except Exception as e:
            print(f"Cleanup error: {e}")

    def create_transaction_success(self):
        from datetime import datetime
        current_month = datetime.now().strftime("%Y-%m")
        budget_data = {
            "category_id": 1,
            "month": current_month,
            "amount": 1000
        }
        budget_response = client.post("/budgets/add", json=budget_data, headers=self.headers)
        print(f"Budget creation response: {budget_response.status_code}, {budget_response.text}")
        transaction_data = {
            "amount": 100,
            "description": "Test expense",
            "category_id": 1,
            "transaction_type": "expense"
        }
        
        response = client.post("/transactions/add", json=transaction_data, headers=self.headers)
        print(f"Transaction response: {response.status_code}, {response.text}")
        assert response.status_code in [200, 201]
        if response.status_code in [200, 201]:
            data = response.json()
            assert data["success"] == True

    def create_transaction_without_budget(self):
        transaction_data = {
            "amount": 100,
            "description": "Test expense",
            "category_id": 999,
            "transaction_type": "expense"
        }       
        response = client.post("/transactions/add", json=transaction_data, headers=self.headers)
        assert response.status_code == 400

    def create_invalid_transaction_type(self):
        transaction_data = {
            "amount": 100,
            "description": "Test transaction",
            "category_id": 1,
            "transaction_type": "invalid_type"
        }    
        response = client.post("/transactions/add", json=transaction_data, headers=self.headers)  
        assert response.status_code == 400

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
