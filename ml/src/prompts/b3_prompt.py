"""Prompt template for B3: KSA Matrix (Knowledge-Skills-Habits)."""


def get_b3_prompt(profile: dict, competencies: dict) -> str:
    """Generate prompt for B3: Decompose competencies into KSA matrix."""
    import json
    competencies_json = json.dumps(competencies, ensure_ascii=False, indent=2)

    return f"""You are an educational expert decomposing competencies into a Knowledge-Skills-Habits (KSA) matrix.

PROFILE CONTEXT:
- Topic: {profile.get('topic')}
- Confusing Concepts: {len(profile.get('confusing_concepts', []))}
- Subtasks: {len(profile.get('subtasks', []))}
- Barriers: {len(profile.get('key_barriers', []))}

COMPETENCIES DATA:
{competencies_json}

TASK: Decompose competencies into atomic KSA items with dependencies.

## KSA Framework:

- **Knowledge (Знания)**: Concepts, facts, principles that must be understood
- **Skills (Умения)**: Procedures that can be executed with conscious effort
- **Habits (Навыки)**: Automated practices that don't require conscious thought

## Process Guidelines:

1. **Extract Knowledge items** from:
   - confusing_concepts (learner confusion points)
   - key_barriers (knowledge gaps)
   - Implicit prerequisites for tasks

2. **Extract Skill items** from:
   - subtasks (specific procedures)
   - Decomposition of complex tasks into steps

3. **Extract Habit items** from:
   - success_criteria (indicators of mastery)
   - Repeated practices that should become automatic

4. **Build dependency_graph**:
   - Knowledge → Skills (skills require knowledge)
   - Skills → Habits (habits require skills)

## OUTPUT FORMAT
Return ONLY a valid JSON object (no markdown, no explanations):

{{
  "knowledge_items": [
    {{
      "id": "k1",
      "title": "Brief name",
      "description": "What must be understood",
      "source": "confusing_concept:c1",
      "required_for": ["s1", "s2"]
    }}
  ],
  "skill_items": [
    {{
      "id": "s1",
      "title": "Brief name",
      "description": "What procedure to execute",
      "source": "subtask:st1",
      "requires_knowledge": ["k1"],
      "required_for": ["h1", "h2"]
    }}
  ],
  "habit_items": [
    {{
      "id": "h1",
      "title": "Brief name",
      "description": "What becomes automatic",
      "source": "mastery_signal:ms1",
      "requires_skills": ["s1", "s2"]
    }}
  ],
  "dependency_graph": [
    {{
      "from_id": "k1",
      "to_id": "s1",
      "dependency_type": "prerequisite"
    }}
  ]
}}

CRITICAL RULES:
1. Output MUST be valid JSON (test with json.loads before responding)
2. ALL fields are REQUIRED - no field can be null or missing
3. Arrays (knowledge_items, skill_items, habit_items, dependency_graph) must contain at least 1 element
4. ID format: knowledge_items use "k1", "k2"...; skill_items use "s1", "s2"...; habit_items use "h1", "h2"...
5. knowledge_items[].required_for must contain ONLY skill_ids (s*) OR habit_ids (h*)
6. skill_items[].required_for must contain ONLY habit_ids (h1, h2, h3...)
7. skill_items[].requires_knowledge must contain ONLY knowledge_ids (k1, k2, k3...)
8. habit_items[].requires_skills must contain ONLY skill_ids (s1, s2, s3...)
9. ALL IDs referenced in required_for/requires_* MUST exist in corresponding arrays
10. Do NOT wrap JSON in markdown code blocks
11. Each item MUST have: id, title, description, source fields
12. dependency_graph entries must have: from_id, to_id, dependency_type

Begin your response with {{ and end with }}
"""
