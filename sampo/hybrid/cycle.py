"""Cyclic hybrid scheduler combining multiple strategies.

Циклический гибридный планировщик, объединяющий несколько стратегий.
"""

import numpy as np

from sampo.api.genetic_api import FitnessFunction, ChromosomeType, ScheduleGenerationScheme
from sampo.base import SAMPO
from sampo.hybrid.population import PopulationScheduler
from sampo.scheduler.genetic import TimeFitness
from sampo.scheduler.genetic.schedule_builder import create_toolbox
from sampo.schemas import WorkGraph, Contractor, Time, LandscapeConfiguration, Schedule
from sampo.schemas.schedule_spec import ScheduleSpec


class CycleHybridScheduler:
    """Scheduler that iteratively applies a set of algorithms.

    Планировщик, который итеративно применяет набор алгоритмов.
    """

    def __init__(
        self,
        starting_scheduler: PopulationScheduler,
        cycle_schedulers: list[PopulationScheduler],
        fitness: FitnessFunction = TimeFitness(),
        max_plateau_size: int = 2,
    ) -> None:
        """Initialize hybrid scheduler.

        Инициализирует гибридный планировщик.

        Args:
            starting_scheduler: Scheduler to generate initial population.
                Планировщик для генерации начальной популяции.
            cycle_schedulers: Schedulers applied sequentially each cycle.
                Планировщики, применяемые последовательно в каждом цикле.
            fitness: Fitness function used for evaluation.
                Функция приспособленности для оценки.
            max_plateau_size: Number of cycles without improvement before stop.
                Количество циклов без улучшения перед остановкой.
        """
        self._starting_scheduler = starting_scheduler
        self._cycle_schedulers = cycle_schedulers
        self._fitness = fitness
        self._max_plateau_size = max_plateau_size

    def _get_population_fitness(self, pop: list[ChromosomeType]):
        # return best chromosome's fitness
        return min(SAMPO.backend.compute_chromosomes(self._fitness, pop))

    def _get_best_individual(self, pop: list[ChromosomeType]) -> ChromosomeType:
        fitness = SAMPO.backend.compute_chromosomes(self._fitness, pop)
        return pop[np.argmin(fitness)]

    def run(
        self,
        wg: WorkGraph,
        contractors: list[Contractor],
        spec: ScheduleSpec = ScheduleSpec(),
        assigned_parent_time: Time = Time(0),
        landscape: LandscapeConfiguration = LandscapeConfiguration(),
    ) -> ChromosomeType:
        """Execute cyclic scheduling returning best chromosome.

        Выполняет циклическое планирование, возвращая лучшую хромосому.

        Args:
            wg: Work graph to schedule.
                Граф работ для планирования.
            contractors: Available contractors.
                Доступные подрядчики.
            spec: Schedule specification.
                Спецификация расписания.
            assigned_parent_time: Start time of parent context.
                Время начала родительского контекста.
            landscape: Landscape configuration.
                Конфигурация местности.

        Returns:
            ChromosomeType: Best found chromosome.
            ChromosomeType: Лучшая найденная хромосома.
        """
        pop = self._starting_scheduler.schedule([], wg, contractors, spec, assigned_parent_time, landscape)

        cur_fitness = Time.inf().value
        plateau_steps = 0

        while True:
            pop_fitness = self._get_population_fitness(pop)
            if pop_fitness == cur_fitness:
                plateau_steps += 1
                if plateau_steps == self._max_plateau_size:
                    break
            else:
                plateau_steps = 0
                cur_fitness = pop_fitness

            for scheduler in self._cycle_schedulers:
                pop = scheduler.schedule(pop, wg, contractors, spec, assigned_parent_time, landscape)

        return self._get_best_individual(pop)

    def schedule(
        self,
        wg: WorkGraph,
        contractors: list[Contractor],
        spec: ScheduleSpec = ScheduleSpec(),
        assigned_parent_time: Time = Time(0),
        sgs_type: ScheduleGenerationScheme = ScheduleGenerationScheme.Parallel,
        landscape: LandscapeConfiguration = LandscapeConfiguration(),
    ) -> Schedule:
        """Produce final schedule from best chromosome.

        Формирует итоговое расписание из лучшей хромосомы.

        Args:
            wg: Work graph to schedule.
                Граф работ для планирования.
            contractors: Available contractors.
                Доступные подрядчики.
            spec: Schedule specification.
                Спецификация расписания.
            assigned_parent_time: Start time of parent context.
                Время начала родительского контекста.
            sgs_type: Schedule generation scheme.
                Схема генерации расписания.
            landscape: Landscape configuration.
                Конфигурация местности.

        Returns:
            Schedule: Generated schedule.
            Schedule: Сформированное расписание.
        """
        best_ind = self.run(wg, contractors, spec, assigned_parent_time, landscape)

        toolbox = create_toolbox(wg=wg, contractors=contractors, landscape=landscape,
                                 assigned_parent_time=assigned_parent_time, spec=spec,
                                 sgs_type=sgs_type)
        node2swork = toolbox.chromosome_to_schedule(best_ind)[0]

        return Schedule.from_scheduled_works(node2swork.values(), wg)
