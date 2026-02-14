"""Prompt template for B4: Learning Units Design."""


def get_b4_prompt(ksa_matrix: dict) -> str:
    """Generate prompt for B4: Design learning units from KSA items."""
    import json
    ksa_json = json.dumps(ksa_matrix, ensure_ascii=False, indent=2)

    return f"""You are an instructional designer creating learning units based on the 4C/ID model.

KSA MATRIX DATA:
{ksa_json}

TASK: Design three types of learning units and organize them into clusters.

## Unit Types Guidelines:

1. **Theory Units** - For Knowledge items
   - Explanations, examples, conceptual understanding
   - Estimated time: 15-45 minutes each
   - Each unit covers 1-3 related knowledge items

2. **Practice Units** - For Skill items
   - Guided practice, exercises with feedback
   - Estimated time: 30-90 minutes each
   - Each unit covers 1-2 related skills

3. **Automation Units** - For Habit items
   - Repeated practice, fluency building
   - Estimated time: 30-60 minutes each
   - Each unit covers 1-2 related habits

4. **Clusters** - Group related units (4C/ID "whole task")
   - Each cluster = theory + practice + automation for a coherent concept
   - Total time per cluster: 60-180 minutes
   - Clusters should follow dependency order from KSA graph

## OUTPUT FORMAT
Return ONLY a valid JSON object (no markdown, no explanations):

{{
  "theory_units": [
    {{
      "id": "tu1",
      "title": "Unit title",
      "knowledge_ids": ["k1", "k2"],
      "estimated_minutes": 30,
      "content_outline": "Brief outline of what will be taught"
    }}
  ],
  "practice_units": [
    {{
      "id": "pu1",
      "title": "Unit title",
      "skill_ids": ["s1"],
      "estimated_minutes": 60,
      "exercises_outline": "Types of exercises"
    }}
  ],
  "automation_units": [
    {{
      "id": "au1",
      "title": "Unit title",
      "habit_ids": ["h1"],
      "estimated_minutes": 45,
      "practice_outline": "Repeated practice activities"
    }}
  ],
  "clusters": [
    {{
      "id": "cluster1",
      "title": "Cluster title",
      "theory_units": ["tu1"],
      "practice_units": ["pu1"],
      "automation_units": ["au1"],
      "total_minutes": 135
    }}
  ]
}}

CRITICAL RULES:
1. Output MUST be valid JSON (test with json.loads before responding)
2. ALL fields are REQUIRED - no field can be null or missing
3. Arrays (theory_units, practice_units, automation_units, clusters) must contain at least 1 element
4. ID format: theory_units use "tu*", practice_units use "pu*", automation_units use "au*", clusters use "cluster*"
5. Each theory_unit MUST have: id, title, knowledge_ids, estimated_minutes, content_outline
6. Each practice_unit MUST have: id, title, skill_ids, estimated_minutes, exercises_outline
7. Each automation_unit MUST have: id, title, habit_ids, estimated_minutes, practice_outline
8. Each cluster MUST have: id, title, theory_units, practice_units, automation_units, total_minutes
9. estimated_minutes constraints: theory (15-45), practice (30-90), automation (30-60), cluster total (60-180)
10. knowledge_ids must reference valid k* IDs from KSA matrix
11. skill_ids must reference valid s* IDs from KSA matrix
12. habit_ids must reference valid h* IDs from KSA matrix
13. cluster unit references (theory_units, practice_units, automation_units) must reference valid unit IDs
14. cluster.total_minutes should equal sum of all referenced units' estimated_minutes
15. Do NOT wrap JSON in markdown code blocks

Begin your response with {{ and end with }}
"""
