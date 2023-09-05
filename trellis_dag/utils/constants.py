import openai
from os import getenv

max_retries = getenv("DEFAULT_MAX_RETRIES")
retry_delay = getenv("DEFAULT_RETRY_DELAY")
rate_limit_delay = getenv("DEFAULT_RATE_LIMIT_DELAY")

DEFAULT_MAX_RETRIES = int(max_retries) if max_retries else 3
DEFAULT_RETRY_DELAY: int = int(retry_delay) if retry_delay else 5
DEFAULT_RATE_LIMIT_DELAY: int = int(rate_limit_delay) if rate_limit_delay else 60


OPENAI_MODELS = [
    "gpt-4",
    "gpt-4-0613",
    "gpt-4-32k",
    "gpt-4-32k-0613",
    "gpt-3.5-turbo",
    "gpt-3.5-turbo-0613",
    "gpt-3.5-turbo-16k",
    "gpt-3.5-turbo-16k-0613",
]
OPENAI_ARGS = {
    "functions": [],
    "function_call": "",
    "temperature": 1,
    "top_p": 1,
    "n": 1,
    "stream": False,
    "stop": None,
    "max_tokens": float("inf"),
    "presence_penalty": 0,
    "frequency_penalty": 0,
    "logit_bias": {},
    "user": "",
}
OPENAI_RESPONSE_SCHEMA = {
    "id": str,
    "object": str,
    "created": int,
    "model": str,
    "choices": [
        {
            "index": int,
            "message": {
                "role": str,
                "content": str,
            },
            "finish_reason": str,
        }
    ],
    "usage": {
        "prompt_tokens": int,
        "completion_tokens": int,
        "total_tokens": int,
    },
}
EXCEPTIONS_TO_TEST = [
    openai.error.InvalidRequestError("Mocked invalid request", "mocked_param"),
    openai.error.AuthenticationError("Mocked authentication error", "mocked_param"),
    openai.error.APIConnectionError("Mocked API connection error", "mocked_param"),
    openai.error.APIError("Mocked API error", "mocked_param"),
    openai.error.RateLimitError("Mocked rate limit error", "mocked_param"),
    openai.error.Timeout("Mocked timeout", "mocked_param"),
    openai.error.ServiceUnavailableError(
        "Mocked service unavailable error", "mocked_param"
    ),
]
