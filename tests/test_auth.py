"""
tests/test_auth.py — Unit and integration tests for Farmer Authentication
"""

import sys
import os
import uuid
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient
from main import app
from services.auth_service import AuthService

client = TestClient(app)


class TestAuthCrypto:
    def test_password_hash_and_verify(self):
        pw = "SecretFarmerPass123"
        hashed = AuthService.hash_password(pw)
        assert hashed != pw
        assert AuthService.verify_password(pw, hashed) is True
        assert AuthService.verify_password("WrongPassword", hashed) is False

    def test_jwt_token_flow(self):
        token = AuthService.create_access_token(user_id=42, phone_or_email="9876543210")
        assert isinstance(token, str)
        payload = AuthService.decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == "42"
        assert payload["identifier"] == "9876543210"

    def test_invalid_token_returns_none(self):
        assert AuthService.decode_access_token("invalid.jwt.token") is None


class TestAuthAPIEndpoints:
    @pytest.fixture(scope="class")
    def registered_farmer(self):
        uid = uuid.uuid4().hex[:8]
        phone = f"912{uid[:7]}"
        email = f"tukaram_{uid}@aerocrop.ai"
        payload = {
            "full_name": "Tukaram Shinde",
            "phone_number": phone,
            "email": email,
            "password": "FarmerPassword123",
            "district": "nashik",
            "taluka_village": "Dindori",
            "preferred_language": "mr",
        }
        res = client.post("/api/auth/register", json=payload)
        assert res.status_code == 200, f"Registration failed: {res.text}"
        data = res.json()
        data["test_phone"] = phone
        data["test_email"] = email
        return data

    def test_register_success(self, registered_farmer):
        assert registered_farmer["status"] == "success"
        assert "access_token" in registered_farmer
        assert registered_farmer["user"]["full_name"] == "Tukaram Shinde"
        assert registered_farmer["user"]["district"] == "nashik"

    def test_duplicate_phone_rejected(self, registered_farmer):
        payload = {
            "full_name": "Another Farmer",
            "phone_number": registered_farmer["test_phone"],  # Duplicate
            "password": "Password123",
            "district": "pune",
            "preferred_language": "en",
        }
        res = client.post("/api/auth/register", json=payload)
        assert res.status_code == 400
        assert "already registered" in res.json()["detail"]

    def test_duplicate_email_rejected(self, registered_farmer):
        payload = {
            "full_name": "Another Farmer",
            "email": registered_farmer["test_email"],  # Duplicate
            "password": "Password123",
            "district": "pune",
            "preferred_language": "en",
        }
        res = client.post("/api/auth/register", json=payload)
        assert res.status_code == 400
        assert "already registered" in res.json()["detail"]

    def test_short_password_rejected(self):
        payload = {
            "full_name": "Short Pass Farmer",
            "phone_number": f"999{uuid.uuid4().hex[:7]}",
            "password": "123",  # Too short
            "district": "pune",
            "preferred_language": "en",
        }
        res = client.post("/api/auth/register", json=payload)
        assert res.status_code == 422 or res.status_code == 400

    def test_login_with_phone_success(self, registered_farmer):
        res = client.post(
            "/api/auth/login",
            json={"identifier": registered_farmer["test_phone"], "password": "FarmerPassword123"},
        )
        assert res.status_code == 200
        data = res.json()
        assert "access_token" in data
        assert data["user"]["full_name"] == "Tukaram Shinde"

    def test_login_with_email_success(self, registered_farmer):
        res = client.post(
            "/api/auth/login",
            json={"identifier": registered_farmer["test_email"], "password": "FarmerPassword123"},
        )
        assert res.status_code == 200
        data = res.json()
        assert "access_token" in data

    def test_login_invalid_password(self, registered_farmer):
        res = client.post(
            "/api/auth/login",
            json={"identifier": registered_farmer["test_phone"], "password": "WrongPassword"},
        )
        assert res.status_code == 401

    def test_get_me_authenticated(self, registered_farmer):
        token = registered_farmer["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        res = client.get("/api/auth/me", headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert data["full_name"] == "Tukaram Shinde"
        assert data["district"] == "nashik"

    def test_get_me_unauthorized(self):
        res = client.get("/api/auth/me")
        assert res.status_code == 401

    def test_update_profile(self, registered_farmer):
        token = registered_farmer["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        res = client.put(
            "/api/auth/profile",
            headers=headers,
            json={"full_name": "Tukaram Patil", "district": "jalgaon", "preferred_language": "hi"},
        )
        assert res.status_code == 200
        data = res.json()
        assert data["user"]["full_name"] == "Tukaram Patil"
        assert data["user"]["district"] == "jalgaon"
        assert data["user"]["preferred_language"] == "hi"

    def test_logout_invalidates_token(self, registered_farmer):
        token = registered_farmer["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Verify token currently works
        res = client.get("/api/auth/me", headers=headers)
        assert res.status_code == 200

        # 2. Perform logout to invalidate token_version
        logout_res = client.post("/api/auth/logout", headers=headers)
        assert logout_res.status_code == 200
        assert "Successfully logged out" in logout_res.json()["message"]

        # 3. Verify old token is now rejected (401)
        res_after = client.get("/api/auth/me", headers=headers)
        assert res_after.status_code == 401
        assert "revoked" in res_after.json()["detail"].lower() or "expired" in res_after.json()["detail"].lower()

    def test_login_with_phone_normalization(self):
        uid = uuid.uuid4().hex[:7]
        raw_phone = f"982{uid}"
        # Register with standard number
        reg_res = client.post(
            "/api/auth/register",
            json={
                "full_name": "Kisan Rao",
                "phone_number": raw_phone,
                "password": "FarmerPassword123",
                "district": "solapur",
            },
        )
        assert reg_res.status_code == 200

        # Login with formatted "+91" prefix and spaces
        login_res = client.post(
            "/api/auth/login",
            json={
                "identifier": f"+91 {raw_phone[:5]} {raw_phone[5:]}",
                "password": "FarmerPassword123",
            },
        )
        assert login_res.status_code == 200
        assert "access_token" in login_res.json()

    def test_change_password_flow(self):
        uid = uuid.uuid4().hex[:7]
        phone = f"987{uid}"
        # Register user
        reg_res = client.post(
            "/api/auth/register",
            json={
                "full_name": "Ramesh Pawar",
                "phone_number": phone,
                "password": "OldPassword123",
                "district": "pune",
            },
        )
        assert reg_res.status_code == 200
        token = reg_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Wrong current password
        bad_res = client.put(
            "/api/auth/change-password",
            headers=headers,
            json={"current_password": "WrongPassword!", "new_password": "NewSecretPassword123"},
        )
        assert bad_res.status_code == 400
        assert "Current password does not match" in bad_res.json()["detail"]

        # 2. Successful password change
        good_res = client.put(
            "/api/auth/change-password",
            headers=headers,
            json={"current_password": "OldPassword123", "new_password": "NewSecretPassword123"},
        )
        assert good_res.status_code == 200
        data = good_res.json()
        assert data["status"] == "success"
        new_token = data["access_token"]

        # 3. Old token should now be invalidated
        old_token_res = client.get("/api/auth/me", headers=headers)
        assert old_token_res.status_code == 401

        # 4. New token works
        new_token_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {new_token}"})
        assert new_token_res.status_code == 200
        assert new_token_res.json()["full_name"] == "Ramesh Pawar"

        # 5. Login with new password succeeds
        login_new = client.post(
            "/api/auth/login",
            json={"identifier": phone, "password": "NewSecretPassword123"},
        )
        assert login_new.status_code == 200


