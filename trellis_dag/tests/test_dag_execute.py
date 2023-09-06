import pytest

from trellis_dag import DAG
from trellis_dag import Node
from trellis_dag import LLM


@pytest.mark.asyncio
async def test_CatFactsAPITool(cat_facts_api_tool) -> None:
    assert cat_facts_api_tool.get_name() == "cat_facts_api_tool"
    assert cat_facts_api_tool.get_status() == "PENDING"
    assert cat_facts_api_tool.get_id() is not None
    assert cat_facts_api_tool.get_input() == {}
    assert cat_facts_api_tool.get_output() == {}

    cat_facts_api_tool.set_execute_args(limit=1, max_length=140)
    await cat_facts_api_tool._pre_hook()
    cat_facts_api_tool.validate_input()
    await cat_facts_api_tool.execute()
    await cat_facts_api_tool._post_hook()

    assert cat_facts_api_tool.get_status() == "SUCCESS"
    assert cat_facts_api_tool.validate_output()


@pytest.mark.asyncio
async def test_ReadFromFileTool(read_from_file_tool) -> None:
    assert read_from_file_tool.get_name() == "read_from_file_tool"
    assert read_from_file_tool.get_status() == "PENDING"
    assert read_from_file_tool.get_id() is not None
    assert read_from_file_tool.get_input() == {}
    assert read_from_file_tool.get_output() == {}

    read_from_file_tool.set_execute_args(file_path="trellis_dag/tests/data.txt")
    await read_from_file_tool._pre_hook()
    read_from_file_tool.validate_input()
    await read_from_file_tool.execute()
    await read_from_file_tool._post_hook()
    read_from_file_tool.validate_output()

    assert read_from_file_tool.get_status() == "SUCCESS"
    assert read_from_file_tool.validate_output()


@pytest.mark.asyncio
async def test_UselessFactsAPITool(useless_facts_api_tool) -> None:
    assert useless_facts_api_tool.get_name() == "useless_facts_api_tool"
    assert useless_facts_api_tool.get_status() == "PENDING"
    assert useless_facts_api_tool.get_id() is not None
    assert useless_facts_api_tool.get_input() == {}
    assert useless_facts_api_tool.get_output() == {}

    await useless_facts_api_tool._pre_hook()
    useless_facts_api_tool.validate_input()
    await useless_facts_api_tool.execute()
    await useless_facts_api_tool._post_hook()
    useless_facts_api_tool.validate_output()

    assert useless_facts_api_tool.get_status() == "SUCCESS"
    assert useless_facts_api_tool.validate_output()


@pytest.mark.asyncio
async def test_CorporateBSGeneratorAPITool(corporate_bs_generator_api_tool) -> None:
    assert (
        corporate_bs_generator_api_tool.get_name() == "corporate_bs_generator_api_tool"
    )
    assert corporate_bs_generator_api_tool.get_status() == "PENDING"
    assert corporate_bs_generator_api_tool.get_id() is not None
    assert corporate_bs_generator_api_tool.get_input() == {}
    assert corporate_bs_generator_api_tool.get_output() == {}

    await corporate_bs_generator_api_tool._pre_hook()
    corporate_bs_generator_api_tool.validate_input()
    await corporate_bs_generator_api_tool.execute()
    await corporate_bs_generator_api_tool._post_hook()
    corporate_bs_generator_api_tool.validate_output()

    assert corporate_bs_generator_api_tool.get_status() == "SUCCESS"
    assert corporate_bs_generator_api_tool.validate_output()


@pytest.mark.asyncio
async def test_ImgFlipMemeNameAPITool(img_flip_meme_name_api_tool) -> None:
    assert img_flip_meme_name_api_tool.get_name() == "img_flip_meme_name_api_tool"
    assert img_flip_meme_name_api_tool.get_status() == "PENDING"
    assert img_flip_meme_name_api_tool.get_id() is not None
    assert img_flip_meme_name_api_tool.get_input() == {}
    assert img_flip_meme_name_api_tool.get_output() == {}

    await img_flip_meme_name_api_tool._pre_hook()
    img_flip_meme_name_api_tool.validate_input()
    await img_flip_meme_name_api_tool.execute()
    await img_flip_meme_name_api_tool._post_hook()
    img_flip_meme_name_api_tool.validate_output()

    assert img_flip_meme_name_api_tool.get_status() == "SUCCESS"
    assert img_flip_meme_name_api_tool.validate_output()


