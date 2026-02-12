"""Prompt template for B4: Learning Units Design."""


def get_b4_prompt(ksa_matrix: dict) -> str:
    """Generate prompt for B4: Design learning units from KSA items."""
    return f"""You are an instructional designer creating learning units based on the 4C/ID model.

KSA MATRIX:
```json
{ksa_matrix}
```

TASK: Design three types of learning units and organize them into clusters.

UNIT TYPES:
1. **Theory Units**: For Knowledge items
   - Explanations, examples, conceptual understanding
   - Estimated time: 15-45 minutes each

2. **Practice Units**: For Skill items
   - Guided practice, exercises with feedback
   - Estimated time: 30-90 minutes each

3. **Automation Units**: For Habit items
   - Repeated practice, fluency building
   - Estimated time: 30-60 minutes each

4. **Clusters**: Group related units (4C/ID "whole task")
   - Each cluster = theory + practice + automation for a coherent concept
   - Total time per cluster: 60-180 minutes

OUTPUT JSON:
{{
  "theory_units": [
    {{
      "id": "tu1",
      "title": "...",
      "knowledge_ids": ["k1", "k2"],
      "estimated_minutes": 30,
      "content_outline": "Brief outline of what will be taught"
    }}
  ],
  "practice_units": [
    {{
      "id": "pu1",
      "title": "...",
      "skill_ids": ["s1"],
      "estimated_minutes": 60,
      "exercises_outline": "Types of exercises"
    }}
  ],
  "automation_units": [
    {{
      "id": "au1",
      "title": "...",
      "habit_ids": ["h1"],
      "estimated_minutes": 45,
      "practice_outline": "Repeated practice activities"
    }}
  ],
  "clusters": [
    {{
      "id": "cluster1",
      "title": "...",
      "theory_units": ["tu1"],
      "practice_units": ["pu1"],
      "automation_units": ["au1"],
      "total_minutes": 135
    }}
  ]
}}

IMPORTANT: Respond ONLY with valid JSON.
"""
