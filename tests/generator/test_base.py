"""Validation tests for synthetic generator utilities.

Проверочные тесты для утилит синтетического генератора.
"""

from sampo.generator.base import SimpleSynthetic
import pytest


def test_generated_graphs_have_non_negative_values() -> None:
    """Ensure generated graphs have non-negative volumes, lags and expected size.

    Убеждается, что сгенерированные графы имеют неотрицательные объёмы, лага и ожидаемый размер.
    """
    synthetic = SimpleSynthetic(rand=42)
    small_wg = synthetic.small_work_graph()
    assert 30 <= len(small_wg.nodes) <= 50
    for node in small_wg.nodes:
        assert node.work_unit.volume >= 0
        for edge in node.edges_from:
            assert edge.lag is None or edge.lag >= 0

    big_wg = synthetic.work_graph(bottom_border=30)
    assert len(big_wg.nodes) >= 30
    for node in big_wg.nodes:
        assert node.work_unit.volume >= 0
        for edge in node.edges_from:
            assert edge.lag is None or edge.lag >= 0


def test_set_materials_for_wg_invalid_bounds() -> None:
    """Check that incorrect borders raise :class:`ValueError`.

    Проверяет, что неправильные границы вызывают :class:`ValueError`.
    """
    synthetic = SimpleSynthetic(rand=42)
    wg = synthetic.small_work_graph()
    with pytest.raises(ValueError):
        synthetic.set_materials_for_wg(wg, ['a', 'b'], bottom_border=3, top_border=2)
    with pytest.raises(ValueError):
        synthetic.set_materials_for_wg(wg, ['a', 'b'], bottom_border=1, top_border=3)
