import pytest

from trellis import Node
from trellis import DAG


def test_init(dag: DAG) -> None:
    assert dag.adj == {}
    assert dag.deps == {}
    assert dag.nodes == {}


def test_add_node(dag: DAG, dummy_node: Node) -> None:
    dag.add_node(dummy_node)
    assert dag.nodes[dummy_node.get_id()] == dummy_node
    assert dag.adj[dummy_node.get_id()] == []
    assert dag.deps[dummy_node.get_id()] == []


def test_add_node_twice(dag: DAG, dummy_node: Node) -> None:
    dag.add_node(dummy_node)
    with pytest.raises(ValueError, match="already exists"):
        dag.add_node(dummy_node)


def test_add_bad_node(dag: DAG) -> None:
    with pytest.raises(ValueError, match="not a valid Node object"):
        dag.add_node(None)
    with pytest.raises(ValueError, match="not a valid Node object"):
        dag.add_node("bad node")


def test_remove_node(dag: DAG, dummy_node: Node) -> None:
    dag.add_node(dummy_node)
    dag.remove_node(dummy_node)
    assert dummy_node.get_id() not in dag.nodes
    assert dummy_node.get_id() not in dag.deps
    assert dummy_node.get_id() not in dag.adj


def test_remove_node_with_edge(dag, dummy_node, dummy_node_2) -> None:
    dag.add_node(dummy_node)
    dag.add_node(dummy_node_2)
    dag.add_edge(dummy_node, dummy_node_2)
    dag.remove_node(dummy_node_2)
    assert dummy_node.get_id() in dag.nodes
    assert dummy_node.get_id() in dag.deps
    assert dummy_node.get_id() in dag.adj
    assert dummy_node_2.get_id() not in dag.nodes
    assert dummy_node_2.get_id() not in dag.deps
    assert dummy_node_2.get_id() not in dag.adj


def test_remove_nonexistent_node(dag: DAG, dummy_node: Node) -> None:
    with pytest.raises(KeyError, match="does not exist"):
        dag.remove_node(dummy_node)


def test_remove_bad_node(dag: DAG) -> None:
    with pytest.raises(ValueError, match="not a valid Node object"):
        dag.remove_node(None)
    with pytest.raises(ValueError, match="not a valid Node object"):
        dag.remove_node("bad node")


def test_get_node(dag: DAG, dummy_node: Node) -> None:
    dag.add_node(dummy_node)
    assert dag.get_node(dummy_node.get_id()) == dummy_node


def test_get_nonexistent_node(dag: DAG, dummy_node: Node) -> None:
    with pytest.raises(ValueError, match="does not exist"):
        dag.get_node(dummy_node.get_id())


def test_get_bad_node(dag: DAG) -> None:
    with pytest.raises(ValueError, match="Please provide a valid node id"):
        dag.get_node(None)
    with pytest.raises(ValueError, match="does not exist"):
        dag.get_node("bad node")


def test_add_edge(dag, dummy_node, dummy_node_2) -> None:
    dag.add_node(dummy_node)
    dag.add_node(dummy_node_2)
    dag.add_edge(dummy_node, dummy_node_2)
    assert dummy_node_2.get_id() == dag.adj[dummy_node.get_id()][-1].get("id", None)
    assert dummy_node.get_id() in dag.deps[dummy_node_2.get_id()]


def test_add_edge_bad_node(dag, dummy_node, dummy_node_2) -> None:
    dag.add_node(dummy_node)
    dag.add_node(dummy_node_2)
    with pytest.raises(ValueError, match="not a valid Node object"):
        dag.add_edge(dummy_node, None)
    with pytest.raises(ValueError, match="not a valid Node object"):
        dag.add_edge(None, dummy_node)
    with pytest.raises(ValueError, match="is not a valid Node object"):
        dag.add_edge(dummy_node, "cool node")
    with pytest.raises(ValueError, match="is not a valid Node object"):
        dag.add_edge("cool node", dummy_node_2)
    with pytest.raises(ValueError, match="not a valid Node object"):
        dag.add_edge(None, None)


def test_add_edge_nonexistent_node(dag, dummy_node, dummy_node_2) -> None:
    with pytest.raises(ValueError, match="does not exist"):
        dag.add_edge(dummy_node, dummy_node_2)
    dag.add_node(dummy_node)
    with pytest.raises(ValueError, match="does not exist"):
        dag.add_edge(dummy_node, dummy_node_2)


