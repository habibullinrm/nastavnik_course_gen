"""Prompt template for B2: Competency Formulation."""


def get_b2_prompt(validated_profile: dict) -> str:
    """
    Generate prompt for B2: Formulate competencies from tasks and outcomes.
    """
    profile = validated_profile["original_profile"]
    effective_level = validated_profile["effective_level"]

    return f"""You are an educational expert designing competencies for a personalized learning track.

VALIDATED PROFILE:
- Topic: {profile.get('topic')}
- Effective Level: {effective_level}
- Peak Task: {profile.get('peak_task_id')}
- Target Tasks: {len(profile.get('target_tasks', []))}
- Desired Outcomes: {profile.get('desired_outcomes')}

FULL PROFILE:
```json
{profile}
```

TASK: Formulate competencies that represent integrated capabilities the learner will develop.

PROCESS:
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

OUTPUT STRUCTURE:
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

IMPORTANT:
- Formulate 4-8 competencies (not too many, not too few)
- Use domain-specific terminology from the subject_area
- Respond ONLY with valid JSON
"""
