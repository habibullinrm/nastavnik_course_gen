"""Prompt template for B7: Schedule Assembly."""


def get_b7_prompt(
    hierarchy: dict, blueprints: dict, schedule_info: dict, total_weeks: int
) -> str:
    """Generate prompt for B7: Assemble weekly schedule."""
    return f"""You are a schedule designer creating a personalized weekly learning schedule.

HIERARCHY & SEQUENCING:
```json
{hierarchy}
```

LESSON BLUEPRINTS:
```json
{blueprints}
```

LEARNER SCHEDULE:
```json
{schedule_info}
```

TARGET: {total_weeks} weeks

TASK: Distribute learning units across weeks and days according to learner's availability.

PROCESS:
1. Map unit_sequence to weeks based on learner's schedule
2. For each week:
   - Assign units to available days
   - Respect daily time limits
   - Group related units together
   - Add checkpoints every 2-4 weeks

3. Add support mechanisms:
   - Scaffolding techniques for difficult concepts
   - Feedback points
   - Additional resources

OUTPUT JSON:
{{
  "weeks": [
    {{
      "week_number": 1,
      "level": "foundational",
      "theme": "Week theme",
      "weekly_goals": ["goal1", "goal2"],
      "days": [
        {{
          "day_of_week": "Monday",
          "learning_units": ["tu1", "pu1"],
          "total_minutes": 90
        }}
      ],
      "checkpoint": null
    }},
    {{
      "week_number": 4,
      "level": "intermediate",
      "theme": "Week theme with checkpoint",
      "weekly_goals": ["goal3"],
      "days": [...],
      "checkpoint": {{
        "week_number": 4,
        "title": "Checkpoint 1",
        "assessment_tasks": ["task1", "task2"]
      }}
    }}
  ],
  "total_weeks": {total_weeks},
  "checkpoints": [
    {{
      "week_number": 4,
      "title": "Checkpoint 1",
      "assessment_tasks": ["task1", "task2"]
    }}
  ],
  "final_assessment": {{
    "week": {total_weeks},
    "tasks": ["final task 1"]
  }},
  "support_plan": {{
    "scaffolding_techniques": ["technique1"],
    "feedback_points": ["point1"],
    "resources": ["resource1"]
  }},
  "progress_milestones": [
    {{
      "week": 2,
      "title": "First milestone",
      "criteria": ["criterion1"]
    }}
  ]
}}

IMPORTANT: Respond ONLY with valid JSON.
"""
