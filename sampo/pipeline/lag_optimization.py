"""Strategies for lag optimization in scheduling pipeline.

Стратегии оптимизации лагов в конвейере планирования.
"""

from enum import Enum


class LagOptimizationStrategy(Enum):
    """Possible approaches to lag optimization.

    Возможные подходы к оптимизации лагов.
    """

    TRUE = True
    FALSE = False
    AUTO = None
    NONE = None
