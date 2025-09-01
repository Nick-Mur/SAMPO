"""Routines for inserting single work units into a graph.

Процедуры вставки отдельных рабочих операций в граф.
"""

from sampo.schemas.graph import GraphNode, EdgeType, WorkGraph
from sampo.schemas.works import WorkUnit
from sampo.structurator.prepare_wg_copy import prepare_work_graph_copy, new_start_finish


def insert_work_unit(
    original_wg: WorkGraph,
    inserted_wu: WorkUnit,
    parents_edges: list[GraphNode] | list[tuple[GraphNode, float, EdgeType]],
    children_edges: list[GraphNode] | list[tuple[GraphNode, float, EdgeType]],
    change_id: bool = True,
) -> WorkGraph:
    """Insert a new node into a work graph.

    Вставить новый узел в граф работ.

    Args:
        original_wg: Graph where the node will be inserted.
            Граф, в который вставляется новый узел.
        inserted_wu: Work unit used to create the node.
            Производственная операция, из которой создается узел.
        parents_edges: Parents for the new node.
            Родительские узлы для нового узла.
        children_edges: Children for the new node.
            Дочерние узлы для нового узла.
        change_id: Whether to generate new identifiers.
            Нужно ли генерировать новые идентификаторы.

    Returns:
        New work graph with the inserted node.
        Новый граф работ с вставленным узлом.
    """
    reduced_parent_edges = _reduce_to_tuple_type(parents_edges)
    reduced_children_edges = _reduce_to_tuple_type(children_edges)

    copied_nodes, original_old_to_new_ids = prepare_work_graph_copy(original_wg, change_id=change_id)

    new_parents_edges = _new_edges(copied_nodes, original_old_to_new_ids, reduced_parent_edges)
    new_children_edges = _new_edges(copied_nodes, original_old_to_new_ids, reduced_children_edges)

    new_node = GraphNode(inserted_wu, new_parents_edges)
    for child, lag, edge in new_children_edges:
        child.add_parents([(new_node, lag, edge)])

    new_start, new_finish = new_start_finish(original_wg, copied_nodes, original_old_to_new_ids)

    return WorkGraph(new_start, new_finish)


def _new_edges(copied_nodes: dict[str, GraphNode], original_old_to_new_ids: dict[str, str],
               edges: list[tuple[GraphNode, float, EdgeType]]) \
        -> list[tuple[GraphNode, float, EdgeType]]:
    return [(copied_nodes[original_old_to_new_ids[parent.id]], lag, edge_type)
            for parent, lag, edge_type in edges]


def _reduce_to_tuple_type(edges: list[GraphNode] or list[tuple[GraphNode, float, EdgeType]]) \
        -> list[tuple[GraphNode, float, EdgeType]]:
    if isinstance(edges[0], GraphNode):
        return [(edge, -1, EdgeType.FinishStart) for edge in edges]
    else:
        return edges


