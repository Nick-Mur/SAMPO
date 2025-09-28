"""Run advanced algorithms documentation examples. Запустить примеры из раздела об алгоритмах."""

from __future__ import annotations

from random import Random
from typing import Iterable
from uuid import uuid4

from sampo.generator.base import SimpleSynthetic
from sampo.scheduler.genetic import GeneticScheduler
from sampo.scheduler.heft import HEFTBetweenScheduler, HEFTScheduler
from sampo.scheduler.topological import TopologicalScheduler
from sampo.schemas.contractor import Contractor
from sampo.schemas.resources import Worker
from sampo.schemas.time import Time
from sampo.schemas.works import WorkUnit

try:
    from sampo.scheduler.multi_agency.block_generator import (
        SyntheticBlockGraphType,
        generate_blocks,
    )
    from sampo.scheduler.multi_agency.multi_agency import Agent, StochasticManager
    MULTI_AGENCY_AVAILABLE = True
except ModuleNotFoundError:
    MULTI_AGENCY_AVAILABLE = False


def _universal_contractor(work_units: Iterable[WorkUnit]) -> list[Contractor]:
    """Create a contractor that covers every worker requirement. Создать подрядчика для всех требований."""
    kinds = {req.kind for unit in work_units for req in unit.worker_reqs}
    contractor_id = str(uuid4())
    workers = {
        kind: Worker(str(uuid4()), kind, 50, contractor_id=contractor_id)
        for kind in kinds
    }
    return [Contractor(id=contractor_id, name="Universal", workers=workers, equipments={})]


def run_single_graph_examples(seed: int = 231) -> None:
    """Execute heuristic and genetic scheduling samples. Выполнить примеры эвристик и генетики."""
    synth = SimpleSynthetic(seed)
    work_graph = synth.work_graph(bottom_border=12, top_border=16)
    contractors = _universal_contractor(node.work_unit for node in work_graph.nodes)

    schedulers = [
        ("HEFT", HEFTScheduler()),
        ("HEFTBetween", HEFTBetweenScheduler()),
        ("Topological", TopologicalScheduler()),
        (
            "Genetic",
            GeneticScheduler(
                number_of_generation=5,
                size_of_population=20,
                mutate_order=0.2,
                mutate_resources=0.2,
            ),
        ),
    ]

    for label, scheduler in schedulers:
        schedule = scheduler.schedule(work_graph, contractors)[0]
        assert schedule.execution_time > Time(0), f"{label} produced non-positive makespan"


def run_multi_agent_examples(seed: int = 231) -> None:
    """Execute multi-agent auction and block scheduling. Выполнить аукцион и блочное планирование."""
    if not MULTI_AGENCY_AVAILABLE:
        print("Skipping multi-agent examples due to missing multi-agency dependencies.")
        return

    synth = SimpleSynthetic(seed)
    work_graph = synth.work_graph(bottom_border=8, top_border=10)
    contractors = _universal_contractor(node.work_unit for node in work_graph.nodes)

    agents = [
        Agent("HEFT", HEFTScheduler(), contractors),
        Agent("Topological", TopologicalScheduler(), contractors),
    ]
    manager = StochasticManager(agents)
    start_time, end_time, schedule, winner = manager.run_auction(work_graph)
    assert winner.name in {"HEFT", "Topological"}
    assert end_time > start_time >= Time(0)
    assert schedule.execution_time == end_time - start_time

    random_source = Random(seed)
    block_graph = generate_blocks(
        SyntheticBlockGraphType.RANDOM,
        n_blocks=3,
        type_prop=[1, 1, 1],
        count_supplier=lambda _: (5, 8),
        edge_prob=0.4,
        rand=random_source,
    )

    contractor_a = synth.contractor(20)
    contractor_b = synth.contractor(20)

    block_agents = [
        Agent("HEFT", HEFTScheduler(), [contractor_a]),
        Agent("Topo", TopologicalScheduler(), [contractor_b]),
    ]
    block_manager = StochasticManager(block_agents)
    scheduled_blocks = block_manager.manage_blocks(block_graph)
    assert scheduled_blocks, "Block scheduling did not produce any blocks"
    for block in scheduled_blocks.values():
        assert block.end_time > block.start_time
        assert block.schedule.execution_time == block.end_time - block.start_time


def main() -> None:
    """Run all algorithm documentation examples. Выполнить все примеры из документации по алгоритмам."""
    run_single_graph_examples()
    run_multi_agent_examples()


if __name__ == "__main__":
    main()
