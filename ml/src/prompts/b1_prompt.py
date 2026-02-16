"""Prompt template for B1: Profile Validation and Enrichment."""


def get_b1_prompt(profile: dict) -> str:
    """
    Generate prompt for B1: Validate and enrich student profile.

    Validates CRITICAL fields, calculates effective_level, enriches with system-generated data.
    """
    from ml.src.prompts.json_utils import to_json
    profile_json = to_json(profile)

    return f"""You are an educational expert analyzing a student profile for personalized course generation.

INPUT PROFILE:
{profile_json}

TASK: Validate and enrich this profile. Follow these steps:

## Step 1: Validation
Check for CRITICAL fields:
- Required: topic, subject_area, experience_level, desired_outcomes, target_tasks, subtasks, confusing_concepts, diagnostic_result, weekly_hours, success_criteria
- Important (warn if missing): schedule, practice_windows

## Step 2: Effective Level Calculation
Apply this decision matrix:
- experience_level="zero" OR diagnostic_result="zero" → effective_level="zero"
- experience_level="beginner" AND diagnostic_result in ["gaps", "misconceptions", "zero"] → effective_level="beginner"
- experience_level="intermediate" AND diagnostic_result="partial" → effective_level="intermediate"
- experience_level="advanced" AND diagnostic_result="mastery" → effective_level="advanced"
- Default: use LOWER of (experience_level, diagnostic_result mapping)

## Step 3: Time Budget Calculation
- weekly_time_budget_minutes = weekly_hours * 60
- estimated_weeks: analyze task complexity, subtask count, experience_level
  - Beginners with many subtasks: 8-16 weeks
  - Intermediate with moderate tasks: 6-12 weeks
  - Advanced with few tasks: 4-8 weeks
  - Minimum: 4 weeks, Maximum: 52 weeks
- total_time_budget_minutes = estimated_weeks * weekly_time_budget_minutes

## OUTPUT FORMAT
Return ONLY a valid JSON object (no markdown, no explanations):

{{
  "validation_status": "valid" | "valid_with_warnings" | "invalid",
  "validation_errors": ["error1", "error2"],
  "validation_warnings": ["warning1"],
  "effective_level": "zero" | "beginner" | "intermediate" | "advanced",
  "estimated_weeks": <integer between 4 and 52>,
  "weekly_time_budget_minutes": <integer>,
  "total_time_budget_minutes": <integer>
}}

CRITICAL RULES:
1. Output MUST be valid JSON (test with json.loads before responding)
2. ALL fields are REQUIRED - no field can be null or missing
3. validation_errors and validation_warnings must be arrays (can be empty [])
4. estimated_weeks must be between 4 and 52
5. Do NOT wrap JSON in markdown code blocks
6. Do NOT include original_profile in output

Begin your response with {{ and end with }}
"""
