"""Utilities for inserting one work graph into another.

Утилиты для вставки одного графа работ в другой.
"""

from sampo.schemas.graph import GraphNode, WorkGraph
from sampo.structurator.prepare_wg_copy import prepare_work_graph_copy, new_start_finish


def graph_in_graph_insertion(
    master_wg: WorkGraph,
    master_start: GraphNode,
    master_finish: GraphNode,
    slave_wg: WorkGraph,
    change_id: bool = True,
) -> WorkGraph:
    """Insert a work graph into another between two nodes.

    Вставить один граф работ в другой между двумя узлами.

    Args:
        master_wg: The graph into which insertion is performed.
            Граф, в который выполняется вставка.
        master_start: Node that becomes the parent for the inserted graph.
            Узел, который становится родителем вставляемого графа.
        master_finish: Node that becomes the child for the inserted graph.
            Узел, который становится потомком вставляемого графа.
        slave_wg: Graph to be inserted into the master graph.
            Граф, который вставляется в основной граф.
        change_id: Whether to generate new identifiers.
            Нужно ли генерировать новые идентификаторы.

    Returns:
        Combined work graph.
        Объединенный граф работ.
    """
    master_nodes, master_old_to_new_ids = prepare_work_graph_copy(master_wg, change_id=change_id)
    slave_nodes, slave_old_to_new = prepare_work_graph_copy(slave_wg, [slave_wg.start, slave_wg.finish], change_id)

    # add parent links from slave_wg's nodes to master_start node from slave_wg's nodes
    master_start = master_nodes[master_old_to_new_ids[master_start.id]]
    for edge in slave_wg.start.edges_from:
        slave_nodes[slave_old_to_new[edge.finish.id]].add_parents([master_start])

    # add parent links from master_finish to slave_wg's nodes
    master_finish = master_nodes[master_old_to_new_ids[master_finish.id]]
    master_finish.add_parents([slave_nodes[slave_old_to_new[edge.start.id]]
                               for edge in slave_wg.finish.edges_to])

    start, finish = new_start_finish(master_wg, master_nodes, master_old_to_new_ids)
    return WorkGraph(start, finish)
