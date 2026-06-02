"""API-shape tests: responses match the OpenAI schema standard clients expect."""


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_chat_completions_shape(client):
    r = client.post(
        "/v1/chat/completions",
        json={"model": "hexrag", "messages": [{"role": "user", "content": "hi"}]},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["object"] == "chat.completion"
    assert isinstance(body["id"], str) and body["id"].startswith("chatcmpl-")
    assert isinstance(body["created"], int)
    choice = body["choices"][0]
    assert choice["index"] == 0
    assert choice["finish_reason"] == "stop"
    assert choice["message"]["role"] == "assistant"
    assert isinstance(choice["message"]["content"], str)


def test_chat_completions_streaming_sse(client):
    r = client.post(
        "/v1/chat/completions",
        json={"messages": [{"role": "user", "content": "hi"}], "stream": True},
    )
    assert r.status_code == 200
    text = r.text
    assert text.startswith("data: ")
    assert "chat.completion.chunk" in text
    assert text.rstrip().endswith("data: [DONE]")


def test_completions_endpoint(client):
    r = client.post("/v1/completions", json={"prompt": "hello"})
    assert r.status_code == 200
    assert r.json()["object"] == "chat.completion"


def test_embeddings_shape(client):
    r = client.post("/v1/embeddings", json={"input": ["a", "b"]})
    assert r.status_code == 200
    body = r.json()
    assert body["object"] == "list"
    assert len(body["data"]) == 2
    assert body["data"][0]["object"] == "embedding"
    assert body["data"][0]["index"] == 0
    assert len(body["data"][0]["embedding"]) == 384


def test_ingest_via_api(client):
    r = client.post("/ingest/text", json={"file_name": "n.txt", "text": "hello world"})
    assert r.status_code == 200
    assert r.json()["data"][0]["doc_id"]
