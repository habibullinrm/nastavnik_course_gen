#!/usr/bin/env python3
"""Test all pipeline steps with mock client."""

import asyncio
import json
import os
import sys
import time

# Enable mock mode
os.environ["MOCK_LLM"] = "true"

from ml.src.services.llm_client_factory import get_llm_client


async def test_all_steps():
    """Test all pipeline steps with mock client."""
    client = await get_llm_client()

    print("=" * 70)
    print("🎭 MOCK PIPELINE - ALL STEPS TEST")
    print("=" * 70)
    print()

    # Define test prompts for each step
    test_cases = [
        ("B1_validate", "You are validating a student profile..."),
        ("B2_competencies", "Formulate competencies from the profile..."),
        (
            "B3_ksa_matrix",
            "Decompose competencies into Knowledge-Skills-Habits matrix...",
        ),
        ("B4_learning_units", "Design learning units from the KSA matrix..."),
        ("B5_hierarchy", "Create a leveled hierarchy of learning units..."),
        (
            "B6_problem_formulations",
            "Create problem formulations for each cluster...",
        ),
    ]

    results = []
    total_start = time.time()

    for step_name, prompt in test_cases:
        step_start = time.time()

        try:
            response = await client.complete(prompt)
            elapsed = time.time() - step_start

            # Parse response
            content = response["choices"][0]["message"]["content"]
            tokens = response["usage"]["total_tokens"]

            # Try to parse as JSON
            try:
                data = json.loads(content)
                data_keys = list(data.keys())
                status = "✅"
            except:
                data_keys = ["invalid_json"]
                status = "⚠️"

            results.append(
                {
                    "step": step_name,
                    "status": status,
                    "time": elapsed,
                    "tokens": tokens,
                    "keys": data_keys,
                }
            )

            print(
                f"{status} {step_name:20s} {elapsed*1000:6.1f}ms  "
                f"{tokens:5d} tokens  {len(data_keys)} keys"
            )

        except Exception as e:
            print(f"❌ {step_name:20s} FAILED: {str(e)[:50]}")
            results.append({"step": step_name, "status": "❌", "error": str(e)})

    total_elapsed = time.time() - total_start

    print()
    print("=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)

    stats = client.get_stats()

    success = sum(1 for r in results if r["status"] == "✅")
    total = len(results)

    print(f"Steps completed: {success}/{total}")
    print(f"Total time: {total_elapsed:.3f}s")
    print(f"Avg time per step: {total_elapsed/total*1000:.1f}ms")
    print(f"Total LLM calls: {stats['call_count']}")
    print(f"Total tokens: {stats['total_tokens']}")
    print()
    print(f"⚡ Speed vs Real mode: ~{180/total_elapsed:.0f}x faster")
    print(f"   (Real mode: ~180s, Mock mode: {total_elapsed:.1f}s)")
    print()

    return 0 if success == total else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(test_all_steps()))
