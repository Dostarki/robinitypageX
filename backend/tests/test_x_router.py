"""Backend tests for /api/x/* endpoints (Robinity X Connect feature)."""
import os
import re
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://robinity-preview.preview.emergentagent.com").rstrip("/")
API = f"{BASE_URL}/api/x"


@pytest.fixture(scope="module")
def clean_client():
    """Fresh session with no cookies."""
    return requests.Session()


@pytest.fixture(scope="module")
def dev_client():
    """Session logged in via dev mock login."""
    s = requests.Session()
    # dev-login uses 302 redirect; allow_redirects=False to inspect
    r = s.get(f"{API}/auth/dev-login", allow_redirects=False, timeout=15)
    assert r.status_code in (302, 307), f"dev-login not redirecting: {r.status_code}"
    assert "x_connected=1" in r.headers.get("location", "")
    assert "ri_x_session" in s.cookies.get_dict(), "session cookie not set"
    return s


# --- Config & auth basics ---
def test_config_unconfigured():
    r = requests.get(f"{API}/config", timeout=10)
    assert r.status_code == 200
    data = r.json()
    assert data["configured"] is False
    assert data["target_username"] == "RobinityInt"


def test_login_503_when_unconfigured():
    r = requests.get(f"{API}/auth/login", timeout=10, allow_redirects=False)
    assert r.status_code == 503


def test_me_without_cookie_returns_null():
    r = requests.get(f"{API}/me", timeout=10)
    assert r.status_code == 200
    assert r.json() == {"user": None}


# --- Dev login ---
def test_dev_login_and_me(dev_client):
    r = dev_client.get(f"{API}/me", timeout=10)
    assert r.status_code == 200
    user = r.json()["user"]
    assert user is not None
    assert user["username"] == "robinity_tester"
    assert user["x_id"] == "dev-000001"
    assert user.get("evm_address") in (None, "")


# --- EVM address flow ---
def test_evm_requires_auth():
    r = requests.post(f"{API}/evm", json={"address": "0x" + "a" * 40}, timeout=10)
    assert r.status_code == 401


def test_evm_invalid_address(dev_client):
    r = dev_client.post(f"{API}/evm", json={"address": "0xabc"}, timeout=10)
    assert r.status_code == 400


def test_evm_save_valid(dev_client):
    addr = "0x" + "A" * 40
    r = dev_client.post(f"{API}/evm", json={"address": addr}, timeout=10)
    assert r.status_code == 200
    user = r.json()["user"]
    assert user["evm_address"].lower() == addr.lower()


def test_evm_conflict_second_save(dev_client):
    r = dev_client.post(f"{API}/evm", json={"address": "0x" + "b" * 40}, timeout=10)
    assert r.status_code == 409


# --- Task verification ---
def test_verify_unknown_task_404(dev_client):
    r = dev_client.post(f"{API}/tasks/unknown/verify", timeout=15)
    assert r.status_code == 404


def test_verify_quote_503_no_tweet(dev_client):
    r = dev_client.post(f"{API}/tasks/quote/verify", timeout=15)
    assert r.status_code == 503


def test_verify_like_rt_503_no_tweet(dev_client):
    r = dev_client.post(f"{API}/tasks/like_rt/verify", timeout=15)
    assert r.status_code == 503


def test_verify_follow_dev_ok(dev_client):
    r = dev_client.post(f"{API}/tasks/follow/verify", timeout=15)
    assert r.status_code == 200
    data = r.json()
    assert data["user"]["tasks"]["follow"]["done"] is True
    # dev token yields verified=False
    assert data["verified"] is False


def test_me_persists_task_state(dev_client):
    r = dev_client.get(f"{API}/me", timeout=10)
    assert r.status_code == 200
    assert r.json()["user"]["tasks"]["follow"]["done"] is True


# --- Logout ---
def test_logout(dev_client):
    r = dev_client.post(f"{API}/logout", timeout=10)
    assert r.status_code == 200
    r2 = dev_client.get(f"{API}/me", timeout=10)
    assert r2.json()["user"] is None
