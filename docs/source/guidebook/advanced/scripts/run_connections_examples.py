"""Run advanced connections documentation examples. Запустить примеры из раздела о связях."""

from __future__ import annotations

from sampo.schemas.graph import EdgeType, GraphNode, WorkGraph
from sampo.schemas.works import WorkUnit


def build_connection_demo() -> WorkGraph:
    """Construct a graph demonstrating edge types. Построить граф для демонстрации типов связей."""
    work_a = WorkUnit(id="A", name="Pour concrete", is_service_unit=False)
    work_b = WorkUnit(id="B", name="Bricklaying", is_service_unit=False)
    work_c = WorkUnit(id="C", name="Drilling", is_service_unit=False)
    work_d = WorkUnit(id="D", name="Anchoring", is_service_unit=False)
    work_e = WorkUnit(id="E", name="Monitoring start", is_service_unit=False)

    node_a = GraphNode(work_a, [])
    node_b = GraphNode(work_b, [(node_a, 3, EdgeType.LagFinishStart)])
    node_c = GraphNode(work_c, [(node_b, 0, EdgeType.InseparableFinishStart)])
    node_d = GraphNode(work_d, [(node_c, 0, EdgeType.InseparableFinishStart)])
    node_e = GraphNode(work_e, [(node_a, 0, EdgeType.StartStart)])

    work_graph = WorkGraph.from_nodes([node_a, node_b, node_c, node_d, node_e])
    assert node_b.parents[0] == node_a
    assert node_c.inseparable_parent == node_b
    assert node_b.inseparable_son == node_c
    assert node_a not in node_e.parents_set
    assert any(edge.type == EdgeType.LagFinishStart for edge in node_b.edges_to)
    assert node_a in node_e.neighbors
    return work_graph


def main() -> None:
    """Run connections documentation examples. Выполнить примеры из документации по связям."""
    build_connection_demo()


if __name__ == "__main__":
    main()
