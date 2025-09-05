"""Tests for :func:`JustInTimeTimeline.update_timeline`."""

from typing import Tuple

from _pytest.fixtures import fixture

from sampo.scheduler.timeline.just_in_time_timeline import JustInTimeTimeline
from sampo.scheduler.utils import get_worker_contractor_pool
from sampo.schemas.graph import GraphNode
from sampo.schemas.resources import Worker
from sampo.schemas.schedule_spec import WorkSpec
from sampo.schemas.time import Time


@fixture(scope="function")
def timeline_context(setup_scheduler_parameters) -> Tuple[JustInTimeTimeline, Worker, GraphNode]:
    """Prepare timeline, worker and node for tests.

    Подготавливает временную шкалу, работника и узел для тестов.
    """
    wg, contractors, landscape = setup_scheduler_parameters
    worker_pool = get_worker_contractor_pool(contractors)
    timeline = JustInTimeTimeline(worker_pool, landscape=landscape)

    worker_offer = next(iter(next(iter(worker_pool.values())).values()))
    worker = worker_offer.copy()
    node = wg.nodes[0]
    return timeline, worker, node


def test_dependent_resources_return(timeline_context):
    """Workers return at finish time for dependent tasks.

    Рабочие возвращаются в момент окончания зависимой задачи.
    """
    timeline, worker, node = timeline_context
    spec = WorkSpec()
    finish = Time(5)

    # use all available workers of this type
    timeline.update_timeline(finish, Time(1), node, [worker], spec)

    start = timeline._find_min_start_time([worker], Time(0), spec)
    assert start == finish


def test_independent_resources_return(timeline_context):
    """All workers are blocked until finish time for independent tasks.

    Все рабочие блокируются до окончания независимой задачи.
    """
    timeline, worker, node = timeline_context
    spec = WorkSpec(is_independent=True)
    finish = Time(7)

    worker.with_count(1)
    timeline.update_timeline(finish, Time(2), node, [worker], spec)

    start = timeline._find_min_start_time([worker], Time(0), spec)
    assert start == finish


def test_event_order_preserved(timeline_context):
    """Event order is preserved when workers are added and removed.

    Порядок событий сохраняется при добавлении и извлечении работников.
    """
    timeline, worker, node = timeline_context
    spec = WorkSpec()

    worker.with_count(1)
    timeline.update_timeline(Time(10), Time(3), node, [worker], spec)
    timeline.update_timeline(Time(3), Time(1), node, [worker], spec)

    worker_timeline = timeline._timeline[worker.get_agent_id()]
    times = [t for t, _ in worker_timeline]
    assert times == sorted(times, reverse=True)

