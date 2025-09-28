"""Validate connection examples from the advanced documentation.
Проверить примеры связей из расширенной документации."""

from __future__ import annotations

import sys
from csv import DictReader
from io import StringIO
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from sampo.schemas.graph import EdgeType, GraphNode, WorkGraph
from sampo.schemas.requirements import WorkerReq
from sampo.schemas.time import Time
from sampo.schemas.works import WorkUnit


def build_connection_graph() -> WorkGraph:
    """Construct a work graph containing multiple edge types.
    Построить граф работ, содержащий несколько типов связей."""

    work_a = WorkUnit(
        id="A",
        name="Pour concrete",
        worker_reqs=[WorkerReq("builder", Time(8), 2, 4)],
        volume=1.0,
    )
    work_b = WorkUnit(id="B", name="Brickwork", volume=1.0)
    work_c = WorkUnit(id="C", name="Drilling", volume=1.0)
    work_d = WorkUnit(id="D", name="Anchoring", volume=1.0)
    work_e = WorkUnit(id="E", name="Monitoring", volume=1.0)

    node_a = GraphNode(work_a, [])
    node_b = GraphNode(work_b, [(node_a, 3, EdgeType.LagFinishStart)])
    node_c = GraphNode(work_c, [(node_b, 0, EdgeType.InseparableFinishStart)])
    node_d = GraphNode(work_d, [(node_c, 0, EdgeType.InseparableFinishStart)])
    node_e = GraphNode(work_e, [(node_a, 0, EdgeType.StartStart)])
    work_f = WorkUnit(id="F", name="Documentation", volume=1.0)
    node_f = GraphNode(work_f, [(node_a, 0, EdgeType.FinishFinish)])

    return WorkGraph.from_nodes([node_a, node_b, node_c, node_d, node_e, node_f])


def export_csv_logic(work_graph: WorkGraph) -> None:
    """Show how CSV dependency rows could be produced.
    Показать, как могут формироваться строки CSV с зависимостями."""

    rows: list[str] = ["child_id,parent_id,type,lag"]
    for node in work_graph.nodes:
        for edge in node.edges_to:
            if edge.start.work_unit.is_service_unit or edge.finish.work_unit.is_service_unit:
                continue
            rows.append(
                f"{edge.finish.id},{edge.start.id},{edge.type.value},{int(edge.lag)}"
            )
    csv_output = "\n".join(rows)
    print("CSV export preview:\n" + csv_output)


def parse_csv_example() -> None:
    """Parse the mini CSV snippet from the documentation.
    Разобрать мини CSV из документации."""

    data = """child_id,parent_id,type,lag\nB,A,FS,3\nC,B,IFS,0\nD,C,IFS,0\nE,A,SS,0\n"""
    reader = DictReader(StringIO(data))
    entries = list(reader)
    print("Parsed CSV rows:")
    for entry in entries:
        print(entry)


def summarize_graph(work_graph: WorkGraph) -> None:
    """Print a summary of edge types and lags for validation.
    Вывести сводку типов связей и лагов для проверки."""

    print("Graph connections summary:")
    for node in work_graph.nodes:
        for edge in node.edges_to:
            if edge.start.work_unit.is_service_unit or edge.finish.work_unit.is_service_unit:
                continue
            print(
                f"{edge.start.id} -> {edge.finish.id}: type={edge.type.value}, lag={edge.lag}"
            )


def main() -> None:
    """Run all connection verification routines.
    Выполнить все проверки связей."""

    work_graph = build_connection_graph()
    summarize_graph(work_graph)
    export_csv_logic(work_graph)
    parse_csv_example()


if __name__ == "__main__":
    main()
