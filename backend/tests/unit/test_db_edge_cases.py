"""Unit tests for filter edge cases not covered in existing tests."""

from app.routers.interactions import _filter_by_item_id


class TestFilterByItemIdEdgeCases:
    """Additional edge cases for _filter_by_item_id not covered in test_interactions.py."""

    def test_filter_with_single_item_list_matching(self) -> None:
        """Filter should return the single item when it matches."""
        from app.models.interaction import InteractionLog

        interactions = [
            InteractionLog(id=1, learner_id=1, item_id=5, kind="attempt")
        ]
        result = _filter_by_item_id(interactions, 5)
        assert len(result) == 1
        assert result[0].item_id == 5

    def test_filter_with_single_item_list_not_matching(self) -> None:
        """Filter should return empty list when single item doesn't match."""
        from app.models.interaction import InteractionLog

        interactions = [
            InteractionLog(id=1, learner_id=1, item_id=5, kind="attempt")
        ]
        result = _filter_by_item_id(interactions, 999)
        assert len(result) == 0

    def test_filter_with_multiple_matches(self) -> None:
        """Filter should return all items matching the item_id."""
        from app.models.interaction import InteractionLog

        interactions = [
            InteractionLog(id=1, learner_id=1, item_id=3, kind="view"),
            InteractionLog(id=2, learner_id=2, item_id=3, kind="attempt"),
            InteractionLog(id=3, learner_id=1, item_id=4, kind="view"),
            InteractionLog(id=4, learner_id=3, item_id=3, kind="complete"),
        ]
        result = _filter_by_item_id(interactions, 3)
        assert len(result) == 3
        assert all(i.item_id == 3 for i in result)

    def test_filter_with_negative_item_id(self) -> None:
        """Filter with negative item_id should return empty (no matches expected)."""
        from app.models.interaction import InteractionLog

        interactions = [
            InteractionLog(id=1, learner_id=1, item_id=1, kind="attempt"),
        ]
        result = _filter_by_item_id(interactions, -1)
        assert len(result) == 0

    def test_filter_preserves_original_list(self) -> None:
        """Filter should not modify the original list."""
        from app.models.interaction import InteractionLog

        interactions = [
            InteractionLog(id=1, learner_id=1, item_id=1, kind="attempt"),
        ]
        original_length = len(interactions)
        _filter_by_item_id(interactions, 1)
        assert len(interactions) == original_length
