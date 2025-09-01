"""Lightweight transformations for work graphs.

Легкие преобразования графов работ.
"""

from sampo.schemas.graph import WorkGraph
from sampo.structurator.graph_insertion import prepare_work_graph_copy
from sampo.structurator.prepare_wg_copy import new_start_finish


def work_graph_ids_simplification(
    wg: WorkGraph, id_offset: int = 0, change_id: bool = True
) -> WorkGraph:
    """Create a copy of a graph with simplified numeric identifiers.

    Создать копию графа с упрощенными числовыми идентификаторами.

    Args:
        wg: Original work graph.
            Исходный граф работ.
        id_offset: Starting number for new identifiers.
            Начальное число для новых идентификаторов.
        change_id: Whether to generate new identifiers.
            Нужно ли генерировать новые идентификаторы.

    Returns:
        Work graph with numeric identifiers.
        Граф работ с числовыми идентификаторами.
    """
    nodes, old_to_new_ids = prepare_work_graph_copy(wg, [], use_ids_simplification=True, id_offset=id_offset)
    start = nodes[old_to_new_ids[wg.start.id]]
    finish = nodes[old_to_new_ids[wg.finish.id]]
    return WorkGraph(start, finish)
