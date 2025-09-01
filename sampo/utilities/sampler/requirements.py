"""Utility functions for worker requirements sampling.

Вспомогательные функции для генерации требований к рабочим.
"""

import random
from typing import Optional

from sampo.schemas.requirements import WorkerReq
from sampo.utilities.sampler.resources import WORKER_TYPES, WorkerSpecialization
from sampo.utilities.sampler.types import MinMax


def get_worker_req(
    rand: random.Random,
    name: str,
    volume: Optional[MinMax[int]] = MinMax[int](1, 50),
    worker_count: Optional[MinMax[int]] = MinMax[int](1, 100),
) -> WorkerReq:
    """Generate a single worker requirement.

    Генерирует одно требование к рабочей силе.

    Args:
        rand: Random number generator.
            Генератор случайных чисел.
        name: Worker specialization.
            Специализация рабочего.
        volume: Range for work volume.
            Диапазон объёма работ.
        worker_count: Range for worker count.
            Диапазон количества работников.

    Returns:
        WorkerReq: Generated requirement.
            WorkerReq: Сгенерированное требование.
    """
    count = rand.randint(volume.min, volume.max)
    return WorkerReq(name, count, worker_count.min, worker_count.max)


def get_worker_reqs_list(
    rand: random.Random,
    volume: Optional[MinMax[int]] = MinMax[int](1, 50),
    worker_count: Optional[MinMax[int]] = MinMax[int](1, 100),
) -> list[WorkerReq]:
    """Create a randomized list of worker requirements.

    Создаёт случайный список требований к рабочим.

    Args:
        rand: Random number generator.
            Генератор случайных чисел.
        volume: Range for work volume.
            Диапазон объёма работ.
        worker_count: Range for worker count.
            Диапазон количества работников.

    Returns:
        list[WorkerReq]: Generated requirements list.
            list[WorkerReq]: Список сгенерированных требований.
    """
    names: list[WorkerSpecialization] = list(WORKER_TYPES)
    rand.shuffle(names)
    req_count = rand.randint(1, len(names))
    names = names[:req_count]
    return get_worker_specific_reqs_list(rand, names, volume, worker_count)


def get_worker_specific_reqs_list(
    rand: random.Random,
    worker_names: list[WorkerSpecialization],
    volume: Optional[MinMax[int]] = MinMax[int](1, 50),
    worker_count: Optional[MinMax[int]] = MinMax[int](1, 100),
) -> list[WorkerReq]:
    """Build requirements for specific worker types.

    Формирует требования для определённых типов рабочих.

    Args:
        rand: Random number generator.
            Генератор случайных чисел.
        worker_names: Required worker specializations.
            Необходимые специализации работников.
        volume: Range for work volume.
            Диапазон объёма работ.
        worker_count: Range for worker count.
            Диапазон количества работников.

    Returns:
        list[WorkerReq]: Generated requirements.
            list[WorkerReq]: Сгенерированные требования.
    """
    return [get_worker_req(rand, name, volume, worker_count) for name in worker_names]
