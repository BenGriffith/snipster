def test_create_snippet(fastapi_client):
    response = fastapi_client.post(
        "/snippets/",
        json={
            "title": "first snippet",
            "code": "print('hello world')",
            "description": "first snippet in snipster",
            "language": "python",
            "tags": "python, fastapi",
            "favorite": True,
        },
    )
    assert response.status_code == 201
    assert "first snippet" == response.json()["title"]


def test_get_snippets(fastapi_client, snippet_one, snippet_two):
    response = fastapi_client.post(
        "/snippets/",
        json={
            "title": snippet_one.title,
            "code": snippet_one.code,
            "description": snippet_one.description,
            "language": "python",
            "tags": "python, fastapi",
            "favorite": False,
        },
    )
    assert response.status_code == 201
    response = fastapi_client.post(
        "/snippets/",
        json={
            "title": snippet_two.title,
            "code": snippet_two.code,
            "description": snippet_two.description,
            "language": "python",
            "tags": "print",
            "favorite": True,
        },
    )
    assert response.status_code == 201

    response = fastapi_client.get("/snippets/")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_snippet(fastapi_client, snippet_one):
    response = fastapi_client.post(
        "/snippets/",
        json={
            "title": snippet_one.title,
            "code": snippet_one.code,
            "description": snippet_one.description,
            "language": "python",
            "tags": "python, fastapi",
            "favorite": False,
        },
    )
    assert response.status_code == 201
    response = fastapi_client.get(f"/snippets/{response.json()['id']}")
    assert response.json()["id"] == 1
    assert response.json()["title"] == "first snippet"


def test_delete_snippet(fastapi_client, snippet_two):
    response = fastapi_client.post(
        "/snippets/",
        json={
            "title": snippet_two.title,
            "code": snippet_two.code,
            "description": snippet_two.description,
            "language": "python",
            "tags": snippet_two.tags,
            "favorite": snippet_two.favorite,
        },
    )
    response = fastapi_client.delete(f"/snippets/{response.json()['id']}")
    assert (
        response.json()["message"]
        == "Snippet ID: 1 was deleted and removed from the Snippet Repository"
    )


def test_toggle_favorite(fastapi_client, snippet_two):
    response = fastapi_client.post(
        "/snippets/",
        json={
            "title": snippet_two.title,
            "code": snippet_two.code,
            "description": snippet_two.description,
            "language": "python",
            "tags": snippet_two.tags,
            "favorite": snippet_two.favorite,
        },
    )
    response = fastapi_client.post(f"/snippets/{response.json()['id']}/favorite")
    assert (
        response.json()["message"]
        == "Snippet ID: 1 favorite updated from True to False"
    )


def test_tag(fastapi_client, snippet_one):
    response = fastapi_client.post(
        "/snippets/",
        json={
            "title": snippet_one.title,
            "code": snippet_one.code,
            "description": snippet_one.description,
            "language": "python",
            "tags": snippet_one.tags,
            "favorite": snippet_one.favorite,
        },
    )
    tag_response = fastapi_client.post(
        f"/snippets/{response.json()['id']}/tags?tags=python&tags=print&remove=false"
    )
    assert (
        tag_response.json()["message"]
        == "Tags ('python, print',) were added for Snippet ID: 1"
    )
    tag_response = fastapi_client.post(
        f"/snippets/{response.json()['id']}/tags?tags=print&remove=true"
    )
    assert (
        tag_response.json()["message"]
        == "Tags ('print',) were removed from Snippet ID: 1"
    )
