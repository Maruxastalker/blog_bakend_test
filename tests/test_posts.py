def get_auth_header(client, username="author"):
    # регистрация пользователя для теста
    resp_reg = client.post(
        "/api/register/",
        json={
            "username": username,
            "email": f"{username}@example.com",
            "password": "secret123",
        },
    )
    assert resp_reg.status_code == 201, resp_reg.text

    # логин
    resp_login = client.post(
        "/api/login/",
        data={"username": username, "password": "secret123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert resp_login.status_code == 200, resp_login.text
    token = resp_login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def create_user_and_get_token(client, username="author"):
    resp_reg = client.post(
        "api/register/",
        json={
            "username":username,
            "email": f"{username}@example.com",
            "password": "secret123",
        },
    )

    assert resp_reg.status_code == 201, resp_reg.text

    resp_login = client.post(
        "/api/login/",
        data={"username": username, "password": "secret123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert resp_login.status_code == 200, resp_login.text
    access_token = resp_login.json()["access_token"]
    return {"Authorization": f"Bearer {access_token}"}


def test_create_and_get_post(client):
    headers = get_auth_header(client)
    content = "x" * 150  # ВАЖНО: длина >= 100

    resp = client.post(
        "/api/posts/",
        json={
            "title": "My first post",
            "content": content,
            "status": "published",
            "tags": ["python", "fastapi"],
        },
        headers=headers,
    )
    assert resp.status_code == 201, resp.text
    post = resp.json()
    slug = post["slug"]

    # список постов
    list_resp = client.get("/api/posts/")
    assert list_resp.status_code == 200, list_resp.text
    posts = list_resp.json()
    assert any(p["slug"] == slug for p in posts)

    # детальный просмотр
    detail_resp = client.get(f"/api/posts/{slug}/")
    assert detail_resp.status_code == 200, detail_resp.text
    assert detail_resp.json()["title"] == "My first post"