@pytest.mark.asyncio
async def test_execute_bad_init_source(
    dag: DAG, dummy_node: Node, dummy_node_2: Node
) -> None:
    dag.add_node(dummy_node_2)
    id = dummy_node.get_id()
    init = {id: {"key": "value"}}
    with pytest.raises(ValueError, match=f"Node with id {id} does not exist"):
        await dag.execute(init)
    with pytest.raises(ValueError, match="is not a valid dict"):
        await dag.execute({dummy_node_2.get_id(): dummy_node})


# Simple test with clear order
# A -> B -> C -> D
# A; Read location data from file
# B; Generate false weather for each location using LLM
# C; Generate travel itinerary using weather and location data using LLM
# D; Write invite to vacation based on itinerary using LLM
@pytest.mark.asyncio
async def test_execute_simple(
    dag: DAG,
    read_from_file_tool: Node,
) -> None:
    messages_1 = [
        {
            "role": "user",
            "content": "Decide which of the following {locations} is better for a vacation. Return the best one and ONLY one. Do not offer any platitudes as to why they are both being returned, pick only a SINGLE ONE and return it.",
        }
    ]
    messages_2 = [
        {
            "role": "user",
            "content": "Generate an itinerary for {location}.",
        }
    ]
    messages_3 = [
        {
            "role": "user",
            "content": "Write an invite to a vacation based on the {itinerary}.",
        }
    ]
    node = read_from_file_tool
    LLM1 = LLM("LLM1")
    LLM2 = LLM("LLM2")
    LLM3 = LLM("LLM3")

    LLM1.set_messages(messages_1)
    LLM2.set_messages(messages_2)
    LLM3.set_messages(messages_3)
    init_dict = {node.get_id(): {"kwargs": {"file_path": "trellis_dag/tests/data.txt"}}}

    dag.add_node(node)
    dag.add_node(LLM1)
    dag.add_node(LLM2)
    dag.add_node(LLM3)

    dag.add_edge(node, LLM1, fn=lambda x: {"locations": x["file_contents"]})
    dag.add_edge(
        LLM1, LLM2, fn=lambda x: {"location": x["choices"][0]["message"]["content"]}
    )
    dag.add_edge(
        LLM2, LLM3, fn=lambda x: {"itinerary": x["choices"][0]["message"]["content"]}
    )

    res = await dag.execute(init_source_nodes=init_dict)


