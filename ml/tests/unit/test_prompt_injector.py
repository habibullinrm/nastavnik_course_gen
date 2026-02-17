"""Тесты для prompt_injector — инъекция реальных данных в промпты."""

import json

import pytest

from ml.src.services.prompt_injector import (
    _replace_section,
    inject_real_data,
)


# ============================================================================
# Fixtures
# ============================================================================

REAL_PROFILE = {
    "topic": "Machine Learning",
    "subject_area": "Data Science",
    "experience_level": "intermediate",
    "desired_outcomes": ["Build ML models", "Understand theory"],
    "target_tasks": [
        {"id": "t1", "title": "Train a classifier"},
        {"id": "t2", "title": "Deploy model"},
    ],
    "subtasks": [
        {"id": "st1", "title": "Data preprocessing", "task_id": "t1"},
        {"id": "st2", "title": "Feature engineering", "task_id": "t1"},
    ],
    "confusing_concepts": [{"id": "c1", "concept": "Backpropagation"}],
    "diagnostic_result": "partial",
    "weekly_hours": 10,
    "success_criteria": ["Build end-to-end pipeline"],
    "key_barriers": [{"id": "b1", "description": "Math background"}],
    "peak_task_id": "t2",
}

B1_RESULT = {
    "validation_status": "valid",
    "effective_level": "intermediate",
    "estimated_weeks": 8,
    "weekly_time_budget_minutes": 600,
    "total_time_budget_minutes": 4800,
    "original_profile": REAL_PROFILE,
}

B2_RESULT = {
    "competencies": [
        {
            "id": "comp_1",
            "title": "Data Preprocessing",
            "description": "Can preprocess data",
            "related_task_ids": ["t1"],
            "related_outcome_indices": [0],
            "level": "foundational",
        }
    ],
    "integral_competency_id": "comp_1",
    "competency_task_map": {"comp_1": ["t1"]},
    "competency_outcome_map": {"comp_1": [0]},
}


# ============================================================================
# _replace_section
# ============================================================================


class TestReplaceSection:
    def test_basic_replacement(self):
        text = "HEADER:\nold content here\n\nNEXT:"
        result = _replace_section(text, "HEADER:", "NEXT:", "new content")
        assert "new content" in result
        assert "old content here" not in result
        assert result.startswith("HEADER:")
        assert "NEXT:" in result

    def test_multiline_replacement(self):
        text = "START:\nline1\nline2\nline3\n\nEND:"
        result = _replace_section(text, "START:", "END:", "replaced")
        assert "replaced" in result
        assert "line1" not in result

    def test_missing_labels_returns_original(self):
        text = "some text without labels"
        result = _replace_section(text, "MISSING:", "ALSO MISSING:", "data")
        assert result == text

    def test_preserves_surrounding_text(self):
        text = "before\n\nHEADER:\nold\n\nFOOTER:\n\nafter"
        result = _replace_section(text, "HEADER:", "FOOTER:", "new")
        assert "before" in result
        assert "after" in result


# ============================================================================
# inject_real_data — B1
# ============================================================================


class TestInjectB1:
    def test_replaces_profile_json(self):
        prompt = (
            "You are an expert.\n\n"
            "INPUT PROFILE:\n"
            '{"topic": "dummy"}\n\n'
            "TASK: Validate and enrich.\n\n"
            "## Step 1\n..."
        )
        result = inject_real_data(prompt, "B1_validate", REAL_PROFILE)
        assert "Machine Learning" in result
        assert '"topic": "dummy"' not in result
        assert "TASK: Validate and enrich." in result

    def test_preserves_task_section(self):
        prompt = (
            "Intro\n\nINPUT PROFILE:\ndummy data\n\nTASK: Do something.\n\nMore text"
        )
        result = inject_real_data(prompt, "B1_validate", REAL_PROFILE)
        assert "TASK: Do something." in result
        assert "More text" in result


# ============================================================================
# inject_real_data — B2
# ============================================================================


class TestInjectB2:
    def test_replaces_both_sections(self):
        prompt = (
            "Intro\n\n"
            "VALIDATED PROFILE:\n- Topic: dummy\n\n"
            "FULL PROFILE DATA:\n{}\n\n"
            "TASK: Formulate competencies.\n\nRest"
        )
        input_data = {"B1_validate": B1_RESULT}
        result = inject_real_data(prompt, "B2_competencies", REAL_PROFILE, input_data)

        # Validated profile summary should have real topic
        assert "Machine Learning" in result
        # Full profile data should have real JSON
        assert "Data Science" in result
        assert "TASK: Formulate competencies." in result


# ============================================================================
# inject_real_data — B3
# ============================================================================


class TestInjectB3:
    def test_replaces_context_and_competencies(self):
        prompt = (
            "Intro\n\n"
            "PROFILE CONTEXT:\n- Topic: dummy\n\n"
            "COMPETENCIES DATA:\n{}\n\n"
            "TASK: Decompose.\n\nRest"
        )
        input_data = {"B2_competencies": B2_RESULT}
        result = inject_real_data(prompt, "B3_ksa_matrix", REAL_PROFILE, input_data)

        assert "Machine Learning" in result
        assert "Data Preprocessing" in result
        assert "TASK: Decompose." in result


