"""Run advanced WorkGraph documentation examples. Запустить примеры из раздела о WorkGraph."""

from __future__ import annotations

from pathlib import Path

from sampo.generator.base import SimpleSynthetic
from sampo.generator.pipeline import SyntheticGraphType
from sampo.pipeline import SchedulingPipeline
from sampo.pipeline.lag_optimization import LagOptimizationStrategy
from sampo.scheduler.heft import HEFTScheduler
from sampo.schemas.graph import EdgeType, GraphNode, WorkGraph
from sampo.schemas.requirements import WorkerReq
from sampo.schemas.time import Time
from sampo.schemas.works import WorkUnit


def run_synthetic_example(seed: int = 123) -> WorkGraph:
    """Generate a synthetic WorkGraph. Сгенерировать синтетический WorkGraph."""
    synth = SimpleSynthetic(seed)
    work_graph = synth.work_graph(
        mode=SyntheticGraphType.GENERAL,
        cluster_counts=3,
        bottom_border=6,
        top_border=10,
    )
    assert work_graph.vertex_count > 0
    return work_graph


def run_csv_pipeline_example() -> WorkGraph:
    """Load a WorkGraph from CSV via pipeline. Загрузить WorkGraph из CSV через конвейер."""
    csv_path = Path("tests/parser/test_wg.csv")
    assert csv_path.exists(), "CSV example is missing"
    project = (
        SchedulingPipeline.create()
        .wg(wg=str(csv_path), sep=";", all_connections=True)
        .lag_optimize(LagOptimizationStrategy.TRUE)
        .schedule(HEFTScheduler())
        .finish()[0]
    )
    assert project.schedule.execution_time > Time(0)
    assert project.wg.vertex_count > 0
    return project.wg


def run_manual_nodes_example() -> WorkGraph:
    """Assemble WorkGraph from custom nodes. Собрать WorkGraph из пользовательских узлов."""
    work_a = WorkUnit(
        id="A",
        name="Task A",
        worker_reqs=[
            WorkerReq(kind="general", volume=Time(10), min_count=1, max_count=2)
        ],
        volume=1.0,
        is_service_unit=False,
    )
    work_b = WorkUnit(
        id="B",
        name="Task B",
        worker_reqs=[],
        volume=1.0,
        is_service_unit=False,
    )
    work_c = WorkUnit(
        id="C",
        name="Task C",
        worker_reqs=[],
        volume=1.0,
        is_service_unit=False,
    )

    node_a = GraphNode(work_a, [])
    node_b = GraphNode(work_b, [(node_a, 0, EdgeType.FinishStart)])
    node_c = GraphNode(work_c, [(node_b, 0, EdgeType.FinishStart)])
    work_graph = WorkGraph.from_nodes([node_a, node_b, node_c])
    assert work_graph.vertex_count == 5  # start + finish + 3 works
    return work_graph


def main() -> None:
    """Run all WorkGraph documentation examples. Выполнить все примеры из документации по WorkGraph."""
    run_synthetic_example()
    run_csv_pipeline_example()
    run_manual_nodes_example()


if __name__ == "__main__":
    main()
