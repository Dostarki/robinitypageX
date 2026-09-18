"""Tests for new points + leaderboard functionality on /api/x/*."""
import os
import pytest
import requests

BASE_URL = (os.environ.get("REACT_APP_BACKEND_URL") or "https://robinity-preview.preview.emergentagent.com").rstrip("/")
API = f"{BASE_URL}/api/x"


@pytest.fixture(scope="module")
def dev_client():
    s = requests.Session()
    r = s.get(f"{API}/auth/dev-login", allow_redirects=False, timeout=15)
    assert r.status_code in (302, 307)
    assert "ri_x_session" in s.cookies.get_dict()
    return s


# --- Config ---
def test_config_returns_points_map():
    r = requests.get(f"{API}/config", timeout=10)
    assert r.status_code == 200
    data = r.json()
    assert data["points"] == {"follow": 20, "like_rt": 10, "quote": 50}


# --- Leaderboard public ---
def test_leaderboard_public_no_cookie():
    r = requests.get(f"{API}/leaderboard", timeout=10)
    assert r.status_code == 200
    data = r.json()
    assert "entries" in data
    assert data["points"] == {"follow": 20, "like_rt": 10, "quote": 50}
    assert data["total_participants"] >= 4
    assert len(data["entries"]) <= 10
    # Sorted desc by points
    pts = [e["points"] for e in data["entries"]]
    assert pts == sorted(pts, reverse=True)
    # Rank correctness
    for i, e in enumerate(data["entries"]):
        assert e["rank"] == i + 1
        for k in ("username", "profile_image_url", "points", "completed"):
            assert k in e
    # Rank 1 should be alice_eth 80
    top = data["entries"][0]
    assert top["username"] == "alice_eth"
    assert top["points"] == 80
    # bob_defi 70, carol_x 20, dave_nft 10
    by_name = {e["username"]: e["points"] for e in data["entries"]}
    assert by_name.get("bob_defi") == 70
    assert by_name.get("carol_x") == 20
    assert by_name.get("dave_nft") == 10


# --- Me includes points ---
def test_me_has_points_field(dev_client):
    r = dev_client.get(f"{API}/me", timeout=10)
    assert r.status_code == 200
    user = r.json()["user"]
    assert user is not None
    assert "points" in user
    assert user["points"] == 0


# --- EVM once ---
def test_evm_save_then_conflict(dev_client):
    addr = "0x" + "c" * 40
    r = dev_client.post(f"{API}/evm", json={"address": addr}, timeout=10)
    assert r.status_code == 200
    r2 = dev_client.post(f"{API}/evm", json={"address": "0x" + "d" * 40}, timeout=10)
    assert r2.status_code == 409


# --- Follow verify awards 20 pts ---
def test_follow_verify_awards_points(dev_client):
    r = dev_client.post(f"{API}/tasks/follow/verify", timeout=15)
    assert r.status_code == 200
    data = r.json()
    assert data["points_awarded"] == 20
    assert data["user"]["points"] == 20


# --- like_rt returns 503 since tweet not configured ---
def test_like_rt_503(dev_client):
    r = dev_client.post(f"{API}/tasks/like_rt/verify", timeout=15)
    assert r.status_code == 503


# --- Leaderboard includes robinity_tester after follow ---
def test_leaderboard_contains_dev_user_after_follow(dev_client):
    r = requests.get(f"{API}/leaderboard", timeout=10)
    assert r.status_code == 200
    names = {e["username"]: e for e in r.json()["entries"]}
    assert "robinity_tester" in names
    assert names["robinity_tester"]["points"] == 20


def test_cleanup(dev_client):
    dev_client.post(f"{API}/logout", timeout=10)