# ============================================================================
# inject_real_data — B4
# ============================================================================


class TestInjectB4:
    def test_replaces_ksa_data(self):
        prompt = "Intro\n\nKSA MATRIX DATA:\n{}\n\nTASK: Design units.\n\nRest"
        b3_data = {"knowledge_items": [{"id": "k1", "title": "Neural Networks"}]}
        input_data = {"B3_ksa_matrix": b3_data}
        result = inject_real_data(prompt, "B4_learning_units", REAL_PROFILE, input_data)

        assert "Neural Networks" in result
        assert "TASK: Design units." in result


# ============================================================================
# inject_real_data — B5
# ============================================================================


class TestInjectB5:
    def test_replaces_units_and_time(self):
        prompt = (
            "Intro\n\n"
            "LEARNING UNITS & CLUSTERS DATA:\n{}\n\n"
            "TIME CONSTRAINTS:\n- old time\n\n"
            "TASK: Create hierarchy.\n\nRest"
        )
        b4_data = {"theory_units": [{"id": "tu1"}], "clusters": []}
        input_data = {"B4_learning_units": b4_data, "B1_validate": B1_RESULT}
        result = inject_real_data(prompt, "B5_hierarchy", REAL_PROFILE, input_data)

        assert "tu1" in result
        assert "600 minutes" in result  # from B1_RESULT.weekly_time_budget_minutes
        assert "old time" not in result
        assert "TASK: Create hierarchy." in result


# ============================================================================
# inject_real_data — B7
# ============================================================================


class TestInjectB7:
    def test_replaces_all_four_sections(self):
        prompt = (
            "Intro\n\n"
            "HIERARCHY & SEQUENCING DATA:\n{}\n\n"
            "LESSON BLUEPRINTS DATA:\n{}\n\n"
            "LEARNER SCHEDULE DATA:\n{}\n\n"
            "TARGET: 12 weeks\n\n"
            "TASK: Distribute.\n\nRest"
        )
        b5_data = {"levels": [], "unit_sequence": [], "total_weeks": 8}
        b6_data = {"blueprints": [{"id": "bp1"}]}
        input_data = {"B5_hierarchy": b5_data, "B6_problem_formulations": b6_data}
        result = inject_real_data(prompt, "B7_schedule", REAL_PROFILE, input_data)

        assert "unit_sequence" in result
        assert "bp1" in result
        assert "weekly_hours" in result
        assert "8 weeks" in result
        assert "TASK: Distribute." in result


# ============================================================================
# inject_real_data — B8
# ============================================================================


class TestInjectB8:
    def test_replaces_profile_and_track(self):
        prompt = (
            "Intro\n\n"
            "ORIGINAL PROFILE DATA:\n{}\n\n"
            "COMPLETE TRACK DATA:\n{}\n\n"
            "TASK: Validate.\n\nRest"
        )
        input_data = {"B1_validate": B1_RESULT, "B2_competencies": B2_RESULT}
        result = inject_real_data(prompt, "B8_validation", REAL_PROFILE, input_data)

        assert "Machine Learning" in result
        assert "B1_validate" in result
        assert "B2_competencies" in result
        assert "TASK: Validate." in result


# ============================================================================
# Edge cases
# ============================================================================


class TestEdgeCases:
    def test_unknown_step_returns_original(self):
        prompt = "some prompt text"
        result = inject_real_data(prompt, "UNKNOWN_STEP", REAL_PROFILE)
        assert result == prompt

    def test_empty_input_data(self):
        prompt = (
            "Intro\n\nINPUT PROFILE:\ndummy\n\nTASK: Do.\n\nRest"
        )
        result = inject_real_data(prompt, "B1_validate", REAL_PROFILE, None)
        assert "Machine Learning" in result

    def test_real_baseline_prompt_b1(self):
        """Тест с реальным baseline промптом B1."""
        from ml.src.services.prompt_reader import get_baseline_prompt

        baseline = get_baseline_prompt("B1_validate")
        result = inject_real_data(baseline, "B1_validate", REAL_PROFILE)

        # Должен содержать реальные данные
        assert "Machine Learning" in result
        # Не должен содержать dummy данные
        assert "Python programming" not in result
        # Структура промпта сохранена
        assert "TASK:" in result
        assert "## Step 1" in result

    def test_real_baseline_prompt_b2(self):
        """Тест с реальным baseline промптом B2."""
        from ml.src.services.prompt_reader import get_baseline_prompt

        baseline = get_baseline_prompt("B2_competencies")
        input_data = {"B1_validate": B1_RESULT}
        result = inject_real_data(baseline, "B2_competencies", REAL_PROFILE, input_data)

        assert "Machine Learning" in result
        assert "TASK:" in result

    def test_prompt_with_modified_structure(self):
        """Пользователь изменил текст промпта, но метки на месте."""
        prompt = (
            "Ты — эксперт. Проанализируй профиль.\n\n"
            "INPUT PROFILE:\nstale dummy data\n\n"
            "TASK: Моя кастомная задача.\n\n"
            "Дополнительные инструкции..."
        )
        result = inject_real_data(prompt, "B1_validate", REAL_PROFILE)
        assert "Machine Learning" in result
        assert "stale dummy data" not in result
        assert "Моя кастомная задача" in result
        assert "Дополнительные инструкции" in result
