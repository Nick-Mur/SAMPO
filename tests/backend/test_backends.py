"""Tests for computational backends.

Тесты для вычислительных бэкендов.
"""

import sampo.scheduler  # noqa: F401 to ensure scheduler is loaded before backends
from uuid import uuid4

import pytest

from sampo.base import SAMPO
from sampo.backend.default import DefaultComputationalBackend
from sampo.backend.multiproc import MultiprocessingComputationalBackend
from sampo.scheduler.heft import HEFTScheduler
from sampo.schemas.graph import WorkGraph, EdgeType
from sampo.schemas.contractor import Contractor
from sampo.schemas.resources import Worker
from sampo.schemas.scheduled_work import ScheduledWork
from sampo.utilities.sampler import Sampler


@pytest.fixture
def simple_setup():
    """Create a deterministic two-node work graph and contractor.

    Создает детерминированный граф из двух работ и подрядчика.
    """
    sampler = Sampler(42)
    n1 = sampler.graph_node("n1", [], group="0", work_id="1")
    n2 = sampler.graph_node("n2", [(n1, 0, EdgeType.FinishStart)], group="1", work_id="2")
    wg = WorkGraph.from_nodes([n1, n2])
    reqs: dict[str, int] = {}
    for node in wg.nodes:
        for req in node.work_unit.worker_reqs:
            reqs[req.kind] = max(reqs.get(req.kind, 0), req.min_count)
    contractor_id = str(uuid4())
    workers = {k: Worker(str(uuid4()), k, 10, contractor_id=contractor_id) for k in reqs}
    contractors = [Contractor(id=contractor_id, name="C", workers=workers, equipments={})]
    return wg, contractors


def _extract_timing(schedule_dict: dict[str, ScheduledWork]) -> dict[str, tuple[int, int]]:
    """Convert scheduled works to start/finish pairs.

    Преобразует запланированные работы в пары начала и окончания.
    """
    return {k: (sw.start_time.value, sw.finish_time.value) for k, sw in schedule_dict.items()}


def test_heft_schedule_same_on_backends(simple_setup):
    """HEFT scheduler produces identical schedule on both backends.

    Планировщик HEFT формирует идентичное расписание на обоих бэкендах.
    """
    wg, contractors = simple_setup
    SAMPO.backend = DefaultComputationalBackend()
    default_schedule = HEFTScheduler().schedule(wg, contractors)[0].to_schedule_work_dict
    SAMPO.backend = MultiprocessingComputationalBackend(1)
    multiproc_schedule = HEFTScheduler().schedule(wg, contractors)[0].to_schedule_work_dict
    assert _extract_timing(default_schedule) == _extract_timing(multiproc_schedule)


def test_multiproc_invalid_cpu(simple_setup):
    """Multiprocessing backend raises ValueError on non-positive CPU count.

    Многопроцессорный бэкенд поднимает ValueError при неположительном числе CPU.
    """
    wg, contractors = simple_setup
    backend = MultiprocessingComputationalBackend(0)
    backend.cache_scheduler_info(wg, contractors)
    backend.cache_genetic_info(population_size=1)
    with pytest.raises(ValueError):
        backend.generate_first_population(1)
