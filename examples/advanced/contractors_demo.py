"""Run contractor-related examples from the advanced documentation.
Запустить примеры, связанные с подрядчиками, из расширенной документации."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from sampo.generator.base import SimpleSynthetic
from sampo.generator.environment.contractor_by_wg import (
    ContractorGenerationMethod,
    get_contractor_by_wg,
)
from sampo.schemas.contractor import Contractor
from sampo.schemas.graph import GraphNode, WorkGraph
from sampo.schemas.interval import IntervalGaussian
from sampo.schemas.requirements import WorkerReq
from sampo.schemas.resources import Worker
from sampo.schemas.time import Time
from sampo.schemas.works import WorkUnit


def create_manual_contractor() -> Contractor:
    """Create a contractor with explicit worker definitions.
    Создать подрядчика с явным определением работников."""

    contractor = Contractor(
        workers={
            "driver": Worker(
                id="w1",
                name="driver",
                count=8,
                productivity=IntervalGaussian(1.0, 0.1, 0.5, 1.5),
            ),
            "fitter": Worker(
                id="w2",
                name="fitter",
                count=6,
                productivity=IntervalGaussian(1.2, 0.1, 0.8, 1.6),
            ),
        },
        id="c1",
        name="Contractor A",
    )
    return contractor


def create_synthetic_contractor(seed: int = 42) -> Contractor:
    """Use SimpleSynthetic to create a contractor automatically.
    Использовать SimpleSynthetic для автоматического создания подрядчика."""

    synthetic = SimpleSynthetic(seed)
    return synthetic.contractor(pack_worker_count=10)


def create_contractor_from_work_graph() -> Contractor:
    """Aggregate worker requirements from a small work graph.
    Агрегировать требования к работникам из небольшого графа работ."""

    work_a = WorkUnit(
        id="A",
        name="Excavation",
        worker_reqs=[WorkerReq("digger", Time(4), 2, 3)],
        volume=1.0,
    )
    work_b = WorkUnit(
        id="B",
        name="Reinforcement",
        worker_reqs=[WorkerReq("fitter", Time(6), 2, 4)],
        volume=1.0,
    )
    work_graph = WorkGraph.from_nodes([GraphNode(work_a, []), GraphNode(work_b, [])])
    contractor = get_contractor_by_wg(
        work_graph,
        scaler=1.0,
        method=ContractorGenerationMethod.AVG,
    )
    return contractor


def main() -> None:
    """Create contractors via all documented methods and show summaries.
    Создать подрядчиков всеми описанными методами и показать сводку."""

    manual = create_manual_contractor()
    synthetic = create_synthetic_contractor()
    by_wg = create_contractor_from_work_graph()

    print("Manual contractor workers:")
    for worker in manual.workers.values():
        print(worker)

    print("\nSynthetic contractor worker kinds:", list(synthetic.workers))
    print("Generated from work graph worker kinds:", list(by_wg.workers))


if __name__ == "__main__":
    main()
