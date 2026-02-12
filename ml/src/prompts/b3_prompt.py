"""Prompt template for B3: KSA Matrix (Knowledge-Skills-Habits)."""


def get_b3_prompt(profile: dict, competencies: dict) -> str:
    """Generate prompt for B3: Decompose competencies into KSA matrix."""
    return f"""You are an educational expert decomposing competencies into a Knowledge-Skills-Habits (KSA) matrix.

PROFILE CONTEXT:
- Topic: {profile.get('topic')}
- Confusing Concepts: {len(profile.get('confusing_concepts', []))}
- Subtasks: {len(profile.get('subtasks', []))}
- Barriers: {len(profile.get('key_barriers', []))}

COMPETENCIES:
```json
{competencies}
```

TASK: Decompose competencies into atomic KSA items with dependencies.

FRAMEWORK:
- **Knowledge (Знания)**: Concepts, facts, principles that must be understood
- **Skills (Умения)**: Procedures that can be executed with conscious effort
- **Habits (Навыки)**: Automated practices that don't require conscious thought

PROCESS:
1. Extract Knowledge items from:
   - confusing_concepts (learner confusion points)
   - key_barriers (knowledge gaps)
   - Implicit prerequisites for tasks

2. Extract Skill items from:
   - subtasks (specific procedures)
   - Decomposition of complex tasks into steps

3. Extract Habit items from:
   - success_criteria (indicators of mastery)
   - Repeated practices that should become automatic

4. Build dependency_graph:
   - Knowledge → Skills (skills require knowledge)
   - Skills → Habits (habits require skills)

OUTPUT JSON:
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
      "required_for": ["h1"]
    }}
  ],
  "habit_items": [
    {{
      "id": "h1",
      "title": "Brief name",
      "description": "What becomes automatic",
      "source": "mastery_signal:ms1",
      "requires_skills": ["s1"]
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

IMPORTANT: Respond ONLY with valid JSON.
"""
