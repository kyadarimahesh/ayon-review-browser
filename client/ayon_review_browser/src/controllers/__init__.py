"""
Modular filter system controllers.

This package provides a modular architecture for table filtering with:
- Strategy pattern for table-specific filter logic
- Centralized filter management
- Dynamic filter definitions based on active table
"""

from .filter_strategy import FilterStrategy, ReviewTableFilterStrategy, ListTableFilterStrategy
from .filter_manager import FilterManager
from .table_filter_controller import BaseTableFilterController, ReviewTableFilterController, ListTableFilterController
from .advanced_filter_controller import AdvancedFilterController

__all__ = [
    'FilterStrategy',
    'ReviewTableFilterStrategy', 
    'ListTableFilterStrategy',
    'FilterManager',
    'BaseTableFilterController',
    'ReviewTableFilterController',
    'ListTableFilterController', 
    'AdvancedFilterController'
]