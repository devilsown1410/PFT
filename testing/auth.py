import pytest
import sys
import os
from fastapi.testclient import TestClient

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from routes.app import app
from config.snowflake import connection

client = TestClient(app)

class TestAuthRoutes:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        self.user_data = {
            "username": "testuser123",
            "email": "test@example.com",
            "password": "testpassword123"
        }
        yield
        try:
            db = connection.get_connection()
            cursor = db.cursor()
            cursor.execute("DELETE FROM PFT.USERS WHERE username = %s", (self.user_data["username"],))
            db.commit()
            cursor.close()
        except Exception as e:
            print(f"Cleanup error: {e}")

    def register_success(self):
        response = client.post("/auth/register", json=self.user_data)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["message"] == "User registered successfully"
        assert data["data"]["username"] == self.user_data["username"]

    def register_duplicate_username(self):
        client.post("/auth/register", json=self.user_data)

        response = client.post("/auth/register", json=self.user_data)
        
        assert response.status_code == 400

    def login_success(self):
        client.post("/auth/register", json=self.user_data)    
        login_data = {
            "username": self.user_data["username"],
            "password": self.user_data["password"]
        }
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "token" in data

    def login_invalid_credentials(self):
        login_data = {
            "username": "nonexistent",
            "password": "wrongpass"
        }       
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 401

    def forgot_password_success(self):
        client.post("/auth/register", json=self.user_data)
        forgot_data = {
            "username": self.user_data["username"],
            "email": self.user_data["email"],
            "new_password": "newpassword123"
        }        
        response = client.patch("/auth/forgot-password", json=forgot_data)       
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True

    def forgot_password_invalid_user(self):
        forgot_data = {
            "username": "nonexistent",
            "email": "wrong@email.com",
            "new_password": "newpassword123"
        }
        response = client.patch("/auth/forgot-password", json=forgot_data)
        assert response.status_code == 404

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
