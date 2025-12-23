from abc import ABC, abstractmethod
from typing import List, Dict, Any

try:
    from ..views.widgets.standalone_search_bar import FilterDefinition
    from ...utils.date_utils import filter_by_date_simple
except ImportError:
    from src.views.widgets.standalone_search_bar import FilterDefinition
    from utils.date_utils import filter_by_date_simple


class FilterStrategy(ABC):
    """Abstract base class for table-specific filter strategies."""

    def __init__(self):
        self._status_items = [{"value": "All"}]
        self._task_type_items = [{"value": "All"}]

    @abstractmethod
    def get_filter_definitions(self) -> List[FilterDefinition]:
        """Return filter definitions for this table type."""
        pass

    @abstractmethod
    def apply_filters(self, data: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Apply filters to data and return filtered results."""
        pass

    @abstractmethod
    def get_searchable_fields(self) -> List[str]:
        """Return list of fields that can be searched."""
        pass

    def set_status_items(self, status_items: List[Dict[str, str]]):
        """Update status filter items dynamically."""
        self._status_items = status_items

    def set_task_type_items(self, task_type_items: List[Dict[str, str]]):
        """Update task type filter items dynamically."""
        self._task_type_items = task_type_items


class ReviewTableFilterStrategy(FilterStrategy):
    """Filter strategy for Review table."""

    def get_filter_definitions(self) -> List[FilterDefinition]:

        return [
            FilterDefinition(
                name="search",
                title="Search",
                filter_type="text",
                placeholder="Search across all fields..."
            ),
            FilterDefinition(
                name="submission_type",
                title="Submission Type",
                filter_type="list",
                items=[
                    {"value": "All"},
                    {"value": "WIP", "color": "#FFA500"},
                    {"value": "FINAL", "color": "#00FF00"},
                    {"value": "PACKAGE", "color": "#0000FF"},
                ]
            ),
            FilterDefinition(
                name="review_status",
                title="Review Status",
                filter_type="list",
                items=[
                    {"value": "All"},
                    {"value": "Approved", "color": "#00FF00"},
                    {"value": "Done", "color": "#008000"},
                    {"value": "Forward", "color": "#0000FF"},
                    {"value": "Retake", "color": "#FF0000"},
                    {"value": "Reviewed", "color": "#00CED1"},
                    {"value": "Submit", "color": "#FFD700"},
                ]
            ),
            FilterDefinition(
                name="date",
                title="Date",
                filter_type="list",
                items=[
                    {"value": "All"},
                    {"value": "Today"},
                    {"value": "Yesterday"},
                    {"value": "Last 7 days"},
                ]
            ),
            FilterDefinition(
                name="reviewer",
                title="Reviewer",
                filter_type="text",
                placeholder="Select or type reviewer name..."
            ),
            FilterDefinition(
                name="task_type",
                title="Task Type",
                filter_type="list",
                items=self._task_type_items
            ),
        ]

    def get_searchable_fields(self) -> List[str]:
        return [
            'sequence_name', 'shot_name', 'task_name', 'product',
            'current_version', 'version_status', 'author', 'submitted_at', 'reviewer_name'
        ]

    def apply_filters(self, data: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        if not data:
            return data

        # Apply date filter first
        date_filter = filters.get('date')
        if date_filter and date_filter not in ['All', 'ALL']:
            data = filter_by_date_simple(data, date_filter)

        # Apply other filters
        filtered_data = []
        for item in data:
            if self._matches_filters(item, filters):
                filtered_data.append(item)

        return filtered_data

    def _matches_filters(self, item: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        # Search filter
        search_text = filters.get('search', '').lower()
        if search_text:
            searchable_fields = [str(item.get(field, '')) for field in self.get_searchable_fields()]
            if not any(search_text in field.lower() for field in searchable_fields):
                return False

        # Submission Type filter
        submission_type_filter = filters.get('submission_type')
        if submission_type_filter:
            if not isinstance(submission_type_filter, list):
                submission_type_filter = [submission_type_filter]
            if 'All' not in submission_type_filter:
                item_submission_type = item.get('submission_type', '')
                if item_submission_type not in submission_type_filter:
                    return False

        # Review Status filter
        review_status_filter = filters.get('review_status')
        if review_status_filter:
            if not isinstance(review_status_filter, list):
                review_status_filter = [review_status_filter]
            if 'All' not in review_status_filter:
                item_review_status = item.get('review_status', '')
                if item_review_status not in review_status_filter:
                    return False

        # Status filter - Multi-selection support
        status_filter = filters.get('status')
        if status_filter:
            if not isinstance(status_filter, list):
                status_filter = [status_filter]
            if 'All' not in status_filter:
                item_status = item.get('version_status', '')
                if item_status not in status_filter:
                    return False

        # Reviewer filter
        reviewer_filter = filters.get('reviewer')
        if reviewer_filter and reviewer_filter != 'All':
            if reviewer_filter != item.get('reviewer_name', ''):
                return False

        # Task type filter - Multi-selection support
        task_type_filter = filters.get('task_type')
        if task_type_filter:
            if not isinstance(task_type_filter, list):
                task_type_filter = [task_type_filter]
            if 'All' not in task_type_filter:
                item_task_type = item.get('task_type', '')
                if item_task_type not in task_type_filter:
                    return False

        return True


class ListTableFilterStrategy(FilterStrategy):
    """Filter strategy for List table."""

    def get_filter_definitions(self) -> List[FilterDefinition]:

        return [
            FilterDefinition(
                name="search",
                title="Search",
                filter_type="text",
                placeholder="Search across all fields..."
            ),
            FilterDefinition(
                name="status",
                title="Status",
                filter_type="list",
                items=self._status_items
            ),
            FilterDefinition(
                name="author",
                title="Author",
                filter_type="text",
                placeholder="Select or type author name..."
            ),
            FilterDefinition(
                name="date",
                title="Created Date",
                filter_type="text",
                placeholder="Select date range...",
                items=[
                    {"value": "ALL"},
                    {"value": "Today"},
                    {"value": "Yesterday"},
                    {"value": "Last 7 days"},
                ]
            ),
            FilterDefinition(
                name="task_type",
                title="Task Type",
                filter_type="list",
                items=self._task_type_items
            ),
        ]

    def get_searchable_fields(self) -> List[str]:
        return [
            'sequence_name', 'shot_name', 'task_name', 'product',
            'current_version', 'version_status', 'author', 'created_at'
        ]

    def apply_filters(self, data: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        if not data:
            return data

        # Apply date filter first
        date_filter = filters.get('date')
        if date_filter and date_filter != 'ALL':
            data = filter_by_date_simple(data, date_filter)

        # Apply other filters
        filtered_data = []
        for item in data:
            if self._matches_filters(item, filters):
                filtered_data.append(item)

        return filtered_data

    def _matches_filters(self, item: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        # Search filter
        search_text = filters.get('search', '').lower()
        if search_text:
            searchable_fields = [str(item.get(field, '')) for field in self.get_searchable_fields()]
            if not any(search_text in field.lower() for field in searchable_fields):
                return False

        # Status filter - Multi-selection support
        status_filter = filters.get('status')
        if status_filter:
            # Ensure it's a list
            if not isinstance(status_filter, list):
                status_filter = [status_filter]

            # Skip filter if 'All' is selected
            if 'All' not in status_filter:
                item_status = item.get('version_status', '')
                if item_status not in status_filter:
                    return False

        # Author filter
        author_filter = filters.get('author')
        if author_filter and author_filter != 'All':
            if author_filter != item.get('author', ''):
                return False

        # Task type filter - Multi-selection support
        task_type_filter = filters.get('task_type')
        if task_type_filter:
            if not isinstance(task_type_filter, list):
                task_type_filter = [task_type_filter]

            if 'All' not in task_type_filter:
                item_task_type = item.get('task_type', '')
                if item_task_type not in task_type_filter:
                    return False

        return True