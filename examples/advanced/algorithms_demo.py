"""Run advanced scheduling algorithm demonstrations.
Запуск расширенных демонстраций алгоритмов планирования."""

from __future__ import annotations

import sys
from pathlib import Path
from random import Random
from uuid import uuid4

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from sampo.generator.base import SimpleSynthetic
from sampo.scheduler.genetic import GeneticScheduler
from sampo.scheduler.heft import HEFTScheduler
from sampo.scheduler.topological import TopologicalScheduler
from sampo.schemas.contractor import Contractor
from sampo.schemas.graph import WorkGraph
from sampo.schemas.resources import Worker


def _run_scheduler_batch(work_graph: WorkGraph, contractors: list[Contractor]) -> None:
    """Execute several schedulers on the same dataset and print makespans.
    Выполнить несколько планировщиков на одном наборе данных и вывести длительности."""

    schedulers = (
        HEFTScheduler(),
        TopologicalScheduler(),
        GeneticScheduler(
            number_of_generation=5,
            size_of_population=15,
            mutate_order=0.2,
            mutate_resources=0.2,
            seed=123,
        ),
    )
    for scheduler in schedulers:
        schedule, *_ = scheduler.schedule(work_graph, contractors)
        print(f"{scheduler.scheduler_type} makespan: {schedule.execution_time}")


def run_basic_algorithms(seed: int = 231) -> None:
    """Demonstrate HEFT, Topological, and Genetic schedulers on a synthetic graph.
    Продемонстрировать планировщики HEFT, Topological и Genetic на синтетическом графе."""

    synthetic = SimpleSynthetic(seed)
    work_graph = synthetic.work_graph(bottom_border=25, top_border=30)
    contractor = synthetic.contractor(pack_worker_count=40)
    _run_scheduler_batch(work_graph, [contractor])


def run_multi_agent_auction(seed: int = 231) -> None:
    """Run a stochastic auction between HEFT and Topological agents.
    Запустить стохастический аукцион между агентами HEFT и Topological."""

    try:
        from sampo.scheduler.multi_agency.multi_agency import Agent, StochasticManager
    except ModuleNotFoundError as error:  # pragma: no cover - environment dependent
        print(f"Skipping multi-agent auction due to missing dependency: {error}")
        return

    synthetic = SimpleSynthetic(seed)
    work_graph = synthetic.work_graph(bottom_border=30, top_border=35)

    kinds = {req.kind for node in work_graph.nodes for req in node.work_unit.worker_reqs}
    contractor_id = str(uuid4())
    workers = {
        kind: Worker(str(uuid4()), kind, 50, contractor_id=contractor_id)
        for kind in kinds
    }
    contractors = [Contractor(id=contractor_id, name="Universal", workers=workers, equipments={})]

    agents = [
        Agent("HEFT", HEFTScheduler(), contractors),
        Agent("Topological", TopologicalScheduler(), contractors),
    ]
    manager = StochasticManager(agents)
    start, end, schedule, winner = manager.run_auction(work_graph)
    print(f"Auction winner: {winner.name}, makespan: {end - start}, schedule id: {schedule.id}")


def run_multi_agent_blocks(seed: int = 231) -> None:
    """Manage a block graph with dedicated contractors for each agent.
    Управлять графом блоков с выделенными подрядчиками для каждого агента."""

    try:
        from sampo.scheduler.multi_agency.block_generator import (
            SyntheticBlockGraphType,
            generate_blocks,
        )
        from sampo.scheduler.multi_agency.multi_agency import Agent, StochasticManager
    except ModuleNotFoundError as error:  # pragma: no cover - environment dependent
        print(f"Skipping block management due to missing dependency: {error}")
        return

    rand = Random(seed)
    block_graph = generate_blocks(
        SyntheticBlockGraphType.RANDOM,
        n_blocks=4,
        type_prop=[1, 1, 1],
        count_supplier=lambda _: (10, 15),
        edge_prob=0.3,
        rand=rand,
    )

    synthetic = SimpleSynthetic(rand)
    contractor_a = synthetic.contractor(pack_worker_count=40)
    contractor_b = synthetic.contractor(pack_worker_count=40)

    agents = [
        Agent("HEFT", HEFTScheduler(), [contractor_a]),
        Agent("Topo", TopologicalScheduler(), [contractor_b]),
    ]
    manager = StochasticManager(agents)
    scheduled_blocks = manager.manage_blocks(block_graph)

    print("Scheduled blocks summary:")
    for block_id, sblock in scheduled_blocks.items():
        print(
            f"Block {block_id}: agent={sblock.agent.name}, "
            f"start={sblock.start_time}, end={sblock.end_time}, duration={sblock.duration}"
        )
    makespan = max(sblock.end_time for sblock in scheduled_blocks.values())
    print(f"Overall makespan: {makespan}")


if __name__ == "__main__":
    run_basic_algorithms()
    run_multi_agent_auction()
    run_multi_agent_blocks()
