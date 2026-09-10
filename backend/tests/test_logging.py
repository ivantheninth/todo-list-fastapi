async def test_request_id_header(client):
    response = await client.get("/")

    assert response.status_code == 200
    assert "X-Request-ID" in response.headers


async def test_existing_request_id_is_preserved(client):
    response = await client.get(
        "/",
        headers={
            "X-Request-ID": "test-request-id",
        },
    )

    assert response.status_code == 200
    assert (
        response.headers["X-Request-ID"]
        == "test-request-id"
    )