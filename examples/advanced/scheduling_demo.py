"""Execute scheduling usage examples from the advanced guide.
Выполнить примеры использования планировщика из расширенного руководства."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from sampo.generator.base import SimpleSynthetic
from sampo.pipeline import SchedulingPipeline
from sampo.pipeline.lag_optimization import LagOptimizationStrategy
from sampo.scheduler import GeneticScheduler
from sampo.scheduler.heft import HEFTScheduler


def run_direct_scheduler(seed: int = 21) -> None:
    """Schedule a synthetic project with HEFT and show the makespan.
    Спланировать синтетический проект с помощью HEFT и показать длительность."""

    synthetic = SimpleSynthetic(seed)
    work_graph = synthetic.work_graph(bottom_border=20, top_border=25)
    contractor = synthetic.contractor(pack_worker_count=35)

    scheduler = HEFTScheduler()
    schedule, *_ = scheduler.schedule(work_graph, [contractor])
    print("HEFT makespan:", schedule.execution_time)


def run_pipeline_example() -> None:
    """Run the scheduling pipeline with a genetic scheduler.
    Запустить конвейер планирования с генетическим планировщиком."""

    result = (
        SchedulingPipeline.create()
        .wg("tests/parser/test_wg.csv", sep=";", all_connections=True)
        .lag_optimize(LagOptimizationStrategy.TRUE)
        .schedule(
            GeneticScheduler(
                number_of_generation=3,
                size_of_population=10,
                mutate_order=0.1,
                mutate_resources=0.1,
                seed=123,
            )
        )
        .finish()
    )[0]

    schedule = result.schedule
    print("Pipeline makespan:", schedule.execution_time)
    df = schedule.merged_stages_datetime_df("2025-01-01")
    print(df.head())


def main() -> None:
    """Execute both scheduling demonstrations.
    Выполнить обе демонстрации планирования."""

    run_direct_scheduler()
    run_pipeline_example()


if __name__ == "__main__":
    main()
