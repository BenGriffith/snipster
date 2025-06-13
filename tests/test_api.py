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
    response.status_code == 201
