"""Prompt template for B7: Schedule Assembly."""


def get_b7_prompt(
    hierarchy: dict, blueprints: dict, schedule_info: dict, total_weeks: int
) -> str:
    """Generate prompt for B7: Assemble weekly schedule."""
    import json
    hierarchy_json = json.dumps(hierarchy, ensure_ascii=False, indent=2)
    blueprints_json = json.dumps(blueprints, ensure_ascii=False, indent=2)
    schedule_json = json.dumps(schedule_info, ensure_ascii=False, indent=2)

    return f"""You are a schedule designer creating a personalized weekly learning schedule.

HIERARCHY & SEQUENCING DATA:
{hierarchy_json}

LESSON BLUEPRINTS DATA:
{blueprints_json}

LEARNER SCHEDULE DATA:
{schedule_json}

TARGET: {total_weeks} weeks

TASK: Distribute learning units across weeks and days according to learner's availability.

## Process Guidelines:

1. **Map unit_sequence to weeks** based on learner's schedule
2. **For each week**:
   - Assign units to available days
   - Respect daily time limits
   - Group related units together
   - Add checkpoints every 2-4 weeks

3. **Add support mechanisms**:
   - Scaffolding techniques for difficult concepts
   - Feedback points
   - Additional resources

## OUTPUT FORMAT
Return ONLY a valid JSON object (no markdown, no explanations):

{{
  "weeks": [
    {{
      "week_number": 1,
      "level": "foundational" | "intermediate" | "advanced" | "integrative",
      "theme": "Week theme description",
      "weekly_goals": ["goal1", "goal2"],
      "days": [
        {{
          "day_of_week": "Monday" | "Tuesday" | ... | "Sunday",
          "learning_units": ["tu1", "pu1"],
          "total_minutes": 90
        }}
      ],
      "checkpoint": null | {{
        "week_number": 4,
        "title": "Checkpoint title",
        "assessment_tasks": ["task1", "task2"],
        "criteria": ["criterion1"]
      }}
    }}
  ],
  "total_weeks": {total_weeks},
  "checkpoints": [
    {{
      "week_number": 4,
      "title": "Checkpoint 1",
      "assessment_tasks": ["task1", "task2"],
      "criteria": ["criterion1"]
    }}
  ],
  "final_assessment": {{
    "week": {total_weeks},
    "tasks": ["final task 1"],
    "criteria": ["criterion1"]
  }},
  "support_plan": {{
    "scaffolding_techniques": ["technique1"],
    "feedback_points": ["point1"],
    "resources": ["resource1"]
  }},
  "progress_milestones": [
    {{
      "week": 2,
      "title": "Milestone title",
      "criteria": ["criterion1"]
    }}
  ]
}}

CRITICAL RULES:
1. Output MUST be valid JSON (test with json.loads before responding)
2. ALL fields are REQUIRED - no field can be null or missing
3. weeks array must contain exactly {total_weeks} elements
4. Each week MUST have: week_number, level, theme, weekly_goals, days, checkpoint
5. week_number must be sequential (1, 2, 3, ..., {total_weeks})
6. level must be one of: "foundational", "intermediate", "advanced", "integrative"
7. weekly_goals must be array of 2-4 strings
8. days must be array of 1-7 day objects
9. Each day MUST have: day_of_week, learning_units, total_minutes
10. day_of_week must be valid day name (Monday-Sunday)
11. learning_units must be array of unit IDs from hierarchy.unit_sequence
12. checkpoint can be null or object with: week_number, title, assessment_tasks, criteria
13. checkpoints array must contain all non-null checkpoints from weeks
14. Add checkpoints every 2-4 weeks (approximately 2-4 checkpoints total)
15. final_assessment MUST have: week, tasks, criteria
16. support_plan MUST have: scaffolding_techniques, feedback_points, resources (arrays of 2-5 strings each)
17. progress_milestones must be array of 2-5 milestone objects
18. Each milestone MUST have: week, title, criteria
19. Do NOT wrap JSON in markdown code blocks
20. All unit IDs in days must exist in hierarchy.unit_sequence

Begin your response with {{ and end with }}
"""
