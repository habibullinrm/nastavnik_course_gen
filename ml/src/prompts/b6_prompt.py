"""Prompt template for B6: Problem Formulations."""


def get_b6_prompt(clusters: list, units: dict) -> str:
    """Generate prompt for B6: Create PBL lesson blueprints."""
    return f"""You are a problem-based learning (PBL) designer creating lesson blueprints.

CLUSTERS:
```json
{clusters}
```

TASK: For each cluster, design a problem-based lesson blueprint.

PBL COMPONENTS:
1. **Problem Formulation**: Authentic problem that motivates learning
2. **Expected Hypotheses**: What learners might initially think
3. **Knowledge Infusions (КИ)**: Just-in-time information portions
4. **Practice Tasks (ПМ)**: Procedural mastery exercises
5. **Contradictions**: Cognitive conflicts to investigate
6. **Synthesis Tasks**: Integration activities
7. **Reflection Questions**: Metacognitive prompts
8. **FSM Rules**: Adaptive flow logic (if-then rules for progression)

OUTPUT JSON:
{{
  "blueprints": [
    {{
      "id": "bp1",
      "cluster_id": "cluster1",
      "problem_formulation": {{
        "problem_statement": "Authentic problem description",
        "expected_hypotheses": ["hypothesis1", "hypothesis2"]
      }},
      "knowledge_infusions": ["КИ portion 1", "КИ portion 2"],
      "practice_tasks": ["Task 1", "Task 2"],
      "contradictions": ["Contradiction to explore"],
      "synthesis_tasks": ["Integration task"],
      "reflection_questions": ["Question 1", "Question 2"],
      "fsm_rules": {{
        "correct_hypothesis": "proceed_to_practice",
        "incorrect_hypothesis": "provide_ki_1",
        "mastery_achieved": "proceed_to_next_cluster"
      }}
    }}
  ]
}}

IMPORTANT: Respond ONLY with valid JSON.
"""
