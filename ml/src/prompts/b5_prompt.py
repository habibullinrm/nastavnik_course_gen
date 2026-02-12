"""Prompt template for B5: Hierarchy and Levels."""


def get_b5_prompt(learning_units: dict, time_budget_minutes: int, estimated_weeks: int) -> str:
    """Generate prompt for B5: Organize units into levels and sequence."""
    return f"""You are a curriculum architect organizing learning units into a progressive hierarchy.

LEARNING UNITS & CLUSTERS:
```json
{learning_units}
```

TIME CONSTRAINTS:
- Total time budget: {time_budget_minutes} minutes ({time_budget_minutes // 60} hours)
- Target weeks: {estimated_weeks}
- Weekly budget: {time_budget_minutes // estimated_weeks if estimated_weeks > 0 else 0} minutes/week

TASK: Create a leveled hierarchy with proper sequencing.

LEVELS (progressive difficulty):
1. **Foundational**: Basic concepts and skills
2. **Intermediate**: Application and integration
3. **Advanced**: Complex problem-solving
4. **Integrative**: Synthesis and mastery

PROCESS:
1. Assign clusters to levels based on dependency graph
2. Topologically sort all units (respecting dependencies)
3. If total time exceeds budget, apply compression:
   - Merge similar units
   - Reduce automation unit duration
   - Keep critical path intact

OUTPUT JSON:
{{
  "levels": [
    {{
      "level": "foundational",
      "clusters": ["cluster1", "cluster2"],
      "estimated_weeks": 3
    }}
  ],
  "unit_sequence": ["tu1", "pu1", "au1", "tu2", ...],
  "time_compression_applied": true/false,
  "total_weeks": <integer>
}}

IMPORTANT: Respond ONLY with valid JSON.
"""
