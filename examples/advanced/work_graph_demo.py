"""Reproduce WorkGraph creation examples from the advanced guide.
Воспроизвести примеры создания WorkGraph из расширенного руководства."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from sampo.generator.base import SimpleSynthetic
from sampo.generator.pipeline import SyntheticGraphType
from sampo.pipeline import SchedulingPipeline
from sampo.pipeline.lag_optimization import LagOptimizationStrategy
from sampo.scheduler.heft import HEFTScheduler
from sampo.schemas.graph import EdgeType, GraphNode, WorkGraph
from sampo.schemas.requirements import WorkerReq
from sampo.schemas.time import Time
from sampo.schemas.works import WorkUnit


def generate_synthetic_graph() -> WorkGraph:
    """Create a synthetic graph with the documented parameters.
    Создать синтетический граф с параметрами из документации."""

    synthetic = SimpleSynthetic()
    return synthetic.work_graph(
        mode=SyntheticGraphType.GENERAL,
        cluster_counts=10,
        bottom_border=100,
        top_border=200,
    )


def load_graph_from_csv() -> WorkGraph:
    """Load a graph through the scheduling pipeline to mimic CSV import.
    Загрузить граф через конвейер планирования, имитируя импорт CSV."""

    result = (
        SchedulingPipeline.create()
        .wg(wg="tests/parser/test_wg.csv", sep=";", all_connections=True)
        .lag_optimize(LagOptimizationStrategy.TRUE)
        .schedule(HEFTScheduler())
        .finish()
    )[0]
    return result.wg


def build_graph_programmatically() -> WorkGraph:
    """Assemble a small graph manually with explicit dependencies.
    Собрать небольшой граф вручную с явными зависимостями."""

    wu_a = WorkUnit(
        id="A",
        name="Task A",
        worker_reqs=[WorkerReq("general", Time(10), 2, 4)],
        volume=1.0,
        is_service_unit=False,
    )
    wu_b = WorkUnit(id="B", name="Task B", volume=1.0, is_service_unit=False)
    wu_c = WorkUnit(id="C", name="Task C", volume=1.0, is_service_unit=False)

    node_a = GraphNode(wu_a, [])
    node_b = GraphNode(wu_b, [(node_a, 0, EdgeType.FinishStart)])
    node_c = GraphNode(wu_c, [(node_b, 0, EdgeType.FinishStart)])
    return WorkGraph.from_nodes([node_a, node_b, node_c])


def main() -> None:
    """Generate and summarize all WorkGraph examples.
    Сгенерировать и описать все примеры WorkGraph."""

    synthetic_graph = generate_synthetic_graph()
    csv_graph = load_graph_from_csv()
    manual_graph = build_graph_programmatically()

    print("Synthetic graph vertices:", synthetic_graph.vertex_count)
    print("CSV graph vertices:", csv_graph.vertex_count)
    print("Manual graph vertices:", manual_graph.vertex_count)


if __name__ == "__main__":
    main()