# Small DAG with multiple orders
# A -> B -> E -> F
# |         ^
# v         |
# C ------> D
#
# A: using https://github.com/sameerkumar18/corporate-bs-generator-api get a random corporate bs phrase
# B: call LLM to translate the phrase into plain english
# C: call LLM to make it longer
# D: call LLM to translate it into plain english
# E: ask LLM to choose which one of those would make more sense to a 5 year old
# F: ask LLM to translate the explanation into spanish
@pytest.mark.asyncio
async def test_execute_sort_small_multi_order(
    dag: DAG,
    corporate_bs_generator_api_tool: Node,
) -> None:
    messages_1 = [
        {
            "role": "user",
            "content": "Take this corporate BS {phrase} and rewrite it simply, in plain english, and short (less than 10 sentences).",
        }
    ]
    messages_2 = [
        {
            "role": "user",
            "content": "Take this corporate BS {phrase} and make it longer by 3 sentences.",
        }
    ]
    messages_3 = [
        {
            "role": "user",
            "content": "Take this corporate BS {phrase} and rewrite it simply, in plain english, and short (less than 10 sentences).",
        }
    ]
    messages_4 = [
        {
            "role": "user",
            "content": "Between \n\nPhrase 1:{phrase_1} and \n\nPhrase 2{phrase_2}, which one would make more sense to a 5 year old? Please return the full phrase.",
        }
    ]
    messages_5 = [
        {
            "role": "user",
            "content": "Take this {phrase} and translate it to Spanish to the best of your ability. If you don't know a word, feel free to make it up completely.",
        }
    ]

    node = corporate_bs_generator_api_tool
    LLM1 = LLM("LLM1")
    LLM2 = LLM("LLM2")
    LLM3 = LLM("LLM3")
    LLM4 = LLM("LLM4")
    LLM5 = LLM("LLM5")

    LLM1.set_messages(messages_1)
    LLM2.set_messages(messages_2)
    LLM3.set_messages(messages_3)
    LLM4.set_messages(messages_4)
    LLM5.set_messages(messages_5)

    init_dict = {}

    dag.add_node(node)
    dag.add_node(LLM1)
    dag.add_node(LLM2)
    dag.add_node(LLM3)
    dag.add_node(LLM4)
    dag.add_node(LLM5)

    def transform_1(x):
        return {"phrase": x["corporate_bs"]}

    def transform_2(x):
        return {"phrase_1": x["choices"][0]["message"]["content"]}

    def transform_3(x):
        return {"phrase": x["choices"][0]["message"]["content"]}

    def transform_4(x):
        return {"phrase_2": x["choices"][0]["message"]["content"]}

    dag.add_edge(node, LLM1, fn=transform_1)
    dag.add_edge(node, LLM2, fn=transform_1)
    dag.add_edge(LLM2, LLM3, fn=transform_3)
    dag.add_edge(LLM1, LLM4, fn=transform_2)
    dag.add_edge(LLM3, LLM4, fn=transform_4)
    dag.add_edge(LLM4, LLM5, fn=transform_3)

    res = await dag.execute(init_source_nodes=init_dict)


# DAG with one Node, no edges
# A
#
# A: ask LLM question about how it's doing
# A: call cat facts api
@pytest.mark.asyncio
async def test_execute_one_node(dag: DAG, cat_facts_api_tool: Node) -> None:
    cat_facts_api_tool.set_execute_args(limit=1, max_length=140)
    dag.add_node(cat_facts_api_tool)
    res = await dag.execute({})


# DAG with multiple Nodes, no edges
# A    B


# C    D
# A: ask LLM question about how it's doing
# B: call cat facts api
# C: using https://github.com/sameerkumar18/corporate-bs-generator-api get a random corporate bs phrase
# D: using https://uselessfacts.jsph.pl/ call uselessfacts and get a useless random fact
@pytest.mark.asyncio
async def test_execute_four_nodes(
    dag: DAG,
    cat_facts_api_tool: Node,
    corporate_bs_generator_api_tool: Node,
    useless_facts_api_tool: Node,
) -> None:
    LLM1 = LLM("LLM")
    messages1 = [
        {
            "role": "user",
            "content": "How are you doing today?",
        }
    ]
    LLM1.set_messages(messages1)

    init_dict = {
        cat_facts_api_tool.get_id(): {"kwargs": {"limit": 1, "max_length": 140}},
        LLM1.get_id(): {
            "kwargs": {
                "temperature": 0.5,
                "max_tokens": 25,
            }
        },
    }

    dag.add_node(cat_facts_api_tool)
    dag.add_node(corporate_bs_generator_api_tool)
    dag.add_node(useless_facts_api_tool)
    dag.add_node(LLM1)

    await dag.execute(init_source_nodes=init_dict)


