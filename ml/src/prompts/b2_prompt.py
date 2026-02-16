"""Prompt template for B2: Competency Formulation."""


def get_b2_prompt(validated_profile: dict) -> str:
    """
    Generate prompt for B2: Formulate competencies from tasks and outcomes.
    """
    from ml.src.prompts.json_utils import to_json
    profile = validated_profile["original_profile"]
    effective_level = validated_profile["effective_level"]
    profile_json = to_json(profile)

    return f"""You are an educational expert designing competencies for a personalized learning track.

VALIDATED PROFILE:
- Topic: {profile.get('topic')}
- Effective Level: {effective_level}
- Peak Task: {profile.get('peak_task_id')}
- Target Tasks: {len(profile.get('target_tasks', []))}
- Desired Outcomes: {profile.get('desired_outcomes')}

FULL PROFILE DATA:
{profile_json}

TASK: Formulate competencies that represent integrated capabilities the learner will develop.

## Process Guidelines:

1. **Identify the Integral Competency**:
   - This is the highest-level competency corresponding to the peak_task
   - Should integrate all other competencies
   - Should align with the most complex desired_outcome

2. **Formulate Component Competencies**:
   - For each task in task_hierarchy, formulate a specific competency
   - Each competency should:
     * Be actionable (start with verbs like "analyze", "construct", "evaluate")
     * Map to specific target_tasks
     * Support specific desired_outcomes
   - Assign level: "foundational" (basics), "intermediate" (application), "advanced" (complex tasks), "integrative" (peak task)

3. **Create Mappings**:
   - competency_task_map: which tasks develop which competencies
   - competency_outcome_map: which competencies support which outcomes (by index)

4. **Ensure Coverage**:
   - ALL desired_outcomes must be covered by at least one competency
   - ALL target_tasks must map to at least one competency

## OUTPUT FORMAT
Return ONLY a valid JSON object (no markdown, no explanations):

{{
  "competencies": [
    {{
      "id": "comp_1",
      "title": "Brief competency name",
      "description": "Detailed description of what learner can do",
      "related_task_ids": ["t1", "t2"],
      "related_outcome_indices": [0, 1],
      "level": "foundational" | "intermediate" | "advanced" | "integrative"
    }}
  ],
  "integral_competency_id": "comp_X",
  "competency_task_map": {{
    "comp_1": ["t1", "t2"],
    "comp_2": ["t3"]
  }},
  "competency_outcome_map": {{
    "comp_1": [0, 1],
    "comp_2": [2]
  }}
}}

CRITICAL RULES:
1. Output MUST be valid JSON (test with json.loads before responding)
2. ALL fields are REQUIRED - no field can be null or missing
3. Formulate 4-8 competencies (not too many, not too few)
4. Each competency MUST have: id, title, description, related_task_ids, related_outcome_indices, level
5. integral_competency_id MUST reference an existing competency id
6. competency_task_map and competency_outcome_map MUST be objects with competency ids as keys
7. related_task_ids and related_outcome_indices must be arrays (can be empty [])
8. level must be one of: "foundational", "intermediate", "advanced", "integrative"
9. Do NOT wrap JSON in markdown code blocks
10. Use domain-specific terminology from the subject_area

Begin your response with {{ and end with }}
"""
