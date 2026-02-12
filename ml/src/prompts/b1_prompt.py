"""Prompt template for B1: Profile Validation and Enrichment."""


def get_b1_prompt(profile: dict) -> str:
    """
    Generate prompt for B1: Validate and enrich student profile.

    Validates CRITICAL fields, calculates effective_level, enriches with system-generated data.
    """
    return f"""You are an educational expert analyzing a student profile for personalized course generation.

INPUT PROFILE:
```json
{profile}
```

TASK: Validate and enrich this profile with the following steps:

1. **Validation**:
   - Check all CRITICAL fields are present: topic, subject_area, experience_level, desired_outcomes, target_tasks, subtasks, confusing_concepts, diagnostic_result, weekly_hours, success_criteria
   - Report any missing CRITICAL fields as errors
   - Report missing IMPORTANT fields (schedule, practice_windows) as warnings

2. **Effective Level Calculation**:
   Using the matrix:
   - If experience_level="zero" OR diagnostic_result="zero" → effective_level="zero"
   - If experience_level="beginner" AND diagnostic_result in ["gaps", "misconceptions"] → effective_level="beginner"
   - If experience_level="intermediate" AND diagnostic_result="partial" → effective_level="intermediate"
   - If experience_level="advanced" AND diagnostic_result="mastery" → effective_level="advanced"
   - Otherwise, use the LOWER of the two levels

3. **Time Budget Calculation**:
   - weekly_time_budget_minutes = weekly_hours * 60
   - Calculate estimated_weeks based on task complexity (minimum 4 weeks, maximum 52 weeks)
   - Analyze the number of subtasks and target_tasks to estimate realistic duration
   - total_time_budget_minutes = estimated_weeks * weekly_time_budget_minutes

4. **Output Requirements**:
   Return a JSON object with this exact structure:
   {{
     "original_profile": <the input profile>,
     "validation_status": "valid" | "valid_with_warnings" | "invalid",
     "validation_errors": [<list of critical errors>],
     "validation_warnings": [<list of warnings>],
     "effective_level": "zero" | "beginner" | "intermediate" | "advanced",
     "estimated_weeks": <integer 4-52>,
     "weekly_time_budget_minutes": <integer>,
     "total_time_budget_minutes": <integer>
   }}

IMPORTANT: Respond ONLY with valid JSON. No explanations outside the JSON.
"""
