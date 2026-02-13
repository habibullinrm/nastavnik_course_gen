"""Reference validator for ID integrity checks."""

from typing import Any

from .base import ValidationCheck, ValidationSeverity


class ReferenceValidator:
    """Validates ID references between pipeline steps."""

    def validate_b2_to_b3(
        self, b2_data: dict[str, Any], b3_data: dict[str, Any]
    ) -> list[ValidationCheck]:
        """
        Validate B2 → B3 references.

        Checks:
        - Competency IDs from B2 are referenced in B3 KSA items
        """
        checks = []

        # Extract competency IDs from B2
        competency_ids = {comp["id"] for comp in b2_data.get("competencies", [])}

        # Extract sources from B3 KSA items
        b3_sources = set()
        for knowledge in b3_data.get("knowledge_items", []):
            b3_sources.add(knowledge.get("source", ""))
        for skill in b3_data.get("skill_items", []):
            b3_sources.add(skill.get("source", ""))
        for habit in b3_data.get("habit_items", []):
            b3_sources.add(habit.get("source", ""))

        # Check if competency IDs are used in sources
        for comp_id in competency_ids:
            if any(comp_id in source for source in b3_sources):
                checks.append(
                    ValidationCheck(
                        check_id=f"B2_B3_comp_ref_{comp_id}",
                        check_name="Competency Reference",
                        category="reference",
                        step="B2→B3",
                        passed=True,
                        severity=ValidationSeverity.INFO,
                        message=f"Competency {comp_id} is referenced in B3",
                    )
                )
            else:
                checks.append(
                    ValidationCheck(
                        check_id=f"B2_B3_comp_ref_{comp_id}",
                        check_name="Competency Reference",
                        category="reference",
                        step="B2→B3",
                        passed=False,
                        severity=ValidationSeverity.WARNING,
                        message=f"Competency {comp_id} from B2 is not used in B3 KSA matrix",
                        recommendation="Ensure all competencies are mapped to KSA items",
                    )
                )

        return checks

    def validate_b3_internal(self, b3_data: dict[str, Any]) -> list[ValidationCheck]:
        """
        Validate B3 internal references.

        Checks:
        - Knowledge items reference valid skills/habits in required_for
        - Skill items reference valid knowledge in requires_knowledge
        - Skill items reference valid habits in required_for
        - Habit items reference valid skills in requires_skills
        - Dependency graph contains only valid IDs
        """
        checks = []

        # Collect all IDs
        knowledge_ids = {k["id"] for k in b3_data.get("knowledge_items", [])}
        skill_ids = {s["id"] for s in b3_data.get("skill_items", [])}
        habit_ids = {h["id"] for h in b3_data.get("habit_items", [])}
        all_ids = knowledge_ids | skill_ids | habit_ids

        # Check knowledge items
        for knowledge in b3_data.get("knowledge_items", []):
            k_id = knowledge["id"]
            for required_id in knowledge.get("required_for", []):
                if required_id in skill_ids or required_id in habit_ids:
                    checks.append(
                        ValidationCheck(
                            check_id=f"B3_knowledge_ref_{k_id}_{required_id}",
                            check_name="Knowledge Required For",
                            category="reference",
                            step="B3",
                            passed=True,
                            severity=ValidationSeverity.INFO,
                            message=f"Knowledge {k_id} → {required_id} reference valid",
                        )
                    )
                else:
                    checks.append(
                        ValidationCheck(
                            check_id=f"B3_knowledge_ref_{k_id}_{required_id}",
                            check_name="Knowledge Required For",
                            category="reference",
                            step="B3",
                            passed=False,
                            severity=ValidationSeverity.CRITICAL,
                            message=f"Knowledge {k_id} references unknown ID {required_id}",
                            expected=f"Valid skill or habit ID",
                            actual=required_id,
                            recommendation=f"Add skill/habit {required_id} or fix reference",
                        )
                    )

        # Check skill items
        for skill in b3_data.get("skill_items", []):
            s_id = skill["id"]

            # Check requires_knowledge
            for req_k_id in skill.get("requires_knowledge", []):
                if req_k_id in knowledge_ids:
                    checks.append(
                        ValidationCheck(
                            check_id=f"B3_skill_req_k_{s_id}_{req_k_id}",
                            check_name="Skill Requires Knowledge",
                            category="reference",
                            step="B3",
                            passed=True,
                            severity=ValidationSeverity.INFO,
                            message=f"Skill {s_id} ← {req_k_id} reference valid",
                        )
                    )
                else:
                    checks.append(
                        ValidationCheck(
                            check_id=f"B3_skill_req_k_{s_id}_{req_k_id}",
                            check_name="Skill Requires Knowledge",
                            category="reference",
                            step="B3",
                            passed=False,
                            severity=ValidationSeverity.CRITICAL,
                            message=f"Skill {s_id} references unknown knowledge {req_k_id}",
                            expected="Valid knowledge ID",
                            actual=req_k_id,
                            recommendation=f"Add knowledge {req_k_id} or fix reference",
                        )
                    )

            # Check required_for
            for req_h_id in skill.get("required_for", []):
                if req_h_id in habit_ids:
                    checks.append(
                        ValidationCheck(
                            check_id=f"B3_skill_req_for_{s_id}_{req_h_id}",
                            check_name="Skill Required For",
                            category="reference",
                            step="B3",
                            passed=True,
                            severity=ValidationSeverity.INFO,
                            message=f"Skill {s_id} → {req_h_id} reference valid",
                        )
                    )
                else:
                    checks.append(
                        ValidationCheck(
                            check_id=f"B3_skill_req_for_{s_id}_{req_h_id}",
                            check_name="Skill Required For",
                            category="reference",
                            step="B3",
                            passed=False,
                            severity=ValidationSeverity.CRITICAL,
                            message=f"Skill {s_id} references unknown habit {req_h_id}",
                            expected="Valid habit ID",
                            actual=req_h_id,
                            recommendation=f"Add habit {req_h_id} or fix reference",
                        )
                    )

        # Check habit items
        for habit in b3_data.get("habit_items", []):
            h_id = habit["id"]
            for req_s_id in habit.get("requires_skills", []):
                if req_s_id in skill_ids:
                    checks.append(
                        ValidationCheck(
                            check_id=f"B3_habit_req_s_{h_id}_{req_s_id}",
                            check_name="Habit Requires Skills",
                            category="reference",
                            step="B3",
                            passed=True,
                            severity=ValidationSeverity.INFO,
                            message=f"Habit {h_id} ← {req_s_id} reference valid",
                        )
                    )
                else:
                    checks.append(
                        ValidationCheck(
                            check_id=f"B3_habit_req_s_{h_id}_{req_s_id}",
                            check_name="Habit Requires Skills",
                            category="reference",
                            step="B3",
                            passed=False,
                            severity=ValidationSeverity.CRITICAL,
                            message=f"Habit {h_id} references unknown skill {req_s_id}",
                            expected="Valid skill ID",
                            actual=req_s_id,
                            recommendation=f"Add skill {req_s_id} or fix reference",
                        )
                    )

        # Check dependency graph
        for edge in b3_data.get("dependency_graph", []):
            from_id = edge.get("from_id")
            to_id = edge.get("to_id")

            if from_id in all_ids and to_id in all_ids:
                checks.append(
                    ValidationCheck(
                        check_id=f"B3_dep_graph_{from_id}_{to_id}",
                        check_name="Dependency Graph",
                        category="reference",
                        step="B3",
                        passed=True,
                        severity=ValidationSeverity.INFO,
                        message=f"Dependency {from_id} → {to_id} valid",
                    )
                )
            else:
                invalid_ids = []
                if from_id not in all_ids:
                    invalid_ids.append(from_id)
                if to_id not in all_ids:
                    invalid_ids.append(to_id)

                checks.append(
                    ValidationCheck(
                        check_id=f"B3_dep_graph_{from_id}_{to_id}",
                        check_name="Dependency Graph",
                        category="reference",
                        step="B3",
                        passed=False,
                        severity=ValidationSeverity.CRITICAL,
                        message=f"Dependency references unknown IDs: {invalid_ids}",
                        expected="Valid KSA IDs",
                        actual={"from": from_id, "to": to_id},
                        recommendation="Fix dependency graph IDs",
                    )
                )

        return checks

    def validate_b4_to_b5(
        self, b4_data: dict[str, Any], b5_data: dict[str, Any]
    ) -> list[ValidationCheck]:
        """
        Validate B4 → B5 references.

        Checks:
        - unit_sequence in B5 contains only units from B4
        - No duplicate IDs in unit_sequence
        - All units from B4 clusters are present in sequence
        """
        checks = []

        # Collect all unit IDs from B4
        all_unit_ids = set()
        for theory in b4_data.get("theory_units", []):
            all_unit_ids.add(theory["id"])
        for practice in b4_data.get("practice_units", []):
            all_unit_ids.add(practice["id"])
        for automation in b4_data.get("automation_units", []):
            all_unit_ids.add(automation["id"])

        # Check unit_sequence
        unit_sequence = b5_data.get("unit_sequence", [])
        sequence_set = set(unit_sequence)

        # Check for duplicates
        if len(unit_sequence) != len(sequence_set):
            duplicates = [uid for uid in unit_sequence if unit_sequence.count(uid) > 1]
            checks.append(
                ValidationCheck(
                    check_id="B4_B5_duplicate_units",
                    check_name="Unit Sequence Duplicates",
                    category="reference",
                    step="B4→B5",
                    passed=False,
                    severity=ValidationSeverity.CRITICAL,
                    message=f"Duplicate unit IDs in sequence: {set(duplicates)}",
                    recommendation="Remove duplicate IDs from unit_sequence",
                )
            )

        # Check if all sequence IDs exist in B4
        for unit_id in unit_sequence:
            if unit_id in all_unit_ids:
                checks.append(
                    ValidationCheck(
                        check_id=f"B4_B5_unit_{unit_id}",
                        check_name="Unit Sequence Reference",
                        category="reference",
                        step="B4→B5",
                        passed=True,
                        severity=ValidationSeverity.INFO,
                        message=f"Unit {unit_id} exists in B4",
                    )
                )
            else:
                checks.append(
                    ValidationCheck(
                        check_id=f"B4_B5_unit_{unit_id}",
                        check_name="Unit Sequence Reference",
                        category="reference",
                        step="B4→B5",
                        passed=False,
                        severity=ValidationSeverity.CRITICAL,
                        message=f"Unit {unit_id} in sequence not found in B4",
                        expected="Valid unit ID from B4",
                        actual=unit_id,
                        recommendation=f"Remove {unit_id} from sequence or add to B4",
                    )
                )

        # Check if all B4 units are in sequence
        missing_units = all_unit_ids - sequence_set
        if missing_units:
            checks.append(
                ValidationCheck(
                    check_id="B4_B5_missing_units",
                    check_name="Complete Unit Coverage",
                    category="reference",
                    step="B4→B5",
                    passed=False,
                    severity=ValidationSeverity.WARNING,
                    message=f"Units from B4 not in sequence: {missing_units}",
                    recommendation="Add missing units to unit_sequence",
                )
            )
        else:
            checks.append(
                ValidationCheck(
                    check_id="B4_B5_complete_coverage",
                    check_name="Complete Unit Coverage",
                    category="reference",
                    step="B4→B5",
                    passed=True,
                    severity=ValidationSeverity.INFO,
                    message="All B4 units are present in B5 sequence",
                )
            )

        return checks

    def validate_all(self, steps_data: dict[str, dict[str, Any]]) -> list[ValidationCheck]:
        """
        Validate all reference integrity checks.

        Args:
            steps_data: Dictionary mapping step names to their output data

        Returns:
            List of all validation checks
        """
        all_checks = []

        # B2 → B3
        if "B2_competencies" in steps_data and "B3_ksa_matrix" in steps_data:
            checks = self.validate_b2_to_b3(
                steps_data["B2_competencies"], steps_data["B3_ksa_matrix"]
            )
            all_checks.extend(checks)

        # B3 internal
        if "B3_ksa_matrix" in steps_data:
            checks = self.validate_b3_internal(steps_data["B3_ksa_matrix"])
            all_checks.extend(checks)

        # B4 → B5
        if "B4_learning_units" in steps_data and "B5_hierarchy" in steps_data:
            checks = self.validate_b4_to_b5(
                steps_data["B4_learning_units"], steps_data["B5_hierarchy"]
            )
            all_checks.extend(checks)

        return all_checks
