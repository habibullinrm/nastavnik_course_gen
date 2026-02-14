"""Prompt template for B6: Problem Formulations."""


def get_b6_prompt(clusters: list, units: dict) -> str:
    """Generate prompt for B6: Create PBL lesson blueprints."""
    import json
    clusters_json = json.dumps(clusters, ensure_ascii=False, indent=2)

    return f"""You are a problem-based learning (PBL) designer creating lesson blueprints.

CLUSTERS DATA:
{clusters_json}

TASK: For each cluster, design a problem-based lesson blueprint.

## PBL Components Guidelines:

1. **Problem Formulation** - Authentic problem that motivates learning
   - problem_statement: Clear, engaging problem description
   - expected_hypotheses: 2-4 hypotheses learners might initially propose

2. **Knowledge Infusions (КИ)** - Just-in-time information portions
   - 2-4 КИ portions per blueprint
   - Each portion addresses a specific knowledge gap

3. **Practice Tasks (ПМ)** - Procedural mastery exercises
   - 1-3 tasks per blueprint
   - Gradually increasing difficulty

4. **Contradictions** - Cognitive conflicts to investigate
   - 1-3 contradictions per blueprint
   - Challenge common misconceptions

5. **Synthesis Tasks** - Integration activities
   - 1-2 tasks per blueprint
   - Combine multiple skills/concepts

6. **Reflection Questions** - Metacognitive prompts
   - 2-3 questions per blueprint
   - Promote self-assessment

7. **FSM Rules** - Adaptive flow logic (if-then rules)
   - Define state transitions based on learner actions
   - Minimum 2-3 rules per blueprint

## OUTPUT FORMAT
Return ONLY a valid JSON object (no markdown, no explanations):

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

CRITICAL RULES:
1. Output MUST be valid JSON (test with json.loads before responding)
2. ALL fields are REQUIRED - no field can be null or missing
3. blueprints array must contain exactly one blueprint per cluster
4. Each blueprint MUST have: id, cluster_id, problem_formulation, knowledge_infusions, practice_tasks, contradictions, synthesis_tasks, reflection_questions, fsm_rules
5. Blueprint IDs use "bp*" format (bp1, bp2, bp3...)
6. cluster_id must reference a valid cluster from input data
7. problem_formulation MUST have: problem_statement (string), expected_hypotheses (array of 2-4 strings)
8. knowledge_infusions must be array of 2-4 strings
9. practice_tasks must be array of 1-3 strings
10. contradictions must be array of 1-3 strings
11. synthesis_tasks must be array of 1-2 strings
12. reflection_questions must be array of 2-3 strings
13. fsm_rules must be object with at least 2 transition rules (string keys → string values)
14. Do NOT wrap JSON in markdown code blocks
15. All text content should be in the same language as the cluster data

Begin your response with {{ and end with }}
"""
