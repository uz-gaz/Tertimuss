"""
==========================================
Task generation algorithms for periodic tasks with implicit deadlines
==========================================

This package contains a set of task generation algorithms for periodic tasks with implicit deadlines

This module exposes the following classes:
- :class:`.PTGUUniFastDiscard`
- :class:`.PTGUUniFast`
"""

from ._uunifast_discard import PTGUUniFastDiscard
from ._uunifast import PTGUUniFast
