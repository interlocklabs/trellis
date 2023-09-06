import logging
from asyncio import iscoroutinefunction
from typing import Callable

from .utils.analyzer import analyzer
from .node import Node


class DAG:
    def __init__(self) -> None:
        self.adj = {}
        self.deps = {}
        self.nodes = {}
        self.logger = logging.getLogger(self.__class__.__name__)

    def set_logger(self, logger: logging.Logger) -> None:
        if not isinstance(logger, logging.Logger):
            raise ValueError(f"Logger {logger} is not a valid logger")
        self.logger = logger

    def is_node(self, node: Node) -> bool:
        return node and isinstance(node, Node)

    def add_node(self, node: Node) -> None:
        if not self.is_node(node):
            self.logger.error(f"{node} is not a valid Node object")
            raise ValueError(f"{node} is not a valid Node object")
        node_id = node.get_id()
        if node_id in self.nodes:
            self.logger.error(f"Node with id {node_id} already exists")
            raise ValueError(f"Node with id {node_id} already exists")
        self.nodes[node_id] = node
        self.adj[node_id] = []
        self.deps[node_id] = []
        self.logger.debug(f"Added node {node} with id {node_id}")

    def remove_node(self, node: Node) -> None:
        if not self.is_node(node):
            self.logger.error(f"{node} is not a valid Node object")
            raise ValueError(f"{node} is not a valid Node object")
        node_id = node.get_id()
        if node_id not in self.nodes:
            self.logger.error(f"Node with id {node_id} does not exist")
            raise KeyError(f"Node with id {node_id} does not exist")
        for _id in self.adj:
            self.adj[_id] = [n for n in self.adj[_id] if n["id"] != node_id]
        for _id in self.deps:
            if node_id in self.deps[_id]:
                self.deps[_id].remove(node_id)
        del self.adj[node_id]
        del self.deps[node_id]
        del self.nodes[node_id]
        self.logger.debug(f"Removed node {node} with id {node_id}")

    def get_node(self, node_id: str) -> Node:
        if not node_id or not isinstance(node_id, str):
            self.logger.error(f"{node_id} is not a valid node id")
            raise ValueError("Please provide a valid node id")
        if node_id not in self.nodes:
            self.logger.error(f"Node with id {node_id} does not exist")
            raise ValueError(f"Node with id {node_id} does not exist")
        return self.nodes[node_id]

    def _is_reachable(self, start: Node, target: Node) -> bool:
        if not self.is_node(start) or not self.is_node(target):
            self.logger.error(f"{target} or {start} is not a valid Node object")
            raise ValueError(f"{target} or {start} is not a valid Node object")
        visited = set()
        stack = [start.get_id()]
        while stack:
            node_id = stack.pop()
            if node_id == target.get_id():
                return True
            if node_id not in visited:
                visited.add(node_id)
                stack.extend([n["id"] for n in self.adj[node_id]])
        return False

    def add_edge(
        self,
        from_node: Node,
        to_node: Node,
        fn: Callable[[dict[str:type]], dict[str:type]] = lambda x: x,
    ) -> None:
        if not self.is_node(from_node) or not self.is_node(to_node):
            self.logger.error(f"{from_node} or {to_node} is not a valid Node object")
            raise ValueError(f"{from_node} or {to_node} is not a valid Node object")
        fnode_id = from_node.get_id()
        tnode_id = to_node.get_id()
        if fnode_id not in self.nodes or tnode_id not in self.nodes:
            self.logger.error(
                f"Cannot add edge either {from_node.get_name()} to {to_node.get_name()} does not exist"
            )
            raise ValueError(
                f"Cannot add edge either {from_node.get_name()} to {to_node.get_name()} does not exist"
            )
        # if we add u -> v and u is reachable from v, then we have a cycle
        if tnode_id == fnode_id or self._is_reachable(to_node, from_node):
            self.logger.error(
                f"Cannot add edge from {from_node.get_name()} to {to_node.get_name()}; cycle detected"
            )
            raise ValueError(
                f"Cannot add edge from {from_node.get_name()} to {to_node.get_name()}; cycle detected"
            )
        self.adj[fnode_id].append({"fn": fn, "id": tnode_id})
        self.deps[tnode_id].append(fnode_id)
        self.logger.debug(
            f"Added edge from {fnode_id} to {tnode_id} with function {fn.__name__}"
        )

    def remove_edge(self, from_node: Node, to_node: Node) -> None:
        if not self.is_node(from_node) or not self.is_node(to_node):
            self.logger.error(f"{from_node} or {to_node} is not a valid Node object")
            raise ValueError(f"{from_node} or {to_node} is not a valid Node object")
        fnode_id = from_node.get_id()
        tnode_id = to_node.get_id()
        if fnode_id not in self.nodes or tnode_id not in self.nodes:
            self.logger.error(
                f"Cannot remove edge either {from_node.get_name()} to {to_node.get_name()} does not exist"
            )
            raise ValueError(
                f"Cannot remove nonexistent edge from {from_node.get_name()} to {to_node.get_name()}"
            )
        # if we add u -> v and u is reachable from v, then we have a cycle
        if tnode_id == fnode_id or tnode_id not in map(
            lambda x: x["id"], self.adj[fnode_id]
        ):
            self.logger.error(
                f"Cannot remove edge from {from_node.get_name()} to {to_node.get_name()}"
            )
            raise ValueError(
                f"Cannot remove nonexistent edge from {from_node.get_name()} to {to_node.get_name()}"
            )
        self.adj[fnode_id] = [n for n in self.adj[fnode_id] if tnode_id != n["id"]]
        self.deps[tnode_id].remove(fnode_id)
        self.logger.debug(f"Removed edge from {fnode_id} to {tnode_id}")

    def _topological_sort(self) -> list[str]:
        # Kahn's algorithm
        # https://en.wikipedia.org/wiki/Topological_sorting#Kahn's_algorithm
        L = []
        S = {n for n in self.nodes if not self.deps[n]}
        deps_copy = self.deps.copy()
        while S:
            n = S.pop()
            L.append(n)
            for m in self.adj[n]:
                deps_copy[m["id"]].remove(n)
                if not deps_copy[m["id"]]:
                    S.add(m["id"])
        if any(deps_copy.values()):
            self.logger.error("Cycle detected")
            raise ValueError("Cycle detected")
        self.logger.debug(f"Topological sort: {L}")
        return L

    def _is_valid_topological_order(self, order: list[str]) -> bool:
        # Check if all nodes are present in the order
        if set(order) != set(self.nodes.keys()):
            return False

        for node_id, edges in self.adj.items():
            for edge in edges:
                # If u comes after v in the list, it's not a valid order
                if order.index(node_id) > order.index(edge["id"]):
                    return False

        return True

    async def execute(
        self,
        init_source_nodes: dict[str:type],
    ) -> dict[str:type]:
        if not isinstance(init_source_nodes, dict):
            self.logger.error(f"{init_source_nodes} is not a valid dict")
            raise ValueError("Please provide a valid dict of source nodes")
        for k, args_kwargs in init_source_nodes.items():
            if k not in self.nodes:
                self.logger.error(f"Node with id {k} does not exist")
                raise ValueError(f"Node with id {k} does not exist")
            if not isinstance(args_kwargs, dict):
                self.logger.error(f"Node {k} input {args_kwargs} is not a valid dict")
                raise ValueError(f"Node {k} input {args_kwargs} is not a valid dict")
        order = self._topological_sort()
        self.logger.info("Executing DAG")
        while order:
            node_id = order.pop(0)
            node = self.nodes[node_id]
            if node.get_status() == "EXECUTING":
                order.append(node_id)
                self.logger.info(
                    f"Node {node_id} is already executing, moving to end of queue"
                )
            else:
                try:
                    a = (
                        init_source_nodes[node_id].get("args", [])
                        if init_source_nodes.get(node_id, {})
                        else (
                            []
                            if not node.execute_args["args"]
                            else node.execute_args["args"]
                        )
                    )
                    k = (
                        init_source_nodes[node_id].get("kwargs", {})
                        if init_source_nodes.get(node_id, {})
                        else (
                            {}
                            if not node.execute_args["kwargs"]
                            else node.execute_args["kwargs"]
                        )
                    )
                    node.set_execute_args(*a, **k)
                    self.logger.info(f"Executing node {node_id}")
                    if iscoroutinefunction(node._pre_hook):
                        await node._pre_hook()
                    else:
                        node._pre_hook()
                    flag = node.validate_input()
                    if flag is False:
                        self.logger.error(
                            f"Node {node_id} input {node.input} is not valid for schema {node._input_s}"
                        )
                        raise ValueError(
                            f"Node {node_id} input {node.input} is not valid for schema {node._input_s}"
                        )
                    if iscoroutinefunction(node.execute):
                        await node.execute()
                    else:
                        node.execute()
                    if iscoroutinefunction(node._post_hook):
                        await node._post_hook()
                    else:
                        node._post_hook()
                    flag = node.validate_output()
                    if flag is False:
                        self.logger.error(
                            f"Node {node_id} output {node.output} is not valid for schema {node._output_s}"
                        )
                        raise ValueError(
                            f"Node {node_id} output {node.output} is not valid for schema {node._output_s}"
                        )
                    self.logger.info(f"Node {node_id} executed successfully")
                    for edge in self.adj[node_id]:
                        self.nodes[edge["id"]].set_input(
                            edge["fn"](node.get_output()), wipe=False
                        )
                    self.logger.info(
                        f"Node {node_id} output propagated to children successfully"
                    )
                except Exception as e:
                    node.set_status("FAILED")
                    self.logger.error(f"Node {node_id} failed: {e}")
                    raise e

        analyzer(
            "dag/execute",
            {
                "nodes": [v.to_dict() for _, v in self.nodes.items()],
                "adj": str(self.adj),
                "deps": str(self.deps),
                "init_source_nodes": init_source_nodes,
            },
        )

        leaves = [self.get_node(n).get_output() for n in self.nodes if not self.adj[n]]
        return leaves
