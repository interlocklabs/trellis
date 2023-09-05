import pytest
import openai

from trellis_dag.utils.constants import OPENAI_RESPONSE_SCHEMA, EXCEPTIONS_TO_TEST
from trellis_dag import LLM


@pytest.fixture
def car_messages() -> list[dict]:
    messages = []
    messages.append({"role": "system", "content": "You are a helpful auto mechanic."})
    messages.append({"role": "user", "content": "Hello my {car} is broken."})
    return messages


@pytest.fixture
def llm() -> LLM:
    return LLM(
        name="test_llm",
        model="gpt-3.5-turbo",
        max_retries=2,
        retry_delay=3,
        rate_limit_delay=4,
    )


def test_init(llm) -> None:
    llm.set_max_retries(4)
    llm.set_retry_delay(6)
    llm.set_rate_limit_delay(90)
    llm.set_model("gpt-4")
    assert llm.get_name() == "test_llm"
    assert llm.get_status() == "PENDING"
    assert llm.get_input() == {}
    assert llm.get_output() == {}
    assert llm.get_id() is not None
    assert llm.get_model() == "gpt-4"
    assert llm.get_max_retries() == 4
    assert llm.get_retry_delay() == 6
    assert llm.get_rate_limit_delay() == 90


def test_set_model(llm) -> None:
    llm.set_model("gpt-4")
    assert llm.get_model() == "gpt-4"


def test_set_model_failure(llm) -> None:
    with pytest.raises(ValueError, match="is not a valid OpenAI model"):
        llm.set_model("gpt-5")


def test_set_max_retries(llm) -> None:
    llm.set_max_retries(4)
    assert llm.get_max_retries() == 4


def test_set_max_retries_failure(llm) -> None:
    with pytest.raises(ValueError, match="is not a valid int"):
        llm.set_max_retries("4")

    with pytest.raises(ValueError, match="is not a valid int"):
        llm.set_max_retries(-1)


def test_set_retry_delay(llm) -> None:
    llm.set_retry_delay(4)
    assert llm.get_retry_delay() == 4


def test_set_retry_delay_failure(llm) -> None:
    with pytest.raises(ValueError, match="is not a valid int"):
        llm.set_retry_delay("4")

    with pytest.raises(ValueError, match="is not a valid int"):
        llm.set_retry_delay(-1)


def test_set_rate_limit_delay(llm) -> None:
    llm.set_rate_limit_delay(4)
    assert llm.get_rate_limit_delay() == 4


def test_set_rate_limit_delay_failure(llm) -> None:
    with pytest.raises(ValueError, match="is not a valid int"):
        llm.set_rate_limit_delay("4")

    with pytest.raises(ValueError, match="is not a valid int"):
        llm.set_rate_limit_delay(-1)


def test_set_messages(llm, car_messages) -> None:
    llm.set_messages(car_messages)
    assert llm.get_messages() == car_messages


def test_set_messages_failure(llm) -> None:
    with pytest.raises(ValueError, match="is not a valid list"):
        llm.set_messages("car_messages")

    with pytest.raises(ValueError, match="is not a valid OpenAI message"):
        llm.set_messages([{"role": "system"}])

    with pytest.raises(ValueError, match="is not a valid OpenAI message"):
        llm.set_messages([{"role": "system", "content": 1}])


@pytest.mark.asyncio
async def test_paid_execute(llm, car_messages) -> None:
    llm.set_input({"car": "Tesla"})
    llm.set_messages(car_messages)
    llm.set_output_s(OPENAI_RESPONSE_SCHEMA)
    await llm.execute()
    assert llm.validate_output()


@pytest.mark.asyncio
@pytest.mark.parametrize("mocked_exception", EXCEPTIONS_TO_TEST)
async def test_openai_errors(llm, car_messages, mocker, mocked_exception):
    mocker.patch.object(openai.ChatCompletion, "create", side_effect=mocked_exception)

    llm.set_input({"car": "Tesla"})
    llm.set_messages(car_messages)
    llm.set_output_s(OPENAI_RESPONSE_SCHEMA)

    with pytest.raises(type(mocked_exception)):
        await llm.execute()
