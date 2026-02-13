#!/usr/bin/env python3
"""Quick script to run pipeline with mock LLM (no real API calls)."""

import asyncio
import json
import sys
import time
import uuid
from pathlib import Path

# Enable mock mode
import os

os.environ["MOCK_LLM"] = "true"


async def main():
    """Run pipeline with mock LLM client."""
    # Import after setting environment variable
    from ml.src.services.llm_client_factory import get_llm_client, is_mock_mode
    from ml.src.services.pipeline_orchestrator import run_pipeline

    print("=" * 70)
    print("🎭 MOCK PIPELINE RUN (No real API calls)")
    print("=" * 70)
    print(f"Mock mode: {is_mock_mode()}")
    print()

    # Load test profile
    profile_path = Path("../docs/test_profile_1.json")
    if not profile_path.exists():
        profile_path = Path("docs/test_profile_1.json")

    if not profile_path.exists():
        print("❌ Error: test_profile_1.json not found")
        return 1

    with open(profile_path) as f:
        profile = json.load(f)

    track_id = uuid.uuid4()

    print(f"📋 Profile: {profile['role']}")
    print(f"📚 Topic: {profile['topic']}")
    print(f"🆔 Track ID: {track_id}")
    print()

    print("⏳ Running pipeline with mock LLM...")
    start_time = time.time()

    try:
        result = await run_pipeline(
            profile=profile, track_id=track_id, algorithm_version="v1.0.0-mock"
        )

        elapsed = time.time() - start_time

        print()
        print("=" * 70)
        print("✅ SUCCESS!")
        print("=" * 70)
        print(f"⏱️  Duration: {elapsed:.2f}s")
        print(f"🆔 Track ID: {track_id}")

        metadata = result.get("generation_metadata", {})
        print(f"📊 Steps: {len(metadata.get('steps_log', []))}")
        print(f"🔢 LLM calls: {metadata.get('llm_calls_count', 0)}")
        print(f"🪙 Total tokens: {metadata.get('total_tokens', 0)}")
        print()

        print("Now run validation:")
        print(
            f"docker exec nastavnik_ml python3 scripts/validate_pipeline.py "
            f"--mode logs --track-id {track_id}"
        )

        return 0

    except Exception as e:
        print()
        print("=" * 70)
        print("❌ ERROR")
        print("=" * 70)
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
