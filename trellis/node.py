from voluptuous import Schema, Invalid
from asyncio import iscoroutinefunction
from typing import Callable
from abc import ABC, abstractmethod
from uuid import uuid4
from .utils.status import Status

import logging


class Node(ABC):
    def __init__(
        self,
        name: str,
        input_s: dict[str:type] = dict,
        output_s: dict[str:type] = dict,
        *args,
        **kwargs,
    ) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.name = name
        self._id = uuid4().hex
        self.set_status("PENDING")
        self.input = {}
        self.set_execute_args(*args, **kwargs)
        self.output = {}
        self.set_input_s(input_s)
        self.__execute_args_s = Schema({"args": list, "kwargs": dict})
        self.set_output_s(output_s)
        self.pre_execute_hook = lambda _: self.input
        self.post_execute_hook = lambda _: self.output

    def __repr__(self) -> str:
        return f"Node(name={self.name}, id={self._id}, status={self._status})"

    def set_logger(self, logger: logging.Logger) -> None:
        if not isinstance(logger, logging.Logger):
            raise ValueError(f"Logger {logger} is not a valid logger")
        self.logger = logger

    # getters
    def get_status(self) -> str:
        return self._status.name

    def get_id(self) -> str:
        return self._id

    def get_name(self) -> str:
        return self.name

    def get_input(self) -> dict[str:type]:
        return self.input

    def get_output(self) -> dict[str:type]:
        return self.output

    def get_execute_args(self) -> dict[str:type]:
        return self.execute_args

    def safe_get_execute_arg(self, key: str, default: type = None) -> type:
        return (
            self.input.get(key, default)
            if key in self.input
            else self.execute_args["kwargs"].get(key, default)
        )

    # setters
    def set_status(self, status: str) -> None:
        if not hasattr(Status, status):
            self.logger.error(f"Status {status} is not a valid Status")
            raise ValueError(f"Status {status} is not a valid Status")
        self._status = Status[status]
        self.logger.debug(f"Node {self._id} status set to {self._status.name}")

    def set_input(self, input: dict[str:type], wipe=True) -> None:
        if not isinstance(input, dict):
            self.logger.error(f"Input {input} is not a valid dict")
            raise ValueError(f"Input {input} is not a valid dict")
        if wipe:
            self.input = input
            self.logger.debug(f"Node {self._id} input set to {input}")
        else:
            self.input.update(input)
            self.logger.debug(f"Node {self._id} input updated with {input}")

    def set_output(self, output: dict[str:type], wipe=True) -> None:
        if not isinstance(output, dict):
            self.logger.error(f"Output {output} is not a valid dict")
            raise ValueError(f"Output {output} is not a valid dict")
        if wipe:
            self.output = output
            self.logger.debug(f"Node {self._id} output set to {output}")
        else:
            self.output.update(output)
            self.logger.debug(f"Node {self._id} output updated with {output}")

    def set_execute_args(self, *args: list[type], **kwargs: dict[str:type]) -> None:
        res = {"args": [], "kwargs": {}}
        if args:
            res["args"] = list(args)
            self.logger.debug(f"Node {self._id} args set to {res}")
        if kwargs:
            res["kwargs"] = kwargs
            self.logger.debug(f"Node {self._id} kwargs set to {res}")
        self.execute_args = res

    def set_input_s(self, input_s: dict[str:type]) -> None:
        if isinstance(input_s, dict) or input_s is dict:
            self._input_s = Schema(input_s)
            self.logger.debug(f"Node {self._id} input schema set to {input_s}")
        else:
            self.logger.error(f"Input Schema {input_s} is not a valid dict")
            raise ValueError(f"Input Schema {input_s} is not a valid dict")

    def set_output_s(self, output_s: dict[str:type]) -> None:
        if isinstance(output_s, dict) or output_s is dict:
            self._output_s = Schema(output_s)
            self.logger.debug(f"Node {self._id} output schema set to {output_s}")
        else:
            self.logger.error(f"Output Schema {output_s} is not a valid dict")
            raise ValueError(f"Output Schema {output_s} is not a valid dict")

    def set_pre_execute_hook(
        self, hook: Callable[[dict[str:type]], dict[str:type]]
    ) -> None:
        if not callable(hook):
            self.logger.error(f"Pre execute hook {hook} is not a callable function")
            raise ValueError(f"Pre execute hook {hook} is not a callable function")
        self.pre_execute_hook = hook
        self.logger.debug(f"Node {self._id} pre execute hook set to {hook.__name__}")

    def set_post_execute_hook(
        self, hook: Callable[[dict[str:type]], dict[str:type]]
    ) -> None:
        if not callable(hook):
            self.logger.error(f"Post execute hook {hook} is not a callable function")
            raise ValueError(f"Post execute hook {hook} is not a callable function")
        self.post_execute_hook = hook
        self.logger.debug(f"Node {self._id} post execute hook set to {hook.__name__}")

    # validators
    def validate_input(self) -> bool:
        try:
            self.logger.debug(f"Node {self._id} validating input {self.input}")
            return self._input_s(self.input)
        except Invalid:
            self.logger.error(f"Node {self._id} input {self.input} is not valid")
            return False

    def validate_output(self) -> bool:
        try:
            self.logger.debug(f"Node {self._id} validating output {self.output}")
            return self._output_s(self.output)
        except Invalid:
            self.logger.error(f"Node {self._id} output {self.output} is not valid")
            return False

    def validate_execute_args(self) -> bool:
        try:
            self.logger.debug(
                f"Node {self._id} validating execute args {self.execute_args}"
            )
            return self.__execute_args_s(self.execute_args)
        except Invalid:
            self.logger.error(
                f"Node {self._id} execute args {self.execute_args} is not valid"
            )
            return False

    # hooks
    async def _pre_hook(self) -> None:
        self.set_status("EXECUTING")
        if iscoroutinefunction(self.pre_execute_hook):
            self.input = await self.pre_execute_hook(self.input)
            self.logger.debug(f"Node {self._id} executing async pre execute hook")
        else:
            self.input = self.pre_execute_hook(self.input)
            self.logger.debug(f"Node {self._id} executing pre execute hook")

    async def _post_hook(self) -> None:
        self.set_status("SUCCESS")
        if iscoroutinefunction(self.post_execute_hook):
            self.output = await self.post_execute_hook(self.output)
            self.logger.debug(f"Node {self._id} executing async post execute hook")
        else:
            self.output = self.post_execute_hook(self.output)
            self.logger.debug(f"Node {self._id} executing post execute hook")

    @abstractmethod
    async def execute(self) -> None:
        pass
