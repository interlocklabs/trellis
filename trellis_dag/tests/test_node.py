import pytest
from voluptuous import Invalid

from trellis_dag import Node


def test_init(dummy_node: Node) -> None:
    assert dummy_node.get_name() == "test"
    assert dummy_node.get_status() == "PENDING"
    assert dummy_node.get_output() == {}
    assert dummy_node.get_input() == {}
    assert dummy_node.get_id() is not None


def test_validate_input(dummy_node: Node) -> None:
    dummy_node.set_input_s({"a": int, "b": str})
    dummy_node.set_input({"a": 1, "b": "2"})
    assert dummy_node.validate_input()


def test_validate_input_failure(dummy_node: Node) -> None:
    with pytest.raises(ValueError, match="is not a valid dict"):
        dummy_node.set_input(2)
        assert not dummy_node.validate_input()

    dummy_node.set_input_s({"a": int})
    dummy_node.set_input({"a": "1"})
    assert not dummy_node.validate_input()


def test_validate_output(dummy_node: Node) -> None:
    dummy_node.set_output_s({"a": int, "b": str})
    dummy_node.set_output({"a": 1, "b": "2"})
    assert dummy_node.validate_output()


def test_validate_output_failure(dummy_node: Node) -> None:
    with pytest.raises(ValueError, match="is not a valid dict"):
        dummy_node.set_output(3)
        assert not dummy_node.validate_output()

    dummy_node.set_output_s({"a": int})
    dummy_node.set_output({"a": "1"})
    assert not dummy_node.validate_output()


def test_validate_execute_args(dummy_node: Node) -> None:
    dummy_node.set_execute_args(1, 2, 3, a=1, b=2, c=3)
    assert dummy_node.validate_execute_args()


@pytest.mark.asyncio
async def test_pre_hook(dummy_node: Node) -> None:
    dummy_node.set_pre_execute_hook(lambda x: {"result": x})
    dummy_node.set_input_s({"result": {"a": int, "b": int}})
    dummy_node.set_input({"a": 1, "b": 2})
    await dummy_node._pre_hook()
    assert dummy_node.get_input() == {"result": {"a": 1, "b": 2}}
    assert dummy_node.validate_input()
    assert dummy_node.get_status() == "EXECUTING"


def test_pre_hook_failure(dummy_node: Node) -> None:
    with pytest.raises(ValueError, match="is not a callable function"):
        dummy_node.set_pre_execute_hook(4)


@pytest.mark.asyncio
async def test_post_hook(dummy_node: Node) -> None:
    dummy_node.set_post_execute_hook(lambda x: {"result": x})
    dummy_node.set_output_s({"result": {"a": int, "b": int}})
    dummy_node.set_output({"a": 1, "b": 2})
    await dummy_node._post_hook()
    assert dummy_node.get_output() == {"result": {"a": 1, "b": 2}}
    assert dummy_node.validate_output()
    assert dummy_node.get_status() == "SUCCESS"


def test_post_hook_failure(dummy_node: Node) -> None:
    with pytest.raises(ValueError, match="is not a callable function"):
        dummy_node.set_post_execute_hook(4)
