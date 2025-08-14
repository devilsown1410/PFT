import pytest
import sys
import os
from models.transactions import Transaction
from models.user import UserProfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_user_profile_model():
    try:
        user = UserProfile(username="testuser", email="test@example.com")
        assert user.username == "testuser"
        assert user.email == "test@example.com"        
        user_dict = user.model_dump()
        assert isinstance(user_dict, dict)
        assert user_dict["username"] == "testuser"
        assert user_dict["email"] == "test@example.com"
        
    except ImportError:
        pytest.skip("UserProfile model not found")

def test_transaction_data():
    try:
        transaction = Transaction(
            amount=100.50,
            description="Coffee shop",
            category_id=101,
            transaction_date="2024-01",
            transaction_type="expense"
        )
        assert hasattr(transaction, "amount")
        assert hasattr(transaction, "description")
        assert hasattr(transaction, "category_id")

        assert transaction.amount == 100.50
        assert transaction.description == "Coffee shop"
        assert transaction.transaction_type == "expense"

        assert isinstance(transaction.amount, (int, float))
        assert isinstance(transaction.description, str)
        assert isinstance(transaction.category_id, int)
        assert isinstance(transaction.transaction_date, str)
        assert isinstance(transaction.transaction_type, str)

        assert transaction.amount > 0

        transaction_dict = transaction.model_dump()
        assert isinstance(transaction_dict, dict)
        assert "amount" in transaction_dict
        assert "description" in transaction_dict
        assert transaction_dict["amount"] == 100.50
        
    except ImportError:
        pytest.skip("Transaction model not found")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
