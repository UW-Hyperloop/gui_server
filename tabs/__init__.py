"""
Tabs package for TBM GUI
Contains different tab views for the main interface.
"""

from .main_tab import MainTab
from .engine_tab import EngineTab
from .pump_tab import PumpTab
from .navigation_tab import NavigationTab

__all__ = ['MainTab', 'EngineTab', 'PumpTab', 'NavigationTab'] 