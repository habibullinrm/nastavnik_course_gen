"""Prompt template for B8: Track Validation."""


def get_b8_prompt(complete_track: dict, profile: dict) -> str:
    """Generate prompt for B8: Validate the complete track."""
    return f"""You are a quality assurance expert validating a generated learning track.

ORIGINAL PROFILE:
```json
{profile}
```

COMPLETE TRACK:
```json
{complete_track}
```

TASK: Perform comprehensive validation with 22 checks.

VALIDATION CHECKS:
1. **Coverage Checks**:
   - All desired_outcomes covered by competencies
   - All target_tasks mapped to learning activities
   - All success_criteria addressed

2. **Dependency Checks**:
   - No circular dependencies in KSA graph
   - Prerequisites taught before dependent skills
   - Proper topological ordering

3. **Time Checks**:
   - Total time fits within budget
   - Weekly distribution matches availability
   - Realistic time estimates per unit

4. **Consistency Checks**:
   - Competencies align with profile level
   - Units match specified KSA items
   - Checkpoints at appropriate intervals

5. **FSM Readiness**:
   - All lesson blueprints have FSM rules
   - Problem formulations are well-defined
   - Adaptive flow paths complete

SEVERITY LEVELS:
- **critical**: Must be fixed (track unusable)
- **warning**: Should be reviewed (track usable but not optimal)
- **info**: Enhancement suggestions

OUTPUT JSON:
{{
  "overall_valid": true/false,
  "checks": [
    {{
      "check_name": "outcomes_coverage",
      "passed": true,
      "severity": "critical",
      "message": "All 3 desired outcomes covered"
    }}
  ],
  "critical_failures": 0,
  "warnings": 2,
  "retry_count": 0,
  "final_status": "validated" | "validated_with_warnings" | "failed"
}}

IMPORTANT:
- If critical_failures > 0, final_status = "failed"
- If critical_failures == 0 and warnings > 0, final_status = "validated_with_warnings"
- Otherwise, final_status = "validated"
- Respond ONLY with valid JSON
"""
