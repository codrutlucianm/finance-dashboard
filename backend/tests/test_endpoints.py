import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, MagicMock
from main import app

# Mock Claude response for categorization
MOCK_CATEGORIES = [{"description": "Kaufland", "category": "Food & Groceries"}]


@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_upload_csv():
    csv_content = b"date,description,amount,currency\n2026-05-01,Kaufland,-150.00,RON\n"

    mock_message = MagicMock()
    mock_message.content[0].text = '[{"description": "Kaufland", "category": "Food & Groceries"}]'

    with patch("main.claude.messages.create", return_value=mock_message):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/upload",
                files={"file": ("test.csv", csv_content, "text/csv")}
            )

    assert response.status_code == 200
    data = response.json()
    assert data["bank"] == "N/A"
    assert data["parser_used"] == "pandas"
    assert data["rows"] == 1


@pytest.mark.asyncio
async def test_upload_invalid_file_type():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/upload",
            files={"file": ("test.txt", b"some content", "text/plain")}
        )

    assert response.status_code == 400
    assert "Only CSV or PDF" in response.json()["detail"]


@pytest.mark.asyncio
async def test_upload_empty_csv():
    csv_content = b"date,description,amount,currency\n"

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/upload",
            files={"file": ("empty.csv", csv_content, "text/csv")}
        )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_categorize_empty_list():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/categorize",
            json=[]
        )
    assert response.status_code == 400
    assert "No transactions provided" in response.json()["detail"]


@pytest.mark.asyncio
async def test_upload_csv_correct_structure():
    csv_content = b"date,description,amount,currency\n2026-05-01,Kaufland,-150.00,RON\n2026-05-02,Salary,5000.00,RON\n"

    mock_message = MagicMock()
    mock_message.content[0].text = '[{"description": "Kaufland", "category": "Food & Groceries"}, {"description": "Salary", "category": "Income"}]'

    with patch("main.claude.messages.create", return_value=mock_message):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/upload",
                files={"file": ("test.csv", csv_content, "text/csv")}
            )

    assert response.status_code == 200
    data = response.json()
    assert "filename" in data
    assert "bank" in data
    assert "parser_used" in data
    assert "rows" in data
    assert "transactions" in data


@pytest.mark.asyncio
async def test_upload_csv_corrupted():
    csv_content = b"\xff\xfe invalid bytes"

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/upload",
            files={"file": ("corrupt.csv", csv_content, "text/csv")}
        )

    assert response.status_code == 400