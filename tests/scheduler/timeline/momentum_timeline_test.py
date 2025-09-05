from _pytest.fixtures import fixture
import numpy as np
import pytest

from sampo.scheduler.timeline.momentum_timeline import MomentumTimeline
from sampo.scheduler.utils import get_worker_contractor_pool
from sampo.schemas.graph import GraphNode
from sampo.schemas.requirements import WorkerReq, ZoneReq
from sampo.schemas.resources import Worker
from sampo.schemas.schedule_spec import WorkSpec
from sampo.schemas.time import Time
from sampo.schemas.types import ScheduleEvent, EventType
from sampo.schemas.works import WorkUnit
from sampo.schemas.landscape import LandscapeConfiguration
from sampo.schemas.zones import ZoneConfiguration


@fixture
def setup_timeline_context(setup_scheduler_parameters):
    setup_wg, setup_contractors, landscape = setup_scheduler_parameters
    setup_worker_pool = get_worker_contractor_pool(setup_contractors)
    worker_kinds = set([w_kind for contractor in setup_contractors for w_kind in contractor.workers.keys()])
    return MomentumTimeline(setup_worker_pool, landscape=landscape), \
        setup_wg, setup_contractors, setup_worker_pool, worker_kinds


def test_init_resource_structure(setup_timeline_context):
    timeline, wg, contractors, worker_pool, worker_kinds = setup_timeline_context
    assert len(timeline._timeline) != 0

    for contractor_timeline in timeline._timeline.values():
        assert len(contractor_timeline) == len(worker_kinds)

        for worker_timeline in contractor_timeline.values():
            assert len(worker_timeline) == 1

            first_event: ScheduleEvent = worker_timeline[0]
            assert first_event.seq_id == -1
            assert first_event.event_type == EventType.INITIAL
            assert first_event.time == Time(0)


