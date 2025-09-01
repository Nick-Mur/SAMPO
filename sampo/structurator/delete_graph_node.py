"""Operations for removing nodes from work graphs.

Операции по удалению узлов из графов работ.
"""

from sampo.schemas.graph import WorkGraph, GraphNode
from sampo.structurator.prepare_wg_copy import prepare_work_graph_copy, new_start_finish


def delete_graph_node(
    original_wg: WorkGraph, remove_gn_id: str, change_id: bool = True
) -> WorkGraph:
    """Delete a task from a work graph.

    Удалить задачу из графа работ.

    If the task consists of inseparable nodes, all of them are removed.
    Если задача содержит неразделимые узлы, удаляются все они.

    Args:
        original_wg: WorkGraph from which the task is removed.
            WorkGraph, из которого удаляется задача.
        remove_gn_id: Identifier of any node from the task to delete.
            Идентификатор любого узла удаляемой задачи.
        change_id: Whether to generate new identifiers in the copy.
            Требуется ли генерировать новые идентификаторы в копии.

    Returns:
        Work graph without the specified task.
        Граф работ без указанной задачи.
    """
    copied_nodes, old_to_new_ids = prepare_work_graph_copy(original_wg, change_id=change_id)

    copied_remove_gn = copied_nodes[old_to_new_ids[remove_gn_id]]

    inseparable_chain = copied_remove_gn.get_inseparable_chain()
    if inseparable_chain is not None:
        copied_remove_gn = inseparable_chain[len(inseparable_chain) - 1]
        parent_to_delete = copied_remove_gn.inseparable_parent
        while parent_to_delete is not None:
            copied_remove_gn = parent_to_delete
            parent_to_delete = copied_remove_gn.inseparable_parent
            _node_deletion(copied_remove_gn, copied_nodes)
    else:
        _node_deletion(copied_remove_gn, copied_nodes)

    start, finish = new_start_finish(original_wg, copied_nodes, old_to_new_ids)

    return WorkGraph(start, finish)


def _node_deletion(remove_gn: GraphNode, nodes: dict[str, GraphNode]):
    parents = remove_gn.parents
    children = remove_gn.children

    for parent in parents:
        for edge in parent.edges_from:
            if edge.finish.id == remove_gn.id:
                parent.edges_from.remove(edge)

    for child in children:
        for edge in child.edges_to:
            if edge.start.id == remove_gn.id:
                child.edges_to.remove(edge)

    nodes.pop(remove_gn.id)

    for child in children:
        child.add_parents(parents)
