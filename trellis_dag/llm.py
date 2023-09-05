import openai
import os
import asyncio
from voluptuous import Schema, Invalid, Required, ALLOW_EXTRA

from . import analyzer
from .node import Node
from .utils.constants import (
    DEFAULT_MAX_RETRIES,
    DEFAULT_RETRY_DELAY,
    DEFAULT_RATE_LIMIT_DELAY,
    OPENAI_MODELS,
    OPENAI_ARGS,
    OPENAI_RESPONSE_SCHEMA,
)

openai.api_key = os.getenv("OPENAI_API_KEY")


class LLM(Node):
    def __init__(
        self,
        name: str,
        input_s: dict[str:type] = dict,
        output_s: dict[str:type] = OPENAI_RESPONSE_SCHEMA,
        messages: list[dict] = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"},
        ],
        model: str = "gpt-3.5-turbo",
        max_retries: int = DEFAULT_MAX_RETRIES,
        retry_delay: int = DEFAULT_RETRY_DELAY,
        rate_limit_delay: int = DEFAULT_RATE_LIMIT_DELAY,
        *args: list,
        **kwargs: dict,
    ) -> None:
        super().__init__(name, input_s, output_s, *args, **kwargs)
        # manually reset to allow extra keys, idk what the full OpenAI response schema can have
        self._output_s = Schema(output_s, extra=ALLOW_EXTRA)
        if model in OPENAI_MODELS:
            self.model = model
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.rate_limit_delay = rate_limit_delay
        self.messages = messages

    def get_model(self) -> str:
        return self.model

    def get_messages(self) -> list[dict]:
        return self.messages

    def get_max_retries(self) -> int:
        return self.max_retries

    def get_retry_delay(self) -> int:
        return self.retry_delay

    def get_rate_limit_delay(self) -> int:
        return self.rate_limit_delay

    def set_model(self, model: str) -> None:
        if model in OPENAI_MODELS:
            self.model = model
            self.logger.debug(f"Set model to {model}")
        else:
            self.logger.error(f"Model {model} is not a valid OpenAI model")
            raise ValueError(f"Model {model} is not a valid OpenAI model")

    def set_messages(self, messages: list[dict]) -> None:
        if not isinstance(messages, list):
            self.logger.error(f"Messages {messages} is not a valid list")
            raise ValueError(f"Messages {messages} is not a valid list")
        for msg in messages:
            try:
                Schema({Required("role"): str, Required("content"): str})(msg)
            except Invalid as e:
                self.logger.error(f"Message {msg} is not a valid OpenAI message: {e}")
                raise ValueError(f"Message {msg} is not a valid OpenAI message: {e}")
        self.messages = messages
        self.logger.debug(f"Set messages to {messages}")

    def set_max_retries(self, max_retries: int) -> None:
        if not isinstance(max_retries, int) or max_retries < 0:
            self.logger.error(f"Max retries {max_retries} is not a valid int")
            raise ValueError(f"Max retries {max_retries} is not a valid int")
        self.max_retries = max_retries
        self.logger.debug(f"Set max retries to {max_retries}")

    def set_retry_delay(self, retry_delay: int) -> None:
        if not isinstance(retry_delay, int) or retry_delay < 0:
            self.logger.error(f"Retry delay {retry_delay} is not a valid int")
            raise ValueError(f"Retry delay {retry_delay} is not a valid int")
        self.retry_delay = retry_delay
        self.logger.debug(f"Set retry delay to {retry_delay}")

    def set_rate_limit_delay(self, rate_limit_delay: int) -> None:
        if not isinstance(rate_limit_delay, int) or rate_limit_delay < 0:
            self.logger.error(f"Rate limit delay {rate_limit_delay} is not a valid int")
            raise ValueError(f"Rate limit delay {rate_limit_delay} is not a valid int")
        self.rate_limit_delay = rate_limit_delay
        self.logger.debug(f"Set rate limit delay to {rate_limit_delay}")

    async def execute(self) -> dict:
        optional_params = {
            k: v
            for k, v in super().get_execute_args()["kwargs"].items()
            if k in OPENAI_ARGS and v != OPENAI_ARGS[k]
        }

        msgs_template = self.messages.copy()

        # handle filling in variables
        if self.input:
            for msg in msgs_template:
                try:
                    msg["content"] = msg["content"].format(**self.input)
                except KeyError:
                    pass

        retries = 0

        while retries < self.max_retries:
            try:
                response = openai.ChatCompletion.create(
                    model=self.model, messages=self.messages, **optional_params
                )
                self.set_output(response)
                analyzer(
                    "llm/chat_completion",
                    {
                        "model": self.model,
                        "messages": self.messages,
                        "response": response,
                        "input": self.input,
                        "optional_params": optional_params,
                    },
                )
                return response.to_dict()
            except Exception as e:
                if isinstance(e, openai.error.InvalidRequestError):
                    self.logger.error("Invalid request to OpenAI API")
                    raise e
                elif isinstance(e, openai.error.AuthenticationError):
                    self.logger.error("Failed to authenticate with OpenAI API")
                    self.logger.error(
                        "Please make sure your key is set as an environment variable. Run 'export OPENAI_API_KEY=your_key_here' to set your key."
                    )
                    raise e
                elif isinstance(e, openai.error.APIConnectionError):
                    self.logger.error(f"Failed to connect to OpenAI API: {e}")
                    if retries + 1 < self.max_retries:
                        retries += 1
                        self.logger.error(f"Retrying in {self.retry_delay} seconds...")
                        await asyncio.sleep(self.retry_delay)
                    else:
                        self.logger.error(
                            f"Method failed after {self.max_retries} retries"
                        )
                        raise e
                elif isinstance(e, openai.error.APIError):
                    self.logger.error(f"OpenAI API returned an API Error: {e}")
                    if retries + 1 < self.max_retries:
                        retries += 1
                        self.logger.error(f"Retrying in {self.retry_delay} seconds...")
                        await asyncio.sleep(self.retry_delay)
                    else:
                        self.logger.error(
                            f"Method failed after {self.max_retries} retries"
                        )
                        raise e
                elif isinstance(e, openai.error.RateLimitError):
                    self.logger.error(f"OpenAI API request exceeded rate limit: {e}")
                    if retries + 1 < self.max_retries:
                        retries += 1
                        self.logger.error(
                            f"Retrying in {self.rate_limit_delay} seconds..."
                        )
                        await asyncio.sleep(self.rate_limit_delay)
                    else:
                        self.logger.error(
                            f"Method failed after {self.max_retries} retries"
                        )
                        raise e
                elif isinstance(e, openai.error.Timeout):
                    self.logger.error(f"OpenAI API request timed out: {e}")
                    if retries + 1 < self.max_retries:
                        retries += 1
                        self.logger.error(f"Retrying in {self.retry_delay} seconds...")
                        await asyncio.sleep(self.retry_delay)
                    else:
                        self.logger.error(
                            f"Method failed after {self.max_retries} retries"
                        )
                        raise e
                elif isinstance(e, openai.error.ServiceUnavailableError):
                    self.logger.error(
                        f"OpenAI API returned a Service Unavailable Error: {e}"
                    )
                    if retries + 1 < self.max_retries:
                        retries += 1
                        self.logger.error(f"Retrying in {self.retry_delay} seconds...")
                        await asyncio.sleep(self.retry_delay)
                    else:
                        self.logger.error(
                            f"Method failed after {self.max_retries} retries"
                        )
                        raise e
