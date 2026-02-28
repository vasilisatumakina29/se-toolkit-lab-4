"""Unit tests for interaction validation and edge cases."""

import pytest
from pydantic import ValidationError

from app.models.interaction import InteractionLog, InteractionLogCreate, InteractionModel


class TestInteractionLogCreateValidation:
    """Test boundary values for InteractionLogCreate schema validation."""

    def test_create_with_empty_kind_is_accepted(self) -> None:
        """Empty kind is accepted by Pydantic (no min_length constraint)."""
        log = InteractionLogCreate(learner_id=1, item_id=1, kind="")
        assert log.kind == ""

    def test_create_with_whitespace_only_kind_is_accepted(self) -> None:
        """Kind with only whitespace is accepted (no strip constraint)."""
        log = InteractionLogCreate(learner_id=1, item_id=1, kind="   ")
        assert log.kind == "   "

    def test_create_with_valid_kind_succeeds(self) -> None:
        """Valid interaction kinds should pass validation."""
        valid_kinds = ["attempt", "view", "complete", "submit", "hint_request"]
        for kind in valid_kinds:
            log = InteractionLogCreate(learner_id=1, item_id=1, kind=kind)
            assert log.kind == kind

    def test_create_with_very_long_kind_succeeds(self) -> None:
        """Very long kind values should be accepted (no artificial limit)."""
        long_kind = "custom_interaction_type_" + "A" * 100
        log = InteractionLogCreate(learner_id=1, item_id=1, kind=long_kind)
        assert len(log.kind) == 124

    def test_create_with_negative_learner_id_succeeds_at_schema_level(self) -> None:
        """Negative learner_id passes schema validation (DB FK may reject)."""
        log = InteractionLogCreate(learner_id=-1, item_id=1, kind="attempt")
        assert log.learner_id == -1

    def test_create_with_negative_item_id_succeeds_at_schema_level(self) -> None:
        """Negative item_id passes schema validation (DB FK may reject)."""
        log = InteractionLogCreate(learner_id=1, item_id=-999, kind="attempt")
        assert log.item_id == -999

    def test_create_with_zero_learner_id_succeeds_at_schema_level(self) -> None:
        """Zero learner_id passes schema validation (0 is falsy but valid)."""
        log = InteractionLogCreate(learner_id=0, item_id=1, kind="attempt")
        assert log.learner_id == 0

    def test_create_with_zero_item_id_succeeds_at_schema_level(self) -> None:
        """Zero item_id passes schema validation (0 is falsy but valid)."""
        log = InteractionLogCreate(learner_id=1, item_id=0, kind="attempt")
        assert log.item_id == 0

    def test_create_with_very_large_ids_succeeds(self) -> None:
        """Very large IDs should be accepted."""
        large_id = 2**31 - 1  # Max 32-bit signed int
        log = InteractionLogCreate(learner_id=large_id, item_id=large_id, kind="attempt")
        assert log.learner_id == large_id
        assert log.item_id == large_id


class TestInteractionModel:
    """Test InteractionModel response schema."""

    def test_model_with_null_created_at_raises_validation_error(self) -> None:
        """InteractionModel requires created_at (not optional)."""
        with pytest.raises(ValidationError):
            InteractionModel(
                id=1, learner_id=1, item_id=1, kind="attempt", created_at=None
            )

    def test_model_with_valid_datetime_succeeds(self) -> None:
        """InteractionModel accepts valid datetime."""
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)
        model = InteractionModel(
            id=1, learner_id=1, item_id=1, kind="attempt", created_at=now
        )
        assert model.created_at == now


class TestInteractionLog:
    """Test InteractionLog database model."""

    def test_log_with_null_created_at(self) -> None:
        """InteractionLog allows null created_at (optional field)."""
        log = InteractionLog(id=1, learner_id=1, item_id=1, kind="attempt")
        assert log.created_at is None

    def test_log_with_id_zero(self) -> None:
        """InteractionLog with id=0 should be valid."""
        log = InteractionLog(id=0, learner_id=1, item_id=1, kind="attempt")
        assert log.id == 0