def test_add_edge_self_loop(dag: DAG, dummy_node: Node) -> None:
    dag.add_node(dummy_node)
    with pytest.raises(ValueError, match="cycle detected"):
        dag.add_edge(dummy_node, dummy_node)


# todo add more cases for cycle tests?
def test_add_edge_cycle(
    dag: DAG, dummy_node: Node, dummy_node_2: Node, dummy_node_3: Node
) -> None:
    dag.add_node(dummy_node)
    dag.add_node(dummy_node_2)
    dag.add_node(dummy_node_3)
    dag.add_edge(dummy_node, dummy_node_2)
    dag.add_edge(dummy_node_2, dummy_node_3)
    with pytest.raises(ValueError, match="cycle detected"):
        dag.add_edge(dummy_node_3, dummy_node)


def test_remove_edge(dag, dummy_node, dummy_node_2) -> None:
    dag.add_node(dummy_node)
    dag.add_node(dummy_node_2)
    dag.add_edge(dummy_node, dummy_node_2)
    dag.remove_edge(dummy_node, dummy_node_2)
    assert dummy_node_2.get_id() not in dag.adj[dummy_node.get_id()]
    assert dummy_node.get_id() not in dag.deps[dummy_node_2.get_id()]


def test_remove_edge_bad_node(dag, dummy_node, dummy_node_2) -> None:
    dag.add_node(dummy_node)
    dag.add_node(dummy_node_2)
    with pytest.raises(ValueError, match="not a valid Node object"):
        dag.remove_edge(dummy_node, None)
    with pytest.raises(ValueError, match="not a valid Node object"):
        dag.remove_edge(None, dummy_node)
    with pytest.raises(ValueError, match="is not a valid Node object"):
        dag.remove_edge(dummy_node, "cool node")
    with pytest.raises(ValueError, match="is not a valid Node object"):
        dag.remove_edge("cool node", dummy_node_2)
    with pytest.raises(ValueError, match="not a valid Node object"):
        dag.remove_edge(None, None)


def test_remove_edge_nonexistent_node(dag, dummy_node, dummy_node_2) -> None:
    with pytest.raises(ValueError, match="Cannot remove nonexistent edge"):
        dag.remove_edge(dummy_node, dummy_node_2)
    dag.add_node(dummy_node)
    with pytest.raises(ValueError, match="Cannot remove nonexistent edge"):
        dag.remove_edge(dummy_node, dummy_node_2)


def test_remove_edge_self_loop(dag: DAG, dummy_node: Node) -> None:
    dag.add_node(dummy_node)
    with pytest.raises(ValueError, match="Cannot remove nonexistent edge"):
        dag.remove_edge(dummy_node, dummy_node)


def test_remove_edge_cycle(
    dag: DAG, dummy_node: Node, dummy_node_2: Node, dummy_node_3: Node
) -> None:
    dag.add_node(dummy_node)
    dag.add_node(dummy_node_2)
    dag.add_node(dummy_node_3)
    dag.add_edge(dummy_node, dummy_node_2)
    dag.add_edge(dummy_node_2, dummy_node_3)
    with pytest.raises(ValueError, match="Cannot remove nonexistent edge"):
        dag.remove_edge(dummy_node_3, dummy_node)


# Simple test with clear order
# A -> B -> C -> D
def test_topological_sort_simple(
    dag: DAG,
    dummy_node: Node,
    dummy_node_2: Node,
    dummy_node_3: Node,
    dummy_node_4: Node,
) -> None:
    dag.add_node(dummy_node)
    dag.add_node(dummy_node_2)
    dag.add_node(dummy_node_3)
    dag.add_node(dummy_node_4)
    dag.add_edge(dummy_node, dummy_node_2)
    dag.add_edge(dummy_node_2, dummy_node_3)
    dag.add_edge(dummy_node_3, dummy_node_4)
    assert dag._is_valid_topological_order(dag._topological_sort())


# Small DAG with multiple orders
# A -> B -> D -> F
# |         ^
# v         |
# C ------> E
def test_topological_sort_small_multi_order(
    dag: DAG,
    dummy_node: Node,
    dummy_node_2: Node,
    dummy_node_3: Node,
    dummy_node_4: Node,
    dummy_node_5: Node,
    dummy_node_6: Node,
) -> None:
    dag.add_node(dummy_node)
    dag.add_node(dummy_node_2)
    dag.add_node(dummy_node_3)
    dag.add_node(dummy_node_4)
    dag.add_node(dummy_node_5)
    dag.add_node(dummy_node_6)
    dag.add_edge(dummy_node, dummy_node_2)
    dag.add_edge(dummy_node, dummy_node_3)
    dag.add_edge(dummy_node_2, dummy_node_4)
    dag.add_edge(dummy_node_3, dummy_node_5)
    dag.add_edge(dummy_node_4, dummy_node_6)
    dag.add_edge(dummy_node_5, dummy_node_4)
    assert dag._is_valid_topological_order(dag._topological_sort())


