"""
E2E тест для Phase 3 (US1) - полный цикл генерации трека.

Сценарий:
1. Загрузить sample JSON профиль
2. Запустить генерацию трека
3. Проверить результат PersonalizedTrack
4. Проверить наличие логов B1-B8 в БД
"""

import pytest
import uuid
from pathlib import Path

# Sample JSON профиль для теста
SAMPLE_PROFILE = {
    "topic": "Python async programming",
    "experience_level": "intermediate",
    "diagnostic_result": "moderate_gaps",
    "peak_task": "Build async web scraper with aiohttp and asyncio",
    "task_hierarchy": [
        "Understand async/await syntax",
        "Work with asyncio event loop",
        "Handle concurrent requests"
    ],
    "desired_outcomes": [
        "Умение писать асинхронный код",
        "Понимание asyncio patterns"
    ],
    "confusing_concepts": ["Event loop mechanics", "Task scheduling"],
    "barriers": ["Debugging async code"],
    "study_hours_week": 10,
    "deadline_days": 30,
    "mastery_signals": ["Efficient concurrent code"],
    "success_criteria": ["Working async application"]
}


@pytest.mark.asyncio
async def test_full_generation_cycle():
    """
    E2E тест: загрузка профиля → генерация трека → проверка результата.

    ВАЖНО: Требует запущенные Docker контейнеры (backend, ml, db).
    Требует DEEPSEEK_API_KEY для реальной генерации.
    """
    import httpx
    
    BASE_URL = "http://localhost:8000"
    
    async with httpx.AsyncClient(timeout=300.0) as client:
        # 1. Загрузить профиль
        import json
        import io
        
        files = {
            'file': ('profile.json', io.BytesIO(json.dumps(SAMPLE_PROFILE).encode()), 'application/json')
        }
        
        response = await client.post(f"{BASE_URL}/api/profiles", files=files)
        assert response.status_code == 200, f"Profile upload failed: {response.text}"
        
        profile_data = response.json()
        profile_id = profile_data['profile_id']
        assert profile_data['validation']['valid'], "Profile validation failed"
        
        # 2. Запустить генерацию
        response = await client.post(
            f"{BASE_URL}/api/tracks/generate",
            json={'profile_id': profile_id}
        )
        assert response.status_code == 202, f"Generation start failed: {response.text}"
        
        generation_data = response.json()
        track_id = generation_data['track_id']
        
        # 3. Дождаться завершения (polling)
        import asyncio
        max_attempts = 60  # 5 минут
        for attempt in range(max_attempts):
            response = await client.get(f"{BASE_URL}/api/tracks/{track_id}")
            if response.status_code == 200:
                track = response.json()
                if track['status'] == 'completed':
                    break
                elif track['status'] == 'failed':
                    pytest.fail(f"Generation failed: {track.get('error_message')}")
            
            await asyncio.sleep(5)
        else:
            pytest.fail("Generation timeout (5 minutes)")
        
        # 4. Проверить PersonalizedTrack
        assert track['track_data'], "track_data is empty"
        assert 'competencies' in track['track_data'] or 'metadata' in track['generation_metadata']
        
        # 5. Проверить логи B1-B8
        response = await client.get(f"{BASE_URL}/api/logs/track/{track_id}")
        assert response.status_code == 200, f"Logs fetch failed: {response.text}"
        
        logs = response.json()
        assert len(logs) == 8, f"Expected 8 logs (B1-B8), got {len(logs)}"
        
        step_names = [log['step_name'] for log in logs]
        expected_steps = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8']
        assert step_names == expected_steps, f"Steps mismatch: {step_names}"


@pytest.mark.skip(reason="Требует DeepSeek API ключ и запущенные контейнеры")
def test_e2e_placeholder():
    """
    Placeholder для E2E теста.
    
    Раскомментируйте test_full_generation_cycle и запустите с:
    pytest backend/tests/e2e/test_phase3_e2e.py -v
    """
    pass
