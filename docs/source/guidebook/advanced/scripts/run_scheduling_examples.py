"""Run advanced scheduling documentation examples. Запустить примеры из раздела о планировании."""

from __future__ import annotations

from sampo.generator.base import SimpleSynthetic
from sampo.pipeline import SchedulingPipeline
from sampo.scheduler.genetic import GeneticScheduler
from sampo.scheduler.heft.base import HEFTScheduler
from sampo.schemas.time import Time


def build_scheduling_inputs(seed: int = 789):
    """Prepare a small WorkGraph and contractors. Подготовить небольшой WorkGraph и подрядчиков."""
    synth = SimpleSynthetic(seed)
    work_graph = synth.work_graph(bottom_border=6, top_border=8)
    contractor = synth.contractor(pack_worker_count=15)
    return work_graph, [contractor]


def run_direct_scheduler_example() -> None:
    """Run a HEFT scheduler directly. Запустить планировщик HEFT напрямую."""
    work_graph, contractors = build_scheduling_inputs()
    scheduler = HEFTScheduler()
    schedule = scheduler.schedule(work_graph, contractors)[0]
    assert schedule.execution_time > Time(0)


def run_pipeline_scheduler_example(tmp_csv: str) -> None:
    """Run the pipeline-based scheduling example. Запустить пример планирования через конвейер."""
    result = (
        SchedulingPipeline.create()
        .wg(tmp_csv, sep=";", all_connections=True)
        .schedule(GeneticScheduler(number_of_generation=3, size_of_population=10))
        .finish()[0]
    )
    assert result.schedule.execution_time > Time(0)
    dataframe = result.schedule.merged_stages_datetime_df(offset="2025-01-01")
    assert not dataframe.empty


def main() -> None:
    """Run scheduling documentation examples. Выполнить примеры из документации по планированию."""
    run_direct_scheduler_example()
    run_pipeline_scheduler_example("tests/parser/test_wg.csv")


if __name__ == "__main__":
    main()
