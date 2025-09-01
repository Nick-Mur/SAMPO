"""Utility helpers for schedulers.

Вспомогательные функции для планировщиков.
"""

from collections import defaultdict
from typing import Iterable

from toposort import toposort_flatten

from sampo.schemas import Worker, Contractor, WorkGraph, GraphNode
from sampo.schemas.types import WorkerName, ContractorName

WorkerContractorPool = dict[WorkerName, dict[ContractorName, Worker]]


def get_worker_contractor_pool(contractors: Iterable[Contractor]) -> WorkerContractorPool:
    """Build worker-contractor mapping.

    Формирует отображение рабочих по подрядчикам.

    Args:
        contractors: Iterable of contractors.
            Итерация подрядчиков.

    Returns:
        WorkerContractorPool: Mapping of worker names to contractors.
        WorkerContractorPool: Отображение имён рабочих на подрядчиков.
    """
    worker_pool = defaultdict(dict)
    for contractor in contractors:
        for name, worker in contractor.workers.items():
            worker_pool[name][contractor.id] = worker.copy()
    return worker_pool


def get_head_nodes_with_connections_mappings(
    wg: WorkGraph,
) -> tuple[list[GraphNode], dict[str, set[str]], dict[str, set[str]]]:
    """Identify head nodes and reconstruct dependencies.

    Определяет головные узлы и восстанавливает зависимости.

    Args:
        wg: Work graph to analyze.
            Граф работ для анализа.

    Returns:
        tuple[list[GraphNode], dict[str, set[str]], dict[str, set[str]]]:
        Head nodes and parent/child mappings.
        tuple[list[GraphNode], dict[str, set[str]], dict[str, set[str]]]:
        Головные узлы и связи родитель/потомок.
    """
    # Filter the work graph nodes to identify all 'head nodes'.
    # A head node is one that is not an 'inseparable son', meaning it's either
    # the start of an inseparable chain or a standalone node.
    nodes = [node for node in wg.nodes if not node.is_inseparable_son()]

    # Construct a mapping from any node within an inseparable chain to its
    # corresponding head node.
    node2inseparable_parent = {child: node for node in nodes for child in node.get_inseparable_chain_with_self()}

    # Reconstruct parent-child relationships between the identified head nodes.
    # For each head node, gather all direct parents of any node within its
    # inseparable chain. Then, map these direct parents back to their
    # respective head nodes using `node2inseparable_parent`.
    node_id2parent_ids = {node.id: set(
        node2inseparable_parent[parent].id  # Get the head node ID for the actual parent
        for inseparable in node.get_inseparable_chain_with_self()  # Iterate through all parts of head node's chain
        for parent in inseparable.parents_set  # Get direct parents of each part
    ) - {node.id}  # Remove self-references
                          for node in nodes}

    # Reconstruct child-parent relationships in the same manner as parent-child.
    # For each head node, gather all direct children of any node within its
    # inseparable chain. Then, map these direct children back to their
    # respective head nodes using `node2inseparable_parent`.
    node_id2child_ids = {node.id: set(
        node2inseparable_parent[child].id  # Get the head node ID for the actual child
        for inseparable in node.get_inseparable_chain_with_self()  # Iterate through all parts of head node's chain
        for child in inseparable.children_set  # Get direct children of each part
    ) - {node.id}  # Remove self-references
                         for node in nodes}

    # Perform a topological sort on the head nodes based on their new parent dependencies.
    # This ensures the returned list of head nodes is ordered correctly for scheduling or analysis.
    tsorted_nodes_ids = toposort_flatten(node_id2parent_ids, sort=True)

    # Map the sorted head node IDs back to their corresponding GraphNode objects.
    tsorted_nodes = [wg[node_id] for node_id in tsorted_nodes_ids]

    return tsorted_nodes, node_id2parent_ids, node_id2child_ids
