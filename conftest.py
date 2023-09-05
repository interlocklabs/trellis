import pytest
import aiohttp
from trellis.node import Node
from trellis.dag import DAG


class DummyNode(Node):
    def __init__(self, name: str) -> None:
        super().__init__(name)

    async def execute(self) -> dict[str : type]:
        pass


class ReadFromFileTool(Node):
    def __init__(
        self,
        name: str,
        input_s: dict[str, type] = dict,
        output_s: dict[str, type] = {"file_contents": str},
        file_path: str = "data.txt",
        *args,
        **kwargs,
    ) -> None:
        super().__init__(name, input_s, output_s, *args, **kwargs)
        self.file_path = file_path

    async def execute(self) -> dict:
        with open(
            self.execute_args["kwargs"].get("file_path", "tests/data.txt"), "r"
        ) as f:
            self.output = {"file_contents": f.read()}
        return self.output


class CatFactsAPITool(Node):
    def __init__(
        self,
        name: str,
        input_s: dict[str, type] = dict,
        output_s: dict[str, type] = {"cat_information": list[dict[str, str]]},
        limit: int = 1,
        max_length: int = 140,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(name, input_s, output_s, *args, **kwargs)
        self.limit = limit
        self.max_length = max_length

    def set_limit(self, limit: int) -> None:
        self.limit = limit

    def set_max_length(self, max_length: int) -> None:
        self.max_length = max_length

    async def execute(self) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://catfact.ninja/facts?limit={self.execute_args['kwargs'].get('limit', 1)}&max_length={self.execute_args['kwargs'].get('max_length', 140)}"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.output = {"cat_information": data["data"]}
                    return self.output
                else:
                    return {"error": "Unable to fetch cat fact."}


class UselessFactsAPITool(Node):
    def __init__(
        self,
        name: str,
        input_s: dict[str, type] = dict,
        output_s: dict[str, type] = {"useless_information": str},
        *args,
        **kwargs,
    ) -> None:
        super().__init__(name, input_s, output_s, *args, **kwargs)

    async def execute(self) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://uselessfacts.jsph.pl/random.json"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.output = {"useless_information": data["text"]}
                    return self.output
                else:
                    return {"error": "Unable to fetch useless fact."}


class CorporateBSGeneratorAPITool(Node):
    def __init__(
        self,
        name: str,
        input_s: dict[str, type] = dict,
        output_s: dict[str, type] = {"corporate_bs": str},
        *args,
        **kwargs,
    ) -> None:
        super().__init__(name, input_s, output_s, *args, **kwargs)

    async def execute(self) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://corporatebs-generator.sameerkumar.website/"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.output = {"corporate_bs": data["phrase"]}
                    return self.output
                else:
                    return {"error": "Unable to fetch corporate bs."}


class ImgFlipMemeNameAPITool(Node):
    def __init__(
        self,
        name: str,
        input_s: dict[str, type] = dict,
        output_s: dict[str, type] = {"meme_name": str},
        *args,
        **kwargs,
    ) -> None:
        super().__init__(name, input_s, output_s, *args, **kwargs)

    async def execute(self) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.imgflip.com/get_memes") as response:
                if response.status == 200:
                    data = await response.json()
                    self.output = {"meme_name": data["data"]["memes"][0]["name"]}
                    return self.output
                else:
                    return {"error": "Unable to fetch meme name."}


@pytest.fixture
def dag() -> DAG:
    return DAG()


@pytest.fixture
def cat_facts_api_tool() -> Node:
    return CatFactsAPITool("cat_facts_api_tool")


@pytest.fixture
def useless_facts_api_tool() -> Node:
    return UselessFactsAPITool("useless_facts_api_tool")


@pytest.fixture
def corporate_bs_generator_api_tool() -> Node:
    return CorporateBSGeneratorAPITool("corporate_bs_generator_api_tool")


@pytest.fixture
def img_flip_meme_name_api_tool() -> Node:
    return ImgFlipMemeNameAPITool("img_flip_meme_name_api_tool")


@pytest.fixture
def read_from_file_tool() -> Node:
    return ReadFromFileTool("read_from_file_tool")


@pytest.fixture
def dummy_node() -> DummyNode:
    return DummyNode("test")


@pytest.fixture()
def dummy_node_2():
    return DummyNode("test2")


@pytest.fixture()
def dummy_node_3():
    return DummyNode("test3")


@pytest.fixture
def dummy_node_4():
    return DummyNode("test4")


@pytest.fixture
def dummy_node_5():
    return DummyNode("test5")


@pytest.fixture
def dummy_node_6():
    return DummyNode("test6")


@pytest.fixture
def dummy_node_7():
    return DummyNode("test7")


@pytest.fixture
def dummy_node_8():
    return DummyNode("test8")
