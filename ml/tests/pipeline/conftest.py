"""Pytest fixtures for pipeline validation tests."""

import pytest


@pytest.fixture
def valid_b1_output():
    """Valid B1 step output."""
    return {
        "validation_status": "valid",
        "effective_level": "beginner",
        "estimated_weeks": 12,
        "weekly_time_budget_minutes": 300,
        "total_time_budget_minutes": 3600,
        "validation_errors": [],
        "validation_warnings": [],
    }


@pytest.fixture
def invalid_b1_output():
    """Invalid B1 step output (missing required fields)."""
    return {
        "validation_status": "valid",
        # Missing effective_level
        "estimated_weeks": 12,
        # Missing time budgets
    }


@pytest.fixture
def valid_b2_output():
    """Valid B2 step output."""
    return {
        "competencies": [
            {
                "id": "comp_1",
                "title": "Test Competency",
                "description": "Test description",
                "related_task_ids": ["t1"],
                "related_outcome_indices": [0],
                "level": "foundational",
            }
        ],
        "integral_competency_id": "comp_1",
        "competency_task_map": {"comp_1": ["t1"]},
        "competency_outcome_map": {"comp_1": [0]},
    }


@pytest.fixture
def valid_b3_output():
    """Valid B3 step output."""
    return {
        "knowledge_items": [
            {
                "id": "k1",
                "title": "Knowledge 1",
                "description": "Test knowledge",
                "source": "comp_1",
                "required_for": ["s1"],
            }
        ],
        "skill_items": [
            {
                "id": "s1",
                "title": "Skill 1",
                "description": "Test skill",
                "source": "comp_1",
                "requires_knowledge": ["k1"],
                "required_for": ["h1"],
            }
        ],
        "habit_items": [
            {
                "id": "h1",
                "title": "Habit 1",
                "description": "Test habit",
                "source": "comp_1",
                "requires_skills": ["s1"],
            }
        ],
        "dependency_graph": [
            {"from_id": "k1", "to_id": "s1", "dependency_type": "prerequisite"}
        ],
    }


@pytest.fixture
def invalid_b3_output():
    """Invalid B3 output with broken references."""
    return {
        "knowledge_items": [
            {
                "id": "k1",
                "title": "Knowledge 1",
                "description": "Test knowledge",
                "source": "comp_1",
                "required_for": ["s999"],  # Non-existent skill
            }
        ],
        "skill_items": [
            {
                "id": "s1",
                "title": "Skill 1",
                "description": "Test skill",
                "source": "comp_1",
                "requires_knowledge": ["k999"],  # Non-existent knowledge
                "required_for": [],
            }
        ],
        "habit_items": [],
        "dependency_graph": [
            {"from_id": "k999", "to_id": "s1", "dependency_type": "prerequisite"}
        ],
    }


@pytest.fixture
def valid_b4_output():
    """Valid B4 step output."""
    return {
        "theory_units": [
            {
                "id": "tu1",
                "title": "Theory Unit 1",
                "knowledge_ids": ["k1"],
                "estimated_minutes": 60,
                "content_outline": "Test content",
            }
        ],
        "practice_units": [
            {
                "id": "pu1",
                "title": "Practice Unit 1",
                "skill_ids": ["s1"],
                "estimated_minutes": 90,
                "exercises_outline": "Test exercises",
            }
        ],
        "automation_units": [
            {
                "id": "au1",
                "title": "Automation Unit 1",
                "habit_ids": ["h1"],
                "estimated_minutes": 120,
                "practice_outline": "Test practice",
            }
        ],
        "clusters": [
            {
                "id": "c1",
                "title": "Cluster 1",
                "theory_units": ["tu1"],
                "practice_units": ["pu1"],
                "automation_units": ["au1"],
                "total_minutes": 270,
            }
        ],
    }


@pytest.fixture
def valid_b5_output():
    """Valid B5 step output."""
    return {
        "levels": [
            {
                "level": "foundational",
                "clusters": ["c1"],
                "estimated_weeks": 4,
            }
        ],
        "unit_sequence": ["tu1", "pu1", "au1"],
        "time_compression_applied": False,
        "total_weeks": 4,
    }


@pytest.fixture
def invalid_b5_output():
    """Invalid B5 output with unknown unit IDs."""
    return {
        "levels": [
            {
                "level": "foundational",
                "clusters": ["c1"],
                "estimated_weeks": 4,
            }
        ],
        "unit_sequence": ["tu1", "pu999", "au1"],  # pu999 doesn't exist in B4
        "time_compression_applied": False,
        "total_weeks": 4,
    }
