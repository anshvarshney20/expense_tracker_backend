
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_register_login(client: AsyncClient):
    # Register
    user_data = {
        "email": "test@example.com",
        "full_name": "Test User",
        "password": "Password123!"
    }
    response = await client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 200
    assert response.json()["success"] is True

    # Login
    login_data = {
        "email": "test@example.com",
        "password": "Password123!"
    }
    response = await client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert "access_token" in response.json()["data"]

@pytest.mark.asyncio
async def test_create_expense(client: AsyncClient):
    # Login first
    await client.post("/api/v1/auth/register", json={
        "email": "expense@example.com",
        "full_name": "Expense User",
        "password": "Password123!"
    })
    login_res = await client.post("/api/v1/auth/login", json={
        "email": "expense@example.com",
        "password": "Password123!"
    })
    
    # Create expense
    expense_data = {
        "title": "Test Coffee",
        "amount": 5.50,
        "category": "Food",
        "date": "2024-03-20",
        "is_avoidable": True
    }
    response = await client.post("/api/v1/expenses", json=expense_data)
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["data"]["title"] == "Test Coffee"

@pytest.mark.asyncio
async def test_get_summary(client: AsyncClient):
    # Summary for current date
    response = await client.get("/api/v1/expenses/summary", params={"year": 2024, "month": 3})
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert "total_amount" in response.json()["data"]
