"""Prompt template for B5: Hierarchy and Levels."""


def get_b5_prompt(learning_units: dict, time_budget_minutes: int, estimated_weeks: int) -> str:
    """Generate prompt for B5: Organize units into levels and sequence."""
    from ml.src.prompts.json_utils import to_json
    units_json = to_json(learning_units)
    weekly_budget = time_budget_minutes // estimated_weeks if estimated_weeks > 0 else 0

    return f"""You are a curriculum architect organizing learning units into a progressive hierarchy.

LEARNING UNITS & CLUSTERS DATA:
{units_json}

TIME CONSTRAINTS:
- Total time budget: {time_budget_minutes} minutes ({time_budget_minutes // 60} hours)
- Target weeks: {estimated_weeks}
- Weekly budget: {weekly_budget} minutes/week

TASK: Create a leveled hierarchy with proper sequencing.

## Levels Definition (progressive difficulty):

1. **Foundational**: Basic concepts and skills
2. **Intermediate**: Application and integration
3. **Advanced**: Complex problem-solving
4. **Integrative**: Synthesis and mastery

## Process Guidelines:

1. **Assign clusters to levels** based on complexity and dependencies
2. **Create unit sequence** by topologically sorting all units (respecting dependencies)
3. **Apply time compression if needed**:
   - If total time exceeds budget, compress by:
     * Merging similar units
     * Reducing automation unit duration
     * Keeping critical path intact
   - Set time_compression_applied = true if compression was used

## OUTPUT FORMAT
Return ONLY a valid JSON object (no markdown, no explanations):

{{
  "levels": [
    {{
      "level": "foundational" | "intermediate" | "advanced" | "integrative",
      "clusters": ["cluster1", "cluster2"],
      "estimated_weeks": 3
    }}
  ],
  "unit_sequence": ["tu1", "pu1", "au1", "tu2", "pu2", "au2"],
  "time_compression_applied": true | false,
  "total_weeks": 12
}}

CRITICAL RULES:
1. Output MUST be valid JSON (test with json.loads before responding)
2. ALL fields are REQUIRED - no field can be null or missing
3. levels array must contain 1-4 elements (one for each level used)
4. Each level MUST have: level, clusters, estimated_weeks
5. level must be one of: "foundational", "intermediate", "advanced", "integrative"
6. clusters must be array of cluster IDs from input data
7. unit_sequence must be array of unit IDs (tu*, pu*, au*) in execution order
8. unit_sequence must include ALL units from all clusters
9. unit_sequence must respect dependencies (prerequisites before dependents)
10. time_compression_applied must be boolean (true or false)
11. total_weeks must be positive integer
12. Sum of estimated_weeks across all levels should approximately equal total_weeks
13. Do NOT wrap JSON in markdown code blocks
14. Do NOT include any units not present in input data

Begin your response with {{ and end with }}
"""
