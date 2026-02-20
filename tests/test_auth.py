def test_register_and_login(client):
    resp = client.post(
        "/api/register/",
        json={
            "username": "user1",
            "email": "user1@example.com",
            "password": "secret123",
        },
    )

    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["username"] == "user1"
    assert data["email"] == "user1@example.com"

    resp_login = client.post(
        "/api/login/",
        data={"username": "user1", "password": "secret123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert resp_login.status_code == 200, resp_login.text
    token_data = resp_login.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"