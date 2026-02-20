def create_user_and_get_token(client, username):
    resp_reg = client.post(
        "/api/register/",
        json={
            "username": username,
            "email": f"{username}@example.com",
            "password": "secret123",
        },
    )

    assert resp_reg.status_code == 201, resp_reg.text 

    resp_login = client.post(
        "api/login/",
        data={"username": username, "password":"secret123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert resp_login.status_code == 200, resp_login.text 

    token = resp_login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def create_published_post(client, headers, title="Post with comments"):
    content = "x" * 150
    resp = client.post(
        "api/posts/",
        json={
            "title": title,
            "content": content,
            "status": "published",
            "tags": ["python"]
        },
        headers=headers,
    )

    assert resp.status_code == 201, resp.text 
    return resp.json()



def test_add_get_comments_with_xss_sanitization(client):
    author_headers = create_user_and_get_token(client, "author")
    post = create_published_post(client, author_headers)
    slug = post["slug"]

    commenter_headers = create_user_and_get_token(client, "commenter")

    raw_text = "<b>Hello</b>"
    resp_comment = client.post(
        f"/api/posts/{slug}/comments/",
        json={"text": raw_text},
        headers=commenter_headers,
    )

    assert resp_comment.status_code == 201, resp_comment.text 
    comment = resp_comment.json()

    assert comment["text"] == "&lt;b&gt;Hello&lt;/b&gt;"


    resp_list = client.get(f"/api/posts/{slug}/comments/")
    assert resp_list.status_code == 200, resp_list.text 
    comments = resp_list.json()

    assert len(comments) == 1

    assert comments[0]["id"] == comment["id"]
    assert comments[0]["text"] == "&lt;b&gt;Hello&lt;/b&gt;"


def test_delete_comment_permissions(client):
    author_headers = create_user_and_get_token(client, "author2")
    commenter_headers = create_user_and_get_token(client, "commenter2")
    other_headers = create_user_and_get_token(client, "other2")

    post = create_published_post(client, author_headers,title="Post for delete test")

    slug = post["slug"]

    resp_comment = client.post(
        f"/api/posts/{slug}/comments/",
        json={"text":"comment to delete"},
        headers=commenter_headers,
    )
    assert resp_comment.status_code == 201, resp_comment.text 
    comment = resp_comment.json()
    comment_id = comment["id"]

    # посторонний пользователь не может удалить комментарий
    resp_forbidden = client.delete(
        f"/api/comments/{comment_id}/",
        headers=other_headers,
    )

    assert resp_forbidden.status_code == 403

    resp_delete_by_commenter = client.delete(
        f"/api/comments/{comment_id}/",
        headers=commenter_headers,
    )
    assert resp_delete_by_commenter.status_code == 204


    resp_list = client.get(f"/api/posts/{slug}/comments/")
    assert resp_list.status_code == 200
    assert len(resp_list.json()) == 0

    resp_comment2 = client.post(
        f"/api/posts/{slug}/comments/",
        json={"text": "second comment"},
        headers=commenter_headers,
    )
    assert resp_comment2.status_code == 201, resp_comment2.text
    comment2_id = resp_comment2.json()["id"]


    resp_delete_by_author = client.delete(
        f"/api/comments/{comment2_id}/",
        headers=author_headers,
    )
    assert resp_delete_by_author.status_code == 204



