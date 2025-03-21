import pytest
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def test_query_vector_search_valid():
    """✅ Test a valid query returns results"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/vector_search/query", json={"query": "Explain neural networks"})

    assert response.status_code == 200
    data = response.json()

    assert "results" in data
    assert isinstance(data["results"], list)

    if data["results"]:  # If results exist, check structure
        for result in data["results"]:
            assert "page" in result
            assert "content" in result
            assert isinstance(result["page"], (int, str))  # Page could be stored as a string
            assert isinstance(result["content"], str)

@pytest.mark.asyncio
async def test_query_vector_search_empty_query():
    """❌ Test sending an empty query returns 400 error"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/vector_search/query", json={"query": ""})

    assert response.status_code == 400
    assert response.json()["detail"] == "Query must be provided"

@pytest.mark.asyncio
async def test_query_vector_search_malformed_request():
    """❌ Test sending malformed JSON returns 422 error"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/vector_search/query", json={"wrong_field": "neural networks"})

    assert response.status_code == 422  # Unprocessable Entity

@pytest.mark.asyncio
async def test_query_vector_search_no_results():
    """✅ Test when no matching results are found"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/vector_search/query", json={"query": "qwerty12345"})

    assert response.status_code == 200
    data = response.json()

    assert "results" in data
    assert isinstance(data["results"], list)
    assert data["results"] == []  # No results found

@pytest.mark.asyncio
async def test_query_vector_search_db_connection_error(monkeypatch):
    """❌ Test if database connection fails"""

    async def mock_query_documents(*args, **kwargs):
        raise Exception("Database connection failed")

    monkeypatch.setattr("services.vector_search.vector_search_service.query_documents", mock_query_documents)

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/vector_search/query", json={"query": "Explain neural networks"})

    assert response.status_code == 500
    assert "Database connection failed" in response.json()["detail"]
