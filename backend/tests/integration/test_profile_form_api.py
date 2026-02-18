"""
Интеграционные тесты для новых эндпоинтов профиля:
- POST /api/profiles/form
- PUT  /api/profiles/{id}

Требует запущенный backend на http://localhost:8000.
"""

import pytest
import httpx
import uuid

BASE_URL = "http://localhost:8000"

VALID_PAYLOAD = {
    "topic": "Тест форм-профиль",
    "subject_area": "Информатика",
    "experience_level": "beginner",
    "desired_outcomes": ["Понимать основы"],
    "diagnostic_result": "partial",
    "weekly_hours": 5,
    "success_criteria": [
        {"id": "sc1", "description": "Решать задачи", "metric": "", "measurable": True}
    ],
    "target_tasks": [
        {"id": "t1", "description": "Задача 1"}
    ],
    "subtasks": [
        {"id": "st1", "description": "Подзадача 1", "parent_task_id": "t1",
         "required_skills": [], "required_knowledge": []}
    ],
    "easiest_task_id": "t1",
    "peak_task_id": "t1",
    "confusing_concepts": [
        {"id": "c1", "term": "Импликация", "confusion_description": ""}
    ],
}


@pytest.mark.asyncio
async def test_create_profile_from_form_valid():
    """POST /api/profiles/form с валидным payload → 201, содержит id и topic."""
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        response = await client.post("/api/profiles/form", json=VALID_PAYLOAD)

    assert response.status_code == 201, f"Ожидался 201, получен {response.status_code}: {response.text}"
    data = response.json()
    assert "id" in data
    assert data["topic"] == VALID_PAYLOAD["topic"]
    assert data["experience_level"] == "beginner"
    assert "validation_result" in data
    assert isinstance(data["validation_result"]["valid"], bool)


@pytest.mark.asyncio
async def test_create_profile_from_form_missing_topic():
    """POST /api/profiles/form без topic → 422."""
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        response = await client.post("/api/profiles/form", json={"subject_area": "Математика"})

    assert response.status_code == 422, f"Ожидался 422, получен {response.status_code}"


@pytest.mark.asyncio
async def test_create_profile_from_form_empty_body():
    """POST /api/profiles/form с пустым телом → 422."""
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        response = await client.post("/api/profiles/form", json={})

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_profile_existing():
    """PUT /api/profiles/{id} для существующего профиля → 200, обновлённый topic."""
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        # Сначала создаём профиль
        create_resp = await client.post("/api/profiles/form", json=VALID_PAYLOAD)
        assert create_resp.status_code == 201
        profile_id = create_resp.json()["id"]

        # Обновляем
        updated_payload = {**VALID_PAYLOAD, "topic": "Обновлённая тема"}
        update_resp = await client.put(f"/api/profiles/{profile_id}", json=updated_payload)

    assert update_resp.status_code == 200, f"Ожидался 200, получен {update_resp.status_code}: {update_resp.text}"
    data = update_resp.json()
    assert data["topic"] == "Обновлённая тема"
    assert data["id"] == profile_id


@pytest.mark.asyncio
async def test_update_profile_not_found():
    """PUT /api/profiles/{id} с несуществующим ID → 404."""
    fake_id = str(uuid.uuid4())
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        response = await client.put(f"/api/profiles/{fake_id}", json=VALID_PAYLOAD)

    assert response.status_code == 404, f"Ожидался 404, получен {response.status_code}"