# Empty DAG
#
def test_topological_sort_empty(dag: DAG) -> None:
    assert dag._is_valid_topological_order(dag._topological_sort())


# DAG with one Node, no edges
# A
def test_topological_sort_one_node(dag: DAG, dummy_node: Node) -> None:
    dag.add_node(dummy_node)
    assert dag._is_valid_topological_order(dag._topological_sort())


# DAG with multiple Nodes, no edges
# A    B


# C    D
def test_topological_sort_four_nodes(
    dag: DAG,
    dummy_node: Node,
    dummy_node_2: Node,
    dummy_node_3: Node,
    dummy_node_4: Node,
) -> None:
    dag.add_node(dummy_node)
    dag.add_node(dummy_node_2)
    dag.add_node(dummy_node_3)
    dag.add_node(dummy_node_4)
    assert dag._is_valid_topological_order(dag._topological_sort())


# DAG with Nodes with multiple incoming edges
# A
# |
# v
# B <- C
# ^
# |
# D
def test_topological_sort_multiple_incoming_edges(
    dag: DAG,
    dummy_node: Node,
    dummy_node_2: Node,
    dummy_node_3: Node,
    dummy_node_4: Node,
) -> None:
    dag.add_node(dummy_node)
    dag.add_node(dummy_node_2)
    dag.add_node(dummy_node_3)
    dag.add_node(dummy_node_4)
    dag.add_edge(dummy_node, dummy_node_2)
    dag.add_edge(dummy_node_3, dummy_node_2)
    dag.add_edge(dummy_node_4, dummy_node_2)
    assert dag._is_valid_topological_order(dag._topological_sort())


# DAG with Nodes with multiple outgoing edges
# A
# ^
# |
# B -> C
# |
# v
# D
def test_topological_sort_multiple_outgoing_edges(
    dag: DAG,
    dummy_node: Node,
    dummy_node_2: Node,
    dummy_node_3: Node,
    dummy_node_4: Node,
) -> None:
    dag.add_node(dummy_node)
    dag.add_node(dummy_node_2)
    dag.add_node(dummy_node_3)
    dag.add_node(dummy_node_4)
    dag.add_edge(dummy_node_2, dummy_node)
    dag.add_edge(dummy_node_2, dummy_node_3)
    dag.add_edge(dummy_node_2, dummy_node_4)
    assert dag._is_valid_topological_order(dag._topological_sort())


# DAG with multiple Nodes with multiple incoming and outgoing edges
#   A
#  / \
# v   v
# B   C
# |   | \
# v   v  v
# D   E  F
#  \ /   |
#   v    v
#   G -> H
def test_topological_sort_multiple_incoming_outgoing(
    dag: DAG,
    dummy_node: Node,
    dummy_node_2: Node,
    dummy_node_3: Node,
    dummy_node_4: Node,
    dummy_node_5: Node,
    dummy_node_6: Node,
    dummy_node_7: Node,
    dummy_node_8: Node,
) -> None:
    dag.add_node(dummy_node)
    dag.add_node(dummy_node_2)
    dag.add_node(dummy_node_3)
    dag.add_node(dummy_node_4)
    dag.add_node(dummy_node_5)
    dag.add_node(dummy_node_6)
    dag.add_node(dummy_node_7)
    dag.add_node(dummy_node_8)
    dag.add_edge(dummy_node, dummy_node_2)
    dag.add_edge(dummy_node, dummy_node_3)
    dag.add_edge(dummy_node_2, dummy_node_4)
    dag.add_edge(dummy_node_3, dummy_node_5)
    dag.add_edge(dummy_node_3, dummy_node_6)
    dag.add_edge(dummy_node_4, dummy_node_7)
    dag.add_edge(dummy_node_5, dummy_node_7)
    dag.add_edge(dummy_node_6, dummy_node_8)
    dag.add_edge(dummy_node_7, dummy_node_8)
    assert dag._is_valid_topological_order(dag._topological_sort())
