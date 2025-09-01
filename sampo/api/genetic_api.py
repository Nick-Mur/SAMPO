"""Interfaces for genetic scheduling API.

Интерфейсы для генетического API планирования.
"""

from abc import ABC, abstractmethod
from enum import Enum
from functools import partial
from typing import Callable

import numpy as np
from deap import base, creator

from sampo.schemas import Schedule
from sampo.schemas.schedule_spec import ScheduleSpec

ChromosomeType = tuple[np.ndarray, np.ndarray, np.ndarray, ScheduleSpec, np.ndarray]

class ScheduleGenerationScheme(Enum):
    """Available schedule generation schemes.

    Доступные схемы генерации расписаний.
    """

    Parallel = 'Parallel'
    Serial = 'Serial'


class FitnessFunction(ABC):
    """Base class for fitness functions.

    Базовый класс для функций приспособленности.
    """

    @abstractmethod
    def evaluate(
        self, chromosome: ChromosomeType, evaluator: Callable[[ChromosomeType], Schedule]
    ) -> tuple[int | float]:
        """Calculate fitness of a chromosome; lower is better.

        Вычисляет приспособленность хромосомы; меньше — лучше.
        """
        ...


# create class FitnessMin, the weights = -1 means that fitness - is function for minimum

# creator.create('FitnessMin', base.Fitness, weights=(-1.0,))
# creator.create('Individual', list, fitness=creator.FitnessMin)
# Individual = creator.Individual

class Individual(list):
    """Wrapper for chromosome with attached fitness.

    Обёртка над хромосомой с прикреплённой приспособленностью.
    """

    def __init__(self, individual_fitness_constructor: Callable[[], base.Fitness], chromosome: ChromosomeType) -> None:
        super().__init__(chromosome)
        self.fitness = individual_fitness_constructor()

    @staticmethod
    def prepare(individual_fitness_constructor: Callable[[], base.Fitness]) -> Callable[[ChromosomeType], list]:
        """Return constructor adapted for DEAP.

        Возвращает конструктор, адаптированный для DEAP.
        """
        return partial(Individual, individual_fitness_constructor)

