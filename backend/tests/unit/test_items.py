"""Unit tests for item validation and edge cases."""

import pytest
from pydantic import ValidationError

from app.models.item import ItemCreate, ItemRecord, ItemUpdate


class TestItemCreateValidation:
    """Test boundary values for ItemCreate schema validation."""

    def test_create_with_empty_title_is_accepted(self) -> None:
        """Empty title is accepted by Pydantic (no min_length constraint)."""
        item = ItemCreate(title="")
        assert item.title == ""

    def test_create_with_whitespace_only_title_is_accepted(self) -> None:
        """Title with only whitespace is accepted (no strip constraint)."""
        item = ItemCreate(title="   ")
        assert item.title == "   "

    def test_create_with_very_long_title_succeeds(self) -> None:
        """Very long titles should be accepted (no artificial limit)."""
        long_title = "A" * 10000
        item = ItemCreate(title=long_title)
        assert len(item.title) == 10000

    def test_create_with_special_characters_in_title_succeeds(self) -> None:
        """Titles with special characters should be accepted."""
        special_title = "Test <script>alert('xss')</script> & <tags> \"quotes\""
        item = ItemCreate(title=special_title)
        assert item.title == special_title

    def test_create_with_self_referencing_parent_id(self) -> None:
        """Item with parent_id pointing to itself should be creatable at schema level."""
        # Note: Database FK constraint may reject this, but schema validation passes
        item = ItemCreate(title="Self-referencing", parent_id=1)
        assert item.parent_id == 1


class TestItemUpdateValidation:
    """Test boundary values for ItemUpdate schema validation."""

    def test_update_with_empty_title_is_accepted(self) -> None:
        """Empty title is accepted on update (no min_length constraint)."""
        item = ItemUpdate(title="", description="Desc")
        assert item.title == ""

    def test_update_with_empty_description_succeeds(self) -> None:
        """Empty description should be allowed on update."""
        item = ItemUpdate(title="Valid Title", description="")
        assert item.description == ""

    def test_update_with_very_long_description_succeeds(self) -> None:
        """Very long descriptions should be accepted."""
        long_desc = "B" * 50000
        item = ItemUpdate(title="Title", description=long_desc)
        assert len(item.description) == 50000


class TestItemRecordDefaults:
    """Test default values and boundary cases for ItemRecord."""

    def test_record_with_default_type_is_step(self) -> None:
        """Default item type should be 'step'."""
        record = ItemRecord(title="Test")
        assert record.type == "step"

    def test_record_with_default_description_is_empty_string(self) -> None:
        """Default description should be empty string."""
        record = ItemRecord(title="Test")
        assert record.description == ""

    def test_record_with_default_attributes_is_empty_dict(self) -> None:
        """Default attributes should be empty dictionary."""
        record = ItemRecord(title="Test")
        assert record.attributes == {}

    def test_record_with_null_parent_id(self) -> None:
        """Root-level items should have null parent_id."""
        record = ItemRecord(title="Root Item")
        assert record.parent_id is None

    def test_record_tree_hierarchy_course_to_step(self) -> None:
        """Test representing course → lab → task → step hierarchy."""
        course = ItemRecord(type="course", title="Course")
        lab = ItemRecord(type="lab", title="Lab", parent_id=1)
        task = ItemRecord(type="task", title="Task", parent_id=2)
        step = ItemRecord(type="step", title="Step", parent_id=3)

        assert course.type == "course"
        assert lab.parent_id == 1
        assert task.parent_id == 2
        assert step.parent_id == 3