def test_insert_works_with_one_worker_kind(setup_timeline_context):
    timeline, wg, contractors, worker_pool, worker_kinds = setup_timeline_context

    worker_kind = worker_kinds.pop()
    worker_kinds.add(worker_kind)  # make worker_kinds stay unchanged

    nodes = []

    for i in range(10):
        work_unit = WorkUnit(id=str(i), name=f'Work {str(i)}', worker_reqs=[WorkerReq(kind=worker_kind,
                                                                                      volume=Time(50),
                                                                                      min_count=10,
                                                                                      max_count=50)])
        nodes.append(GraphNode(work_unit=work_unit, parent_works=[]))

    node2swork = {}
    contractor = contractors[0]
    worker_count = contractor.workers[worker_kind].count
    for i, node in enumerate(nodes):
        worker_team = [Worker(id=str(i), name=worker_kind, count=worker_count // 2, contractor_id=contractor.id)]
        timeline.schedule(node, node2swork, worker_team, contractor, WorkSpec())


def test_update_events_multiple_worker_types(setup_timeline_context):
    """Verify event updates for several worker kinds.

    Проверяет обновление событий для нескольких типов работников.
    """
    timeline, wg, contractors, worker_pool, worker_kinds = setup_timeline_context
    if len(worker_kinds) < 2:
        pytest.skip('Need at least two worker kinds')

    contractor = contractors[0]
    kinds = list(worker_kinds)[:2]

    worker_reqs = []
    team = []
    for i, kind in enumerate(kinds):
        count = contractor.workers[kind].count
        worker_reqs.append(WorkerReq(kind=kind, volume=Time(5),
                                     min_count=count, max_count=count))
        team.append(Worker(id=str(i), name=kind, count=count,
                           contractor_id=contractor.id))

    wu = WorkUnit(id='m1', name='Multi', worker_reqs=worker_reqs)
    node1 = GraphNode(work_unit=wu, parent_works=[])
    node2 = GraphNode(work_unit=wu, parent_works=[node1])

    node2swork = {}
    timeline.schedule(node1, node2swork, team, contractor, WorkSpec())
    timeline.schedule(node2, node2swork, team, contractor, WorkSpec())

    for kind in kinds:
        state = timeline._timeline[contractor.id][kind]
        times = [ev.time for ev in state]
        assert times == sorted(times)
        assert all(ev.available_workers_count >= 0 for ev in state)
        assert len(state) == 5


def test_reschedule_respects_dependencies_and_zones(setup_timeline_context):
    """Ensure rescheduling obeys dependencies and zones.

    Проверяет соблюдение зависимостей и зон при повторном планировании.
    """
    _, wg, contractors, worker_pool, worker_kinds = setup_timeline_context
    contractor = contractors[0]
    worker_kind = next(iter(worker_kinds))
    worker_req = WorkerReq(kind=worker_kind, volume=Time(5),
                           min_count=1, max_count=1)
    zone_a = ZoneReq(kind='zone1', required_status=2)
    zone_b = ZoneReq(kind='zone1', required_status=1)

    wu_a = WorkUnit(id='a', name='A', worker_reqs=[worker_req], zone_reqs=[zone_a])
    wu_b = WorkUnit(id='b', name='B', worker_reqs=[worker_req], zone_reqs=[zone_b])
    node_a = GraphNode(work_unit=wu_a, parent_works=[])
    node_b = GraphNode(work_unit=wu_b, parent_works=[node_a])

    landscape = LandscapeConfiguration(
        zone_config=ZoneConfiguration(start_statuses={'zone1': 1},
                                      time_costs=np.zeros((3, 3)))
    )
    timeline = MomentumTimeline(worker_pool, landscape)
    team = [Worker(id='w', name=worker_kind, count=1,
                   contractor_id=contractor.id)]
    node2swork = {}
    timeline.schedule(node_a, node2swork, team, contractor, WorkSpec())
    timeline.schedule(node_b, node2swork, team, contractor, WorkSpec())

    assert node2swork[node_b].start_end_time[0] >= node2swork[node_a].start_end_time[1]
    assert node2swork[node_a].zones_pre
    assert node2swork[node_b].zones_pre
#
# TODO
# def test_update_resource_structure(setup_timeline, setup_worker_pool):
#     mut_name: WorkerName = list(setup_worker_pool.keys())[0]
#     mut_contractor: ContractorName = list(setup_worker_pool[mut_name].keys())[0]
#     mut_count = setup_timeline[(mut_contractor, mut_name)][0][1]
#
#     # mutate
#     worker = Worker(str(uuid4()), mut_name, 1, contractor_id=mut_contractor)
#     setup_timeline.update_timeline(0, Time(1), None, {}, [worker])
#
#     worker_timeline = setup_timeline[worker.get_agent_id()]
#
#     if mut_count == 1:
#         assert len(worker_timeline) == 1
#         assert worker_timeline[0] == (Time(0), 1)
#     else:
#         assert len(worker_timeline) == 2
#         assert worker_timeline[0] == (Time(1), 1)
#         assert worker_timeline[1] == (Time(0), mut_count - 1)
#
# TODO
# def test_schedule(setup_wg, setup_worker_pool, setup_contractors, setup_timeline):
#     ordered_nodes = prioritization(setup_wg)
#     node = ordered_nodes[-1]
#
#     reqs = build_index(node.work_unit.worker_reqs, attrgetter('kind'))
#     worker_team = [list(cont2worker.values())[0].copy() for name, cont2worker in setup_worker_pool.items() if
#                    name in reqs]
#
#     contractor_index = build_index(setup_contractors, attrgetter('id'))
#     contractor = contractor_index[worker_team[0].contractor_id] if worker_team else None
#
#     node2swork: Dict[GraphNode, ScheduledWork] = {}
#     setup_timeline.schedule(0, node, node2swork, worker_team, contractor, work_estimator=None)
#
#     assert len(node2swork) == 1
#     for swork in node2swork.values():
#         assert not swork.finish_time.is_inf()
