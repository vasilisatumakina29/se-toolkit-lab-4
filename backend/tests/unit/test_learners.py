"""Unit tests for learner validation and edge cases."""

import pytest
from pydantic import ValidationError

from app.models.learner import Learner, LearnerCreate


class TestLearnerCreateValidation:
    """Test boundary values for LearnerCreate schema validation."""

    def test_create_with_empty_name_is_accepted(self) -> None:
        """Empty name is accepted by Pydantic (no min_length constraint)."""
        learner = LearnerCreate(name="", email="test@example.com")
        assert learner.name == ""

    def test_create_with_whitespace_only_name_is_accepted(self) -> None:
        """Name with only whitespace is accepted (no strip constraint)."""
        learner = LearnerCreate(name="   ", email="test@example.com")
        assert learner.name == "   "

    def test_create_with_empty_email_is_accepted(self) -> None:
        """Empty email is accepted by Pydantic (no format validation by default)."""
        learner = LearnerCreate(name="Test User", email="")
        assert learner.email == ""

    def test_create_with_invalid_email_format_is_accepted(self) -> None:
        """Invalid email formats are accepted (no built-in email validation)."""
        invalid_emails = [
            "invalid",
            "missing@",
            "@missing.domain",
            "no-at-sign.com",
            "spaces in@email.com",
        ]
        for invalid_email in invalid_emails:
            learner = LearnerCreate(name="Test User", email=invalid_email)
            assert learner.email == invalid_email

    def test_create_with_valid_email_succeeds(self) -> None:
        """Valid email formats should pass validation."""
        valid_emails = [
            "user@example.com",
            "user.name+tag@domain.co.uk",
            "user_name@sub.domain.org",
            "test123@test-domain.com",
        ]
        for valid_email in valid_emails:
            learner = LearnerCreate(name="Test User", email=valid_email)
            assert learner.email == valid_email

    def test_create_with_very_long_name_succeeds(self) -> None:
        """Very long names should be accepted (no artificial limit)."""
        long_name = "A" * 500
        learner = LearnerCreate(name=long_name, email="test@example.com")
        assert len(learner.name) == 500

    def test_create_with_unicode_name_succeeds(self) -> None:
        """Names with unicode characters should be accepted."""
        unicode_names = [
            "Василиса",
            "田中太郎",
            "Müller",
            "Ελληνικά",
            "العربية",
        ]
        for name in unicode_names:
            learner = LearnerCreate(name=name, email="test@example.com")
            assert learner.name == name

    def test_create_with_duplicate_email_allowed_at_schema_level(self) -> None:
        """Schema validation allows duplicate emails (DB constraint may reject)."""
        learner1 = LearnerCreate(name="User One", email="duplicate@example.com")
        learner2 = LearnerCreate(name="User Two", email="duplicate@example.com")
        assert learner1.email == learner2.email


class TestLearnerModel:
    """Test Learner model with database fields."""

    def test_learner_with_null_enrolled_at(self) -> None:
        """Learner can have null enrolled_at (optional field)."""
        learner = Learner(id=1, name="Test", email="test@example.com")
        assert learner.enrolled_at is None

    def test_learner_with_id_zero(self) -> None:
        """Learner with id=0 should be valid (0 is falsy but valid)."""
        learner = Learner(id=0, name="Test", email="test@example.com")
        assert learner.id == 0

    def test_learner_with_negative_id(self) -> None:
        """Negative IDs should be accepted at schema level."""
        learner = Learner(id=-1, name="Test", email="test@example.com")
        assert learner.id == -1
