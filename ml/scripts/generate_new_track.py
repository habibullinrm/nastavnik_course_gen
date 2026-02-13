#!/usr/bin/env python3
"""Script to generate a new track for testing the fixed B3 prompt."""

import json
import sys
import uuid

import httpx


def main():
    """Generate new track with fixed B3 prompt."""
    # Read profile from docs
    with open("../docs/test_profile_1.json") as f:
        profile = json.load(f)

    new_track_id = str(uuid.uuid4())

    print(f"🚀 Запуск генерации с исправленным промптом B3")
    print(f"   Track ID: {new_track_id}")
    print(f"   Профиль: {profile['role']}")
    print(f"   Тема: {profile['topic']}")
    print()

    request_data = {
        "profile": profile,
        "track_id": new_track_id,
        "algorithm_version": "v1.0.0",
    }

    print("⏳ Отправка запроса (это займет несколько минут)...")
    try:
        response = httpx.post(
            "http://localhost:8001/pipeline/run",
            json=request_data,
            timeout=600.0,
        )

        print(f"✅ Ответ получен: HTTP {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print()
            print("=" * 70)
            print("УСПЕХ! Трек сгенерирован")
            print("=" * 70)
            print(f"Track ID: {new_track_id}")
            print(
                f"Validation B8: {result.get('validation_b8', {}).get('final_status', 'N/A')}"
            )

            metadata = result.get("generation_metadata", {})
            print(f"Duration: {metadata.get('total_duration_sec', 0):.1f}s")
            print(f"LLM calls: {metadata.get('llm_calls_count', 0)}")
            print(f"Total tokens: {metadata.get('total_tokens', 0)}")
            print()
            print("Теперь запустите валидацию:")
            print(
                f"docker exec nastavnik_ml python3 scripts/validate_pipeline.py --mode logs --track-id {new_track_id}"
            )

            # Save track_id for later use
            with open("/tmp/last_track_id.txt", "w") as f:
                f.write(new_track_id)

            return 0
        else:
            print(f"❌ Ошибка {response.status_code}: {response.text[:500]}")
            return 1

    except Exception as e:
        print(f"❌ Исключение: {e}")
        import traceback

        traceback.print_exc()
        return 2


if __name__ == "__main__":
    sys.exit(main())