# DAG with Nodes with multiple incoming edges
# A
# |
# v
# D <- B
# ^
# |
# C
#
# A: using https://github.com/sameerkumar18/corporate-bs-generator-api get a random corporate bs phrase
# B: using https://uselessfacts.jsph.pl/ call uselessfacts and get a useless random fact
# C: using https://imgflip.com/api call imgflip/get_memes, do result["data"]["memes"][0]["name"]
# D: generate what all of these statements have in common using LLM
@pytest.mark.asyncio
async def test_execute_multiple_incoming_edges(
    dag: DAG,
    corporate_bs_generator_api_tool: Node,
    useless_facts_api_tool: Node,
    img_flip_meme_name_api_tool: Node,
) -> None:
    LLM1 = LLM("LLM")
    messages1 = [
        {
            "role": "user",
            "content": "Statement 1\n{statement_1}\n\nStatement 2\n{statement_2}\n\nStatement 3\n{statement_3}\n\nWhat do all of these statements have in common? Even if it's something as simple as each of them containing a certain letter, please return it.",
        }
    ]
    LLM1.set_messages(messages1)

    init_dict = {
        LLM1.get_id(): {
            "kwargs": {
                "temperature": 0.5,
            }
        },
    }

    dag.add_node(img_flip_meme_name_api_tool)
    dag.add_node(corporate_bs_generator_api_tool)
    dag.add_node(useless_facts_api_tool)
    dag.add_node(LLM1)

    dag.add_edge(
        img_flip_meme_name_api_tool, LLM1, fn=lambda x: {"statement_1": x["meme_name"]}
    )
    dag.add_edge(
        corporate_bs_generator_api_tool,
        LLM1,
        fn=lambda x: {"statement_2": x["corporate_bs"]},
    )
    dag.add_edge(
        useless_facts_api_tool,
        LLM1,
        fn=lambda x: {"statement_3": x["useless_information"]},
    )

    res = await dag.execute(init_source_nodes=init_dict)


# DAG with Nodes with multiple outgoing edges
# B
# ^
# |
# A -> C
# |
# v
# D
#
# A: using https://uselessfacts.jsph.pl/ call uselessfacts and get a useless random fact
# B: call LLM to say why the fact isn't useless
# C: call LLM to say why the fact is useless
# D: call LLM to give more context on the fact
@pytest.mark.asyncio
async def test_execute_multiple_outgoing_edges(
    dag: DAG,
    useless_facts_api_tool: Node,
) -> None:
    LLM1 = LLM("LLM")
    messages1 = [
        {
            "role": "user",
            "content": "Why is this fact not useless?\n{useless_information}",
        }
    ]
    LLM1.set_messages(messages1)

    LLM2 = LLM("LLM")
    messages2 = [
        {
            "role": "user",
            "content": "Why is this fact useless?\n{useless_information}",
        }
    ]
    LLM2.set_messages(messages2)

    LLM3 = LLM("LLM")
    messages3 = [
        {
            "role": "user",
            "content": "Can you give more context on this fact?\n{useless_information}",
        }
    ]
    LLM3.set_messages(messages3)

    init_dict = {
        LLM1.get_id(): {
            "kwargs": {
                "temperature": 0.5,
            }
        },
        LLM2.get_id(): {
            "kwargs": {
                "temperature": 0.5,
            }
        },
        LLM3.get_id(): {
            "kwargs": {
                "temperature": 0.5,
            }
        },
    }

    dag.add_node(useless_facts_api_tool)
    dag.add_node(LLM1)
    dag.add_node(LLM2)
    dag.add_node(LLM3)

    dag.add_edge(
        useless_facts_api_tool,
        LLM1,
        fn=lambda x: {"useless_information": x["useless_information"]},
    )
    dag.add_edge(
        useless_facts_api_tool,
        LLM2,
        fn=lambda x: {"useless_information": x["useless_information"]},
    )
    dag.add_edge(
        useless_facts_api_tool,
        LLM3,
        fn=lambda x: {"useless_information": x["useless_information"]},
    )

    res = await dag.execute(init_source_nodes=init_dict)


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
#
# A: get a meme type using https://imgflip.com/api call imgflip/get_memes, do result["data"]["memes"][0]["name"]
# B: ask LLM to explain the origin of the meme in one sentence
# C: ask LLM to create a new meme tagline with it
# D: ask LLM to make the origin explanation something a dad would appreciate
# E: ask LLM to make the meme tagline something that a dad would like
# F: ask LLM to make the meme tagline funnier
# G: ask LLM to make an explanation of why the new meme tagline is funny given the context of the origin
# H: ask LLM to judge which one it prefers and print it
@pytest.mark.asyncio
async def test_execute_multiple_incoming_outgoing(
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
    pass
