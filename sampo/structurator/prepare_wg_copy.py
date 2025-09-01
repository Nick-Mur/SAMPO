"""Helpers for copying work graphs and restoring connections.

Вспомогательные функции для копирования графов работ и восстановления связей.
"""

from copy import deepcopy

from sampo.schemas.graph import GraphNode, WorkGraph
from sampo.schemas.utils import uuid_str
from sampo.schemas.works import WorkUnit


def copy_graph_node(
    node: GraphNode, new_id: int | str | None = None, change_id: bool = True
) -> tuple[GraphNode, tuple[str, str]]:
    """Deep-copy a node optionally changing its identifier.

    Создать глубокую копию узла с возможной сменой идентификатора.

    Args:
        node: Original graph node.
            Исходный узел графа.
        new_id: Desired identifier for the copy.
            Желаемый идентификатор для копии.
        change_id: Whether to generate a new identifier if none provided.
            Нужно ли генерировать новый идентификатор, если он не задан.

    Returns:
        Tuple of the new node and pair of old and new identifiers.
        Кортеж из нового узла и пары старого и нового идентификаторов.
    """
    if change_id:
        new_id = new_id or uuid_str()
        new_id = str(new_id) if isinstance(new_id, int) else new_id
    else:
        new_id = node.work_unit.id
    wu = node.work_unit
    new_wu = WorkUnit(id=new_id, name=wu.name,
                      worker_reqs=deepcopy(wu.worker_reqs),
                      material_reqs=deepcopy(wu.material_reqs),
                      equipment_reqs=deepcopy(wu.equipment_reqs),
                      object_reqs=deepcopy(wu.object_reqs),
                      zone_reqs=deepcopy(wu.zone_reqs),
                      group=wu.group,
                      is_service_unit=wu.is_service_unit, volume=wu.volume, volume_type=wu.volume_type)
    return GraphNode(new_wu, []), (wu.id, new_id)


def restore_parents(
    new_nodes: dict[str, GraphNode],
    original_wg: WorkGraph,
    old_to_new_ids: dict[str, str],
    excluded_ids: set[str],
) -> None:
    """Restore parent edges for copied nodes.

    Восстановить ребра к родителям для скопированных узлов.

    Args:
        new_nodes: Copied nodes.
            Скопированные узлы.
        original_wg: Original work graph used for reference.
            Исходный граф работ, используемый для ссылки.
        old_to_new_ids: Mapping from old identifiers to new ones.
            Отображение от старых идентификаторов к новым.
        excluded_ids: Set of node identifiers that should be ignored.
            Множество идентификаторов узлов, которые следует игнорировать.

    Returns:
        None
        None
    """
    for node in original_wg.nodes:
        if node.id in old_to_new_ids and node.id not in excluded_ids:
            new_node = new_nodes[old_to_new_ids[node.id]]
            new_node.add_parents([(new_nodes[old_to_new_ids[edge.start.id]], edge.lag, edge.type)
                                  for edge in node.edges_to
                                  if edge.start.id in old_to_new_ids and edge.start.id not in excluded_ids])


def prepare_work_graph_copy(
    wg: WorkGraph,
    excluded_nodes: list[GraphNode] | None = None,
    use_ids_simplification: bool = False,
    id_offset: int = 0,
    change_id: bool = True,
) -> tuple[dict[str, GraphNode], dict[str, str]]:
    """Create a copy of a work graph with new identifiers.

    Создать копию графа работ с новыми идентификаторами.

    Args:
        wg: Original work graph.
            Исходный граф работ.
        excluded_nodes: Nodes to exclude from the copy.
            Узлы, исключаемые из копии.
        use_ids_simplification: Whether to use short numeric identifiers.
            Использовать ли короткие числовые идентификаторы.
        id_offset: Offset for numeric identifiers.
            Смещение для числовых идентификаторов.
        change_id: Whether to generate new identifiers.
            Нужно ли генерировать новые идентификаторы.

    Returns:
        Dictionary of new nodes and mapping from old to new identifiers.
        Словарь новых узлов и отображение старых идентификаторов в новые.
    """
    excluded_nodes = excluded_nodes or []
    excluded_nodes = {node.id for node in excluded_nodes}
    node_list = [(id_offset + ind, node) for ind, node in enumerate(wg.nodes)] \
        if use_ids_simplification \
        else [(None, node) for node in wg.nodes]
    nodes, old_to_new_ids = list(zip(*[copy_graph_node(node, ind, change_id) for ind, node in node_list
                                       if node.id not in excluded_nodes]))
    id_old_to_new = dict(old_to_new_ids)
    nodes = {node.id: node for node in nodes}
    restore_parents(nodes, wg, id_old_to_new, excluded_nodes)
    return nodes, id_old_to_new


def new_start_finish(
    original_wg: WorkGraph,
    copied_nodes: dict[str, GraphNode],
    old_to_new_ids: dict[str, str],
) -> tuple[GraphNode, GraphNode]:
    """Return start and finish nodes for a copied graph.

    Вернуть начальный и конечный узлы для скопированного графа.

    Args:
        original_wg: Work graph used for copying.
            Граф работ, использованный для копирования.
        copied_nodes: Nodes of the copied graph.
            Узлы скопированного графа.
        old_to_new_ids: Mapping from old identifiers to new ones.
            Отображение от старых идентификаторов к новым.

    Returns:
        Pair of start and finish nodes for the new graph.
        Пара начального и конечного узлов для нового графа.
    """
    new_start = copied_nodes[old_to_new_ids[original_wg.start.id]]
    new_finish = copied_nodes[old_to_new_ids[original_wg.finish.id]]
    return new_start, new_finish
