import pytest
import sys
import os
import asyncio
from fastapi.testclient import TestClient

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from routes.app import app
from config.snowflake import async_db_manager

client = TestClient(app)
class TestAuthRoutes:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        self.test_user_data = {
            "username": "testuser123",
            "email": "test@example.com",
            "password": "testpassword123"
        }
        yield
        # Async cleanup using asyncio.run()
        try:
            asyncio.run(self._async_cleanup())
        except Exception as e:
            print(f"Cleanup error: {e}")
    
    async def _async_cleanup(self):
        """Async cleanup method"""
        await async_db_manager.execute_command_async(
            "DELETE FROM PFT.USERS WHERE username = %s", 
            (self.test_user_data["username"],)
        )

    def test_register_success(self):
        response = client.post("/auth/register", json=self.test_user_data)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["message"] == "User registered successfully"
        assert data["data"]["username"] == self.test_user_data["username"]

    def test_register_duplicate_username(self):
        client.post("/auth/register", json=self.test_user_data)
        
        response = client.post("/auth/register", json=self.test_user_data)
        
        assert response.status_code == 400

    def test_login_success(self):
        client.post("/auth/register", json=self.test_user_data)
        login_data = {
            "username": self.test_user_data["username"],
            "password": self.test_user_data["password"]
        }
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "token" in data

    def test_login_invalid_credentials(self):
        login_data = {
            "username": "nonexistent",
            "password": "wrongpass"
        }       
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 401

    def test_forgot_password_success(self):
        client.post("/auth/register", json=self.test_user_data)
        forgot_data = {
            "username": self.test_user_data["username"],
            "email": self.test_user_data["email"],
            "new_password": "newpassword123"
        }        
        response = client.patch("/auth/forgot-password", json=forgot_data)       
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True

    def test_forgot_password_invalid_user(self):
        forgot_data = {
            "username": "nonexistent",
            "email": "wrong@email.com",
            "new_password": "newpassword123"
        }
        response = client.patch("/auth/forgot-password", json=forgot_data)
        assert response.status_code == 404

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
