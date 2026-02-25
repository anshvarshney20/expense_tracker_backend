import requests
import json

BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_auth_flow():
    session = requests.Session()
    
    # 1. Register
    reg_data = {
        "email": "testuser@example.com",
        "full_name": "Test User",
        "password": "StrongPassword123!"
    }
    print(f"Registering: {reg_data['email']}...")
    try:
        r = session.post(f"{BASE_URL}/auth/register", json=reg_data)
        print(f"Status: {r.status_code}")
        print(f"Response: {r.json()}")
    except Exception as e:
        print(f"Register Failed: {e}")

    # 2. Login
    login_data = {
        "email": "testuser@example.com",
        "password": "StrongPassword123!"
    }
    print(f"\nLogging in...")
    try:
        r = session.post(f"{BASE_URL}/auth/login", json=login_data)
        print(f"Status: {r.status_code}")
        print(f"Response: {r.json()}")
        print(f"Cookies: {session.cookies.get_dict()}")
    except Exception as e:
        print(f"Login Failed: {e}")

    # 3. Get Me
    print(f"\nFetching /me...")
    try:
        r = session.get(f"{BASE_URL}/auth/me")
        print(f"Status: {r.status_code}")
        print(f"Response: {r.json()}")
    except Exception as e:
        print(f"Get Me Failed: {e}")

    # 4. Logout
    print(f"\nLogging out...")
    try:
        r = session.post(f"{BASE_URL}/auth/logout")
        print(f"Status: {r.status_code}")
        print(f"Response: {r.json()}")
    except Exception as e:
        print(f"Logout Failed: {e}")

if __name__ == "__main__":
    test_auth_flow()
