"""Prompt template for B8: Track Validation."""


def get_b8_prompt(complete_track: dict, profile: dict) -> str:
    """Generate prompt for B8: Validate the complete track."""
    from ml.src.prompts.json_utils import to_json
    profile_json = to_json(profile)
    track_json = to_json(complete_track)

    return f"""You are a quality assurance expert validating a generated learning track.

ORIGINAL PROFILE DATA:
{profile_json}

COMPLETE TRACK DATA:
{track_json}

TASK: Perform comprehensive validation with 22 checks across 5 categories.

## Validation Check Categories:

### 1. Coverage Checks (3 checks)
- outcomes_coverage: All desired_outcomes covered by competencies
- tasks_mapped: All target_tasks mapped to learning activities
- success_criteria_addressed: All success_criteria addressed in track

### 2. Dependency Checks (5 checks)
- circular_dependencies: No circular dependencies in KSA graph
- prerequisite_ordering: Prerequisites taught before dependent skills
- topological_order: Proper topological ordering in unit_sequence
- ksa_references: All KSA references valid
- unit_dependencies: Unit prerequisites respected

### 3. Time Checks (4 checks)
- total_time_budget: Total time fits within budget
- weekly_distribution: Weekly distribution matches availability
- unit_time_realistic: Realistic time estimates per unit
- checkpoint_timing: Checkpoints at appropriate intervals (every 2-4 weeks)

### 4. Consistency Checks (6 checks)
- competencies_level_match: Competencies align with profile level
- units_ksa_match: Units match specified KSA items
- blueprint_cluster_match: Blueprints match clusters
- schedule_hierarchy_match: Schedule follows hierarchy
- level_progression: Levels progress logically (foundational→intermediate→advanced→integrative)
- content_completeness: All content areas covered

### 5. FSM Readiness (4 checks)
- blueprints_have_fsm: All lesson blueprints have FSM rules
- problem_formulations_defined: Problem formulations are well-defined
- adaptive_paths_complete: Adaptive flow paths complete
- hypothesis_coverage: Expected hypotheses cover likely learner responses

## Severity Levels:
- **critical**: Must be fixed (track unusable)
- **warning**: Should be reviewed (track usable but not optimal)
- **info**: Enhancement suggestions

## OUTPUT FORMAT
Return ONLY a valid JSON object (no markdown, no explanations):

{{
  "overall_valid": true | false,
  "checks": [
    {{
      "check_name": "outcomes_coverage",
      "passed": true | false,
      "severity": "critical" | "warning" | "info",
      "message": "Detailed check result message"
    }}
  ],
  "critical_failures": 0,
  "warnings": 2,
  "retry_count": 0,
  "final_status": "validated" | "validated_with_warnings" | "failed"
}}

CRITICAL RULES:
1. Output MUST be valid JSON (test with json.loads before responding)
2. ALL fields are REQUIRED - no field can be null or missing
3. checks array must contain exactly 22 check objects (one per validation check)
4. Each check MUST have: check_name, passed, severity, message
5. check_name must match one of the 22 predefined check names listed above
6. passed must be boolean (true or false)
7. severity must be one of: "critical", "warning", "info"
8. message must be non-empty string describing the check result
9. critical_failures must equal count of checks where passed=false AND severity="critical"
10. warnings must equal count of checks where passed=false AND severity="warning"
11. retry_count must be integer (0 if first attempt)
12. overall_valid = true if critical_failures == 0, false otherwise
13. final_status logic:
    - If critical_failures > 0: "failed"
    - If critical_failures == 0 AND warnings > 0: "validated_with_warnings"
    - If critical_failures == 0 AND warnings == 0: "validated"
14. Do NOT wrap JSON in markdown code blocks
15. All 22 checks must be performed and reported

Begin your response with {{ and end with }}
"""
