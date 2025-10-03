"""Run advanced contractor documentation examples. Запустить примеры из раздела о подрядчиках."""

from __future__ import annotations

from sampo.generator.base import SimpleSynthetic
from sampo.generator.environment.contractor_by_wg import (
    ContractorGenerationMethod,
    get_contractor_by_wg,
)
from sampo.schemas.contractor import Contractor
from sampo.schemas.interval import IntervalGaussian
from sampo.schemas.resources import Worker


def build_manual_contractor() -> Contractor:
    """Create a manual contractor definition. Создать подрядчика вручную."""
    workers = {
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
    }
    contractor = Contractor(id="c1", name="Contractor A", workers=workers)
    assert set(contractor.workers) == {"driver", "fitter"}
    return contractor


def build_synthetic_contractor(seed: int = 456) -> Contractor:
    """Generate a contractor with SimpleSynthetic. Сгенерировать подрядчика через SimpleSynthetic."""
    synth = SimpleSynthetic(seed)
    contractor = synth.contractor(pack_worker_count=10)
    assert contractor.workers, "Synthetic contractor must include workers"
    return contractor


def build_contractor_from_wg() -> Contractor:
    """Create contractor based on WorkGraph requirements. Создать подрядчика по требованиям WorkGraph."""
    synth = SimpleSynthetic(321)
    work_graph = synth.work_graph(bottom_border=5, top_border=7)
    contractor = get_contractor_by_wg(
        work_graph,
        scaler=1.0,
        method=ContractorGenerationMethod.AVG,
    )
    assert contractor.workers, "Generated contractor must provide workers"
    return contractor


def main() -> None:
    """Run contractor documentation examples. Выполнить примеры из документации о подрядчиках."""
    build_manual_contractor()
    build_synthetic_contractor()
    build_contractor_from_wg()


if __name__ == "__main__":
    main()
