import pytest
import sys
import os
from fastapi.testclient import TestClient

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from routes.app import app
from config.snowflake import connection

client = TestClient(app)

class TestUserRoutes:
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
            cursor.execute("DELETE FROM PFT.USERS WHERE username = %s", (self.user_data["username"],))
            db.commit()
            cursor.close()
        except Exception as e:
            print(f"Cleanup error: {e}")

    def get_user_profile_success(self):
        response = client.get(f"/users/profile/{self.user_data['username']}", headers=self.headers)        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["data"]["username"] == self.user_data["username"]
        assert data["data"]["email"] == self.user_data["email"]

    def get_user_profile_not_found(self):
        response = client.get("/users/profile/nonexistent", headers=self.headers)      
        assert response.status_code == 404

    def update_user_profile_success(self):
        update_data = {
            "email": "updated@example.com"
        }    
        response = client.put(f"/users/profile/{self.user_data['username']}", 
                            json=update_data, headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["data"]["email"] == "updated@example.com"

    def delete_user_profile_success(self):
        response = client.delete(f"/users/profile/{self.user_data['username']}", 
                               headers=self.headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
