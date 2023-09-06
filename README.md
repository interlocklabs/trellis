# Trellis
## Intro
**Trellis is an open-source framework for programmatically
orchestrating LLM workflows as Directed Acyclic Graphs (DAGs) in Python.** We've intentionally designed it to give 
developers as much control as possible, and we've written documentation to make it incredibly easy to 
get started. Start building with our [docs](https://interlocklabsinc.mintlify.app/documentation/introduction).

## Structure
Trellis is composed of only three abstractions: `Node`, `DAG`, and `LLM`.
- Node: the atomic unit of Trellis. Nodes are chained together to form a DAG. 
  `Node` is an abstract class with only *one* method required to implement.
- DAG: a directed acyclic graph of `Node`s. It is the primary abstraction for orchestrating LLM workflows. When you 
  add edges between `Node`s, you can specify a transformation function to reuse `Node`s and connect any two `Node`s.
  Trellis verifies the data flowing between `Nodes` in a `DAG` to ensure the flow of data is validated. 
- LLM: a wrapper around a large language model with simple catches for common OpenAI errors. Currently, the only provider
  that Trellis supports is OpenAI.

## Environment Variables
- If you're going to use the LLM class, set:
    - `OPENAI_API_KEY=YOUR_OPENAI_KEY`
- If you don't want us to send telemetry data (in the `Node._init_()`, `LLM.execute()` (including prompts and responses from OpenAI) and `DAG.execute()` methods, info about nodes you create or dags you run), to an external server (currently (PostHog)[https://posthog.com/]) for analysis, set:
    - `TRELLIS_DISABLE_TELEMETRY=1`
- If you want to reduce the amount of information the logger returns, set:
    - [for everything] `TRELLIS_LOG_LEVEL=DEBUG`
    - [for status updates] `TRELLIS_LOG_LEVEL=INFO`
    - [for only warnings] `TRELLIS_LOG_LEVEL=WARNING`
    - [for errors which stop runtime] `TRELLIS_LOG_LEVEL=ERROR`
    - [for only critical errors] `TRELLIS_LOG_LEVEL=CRITICAL`

## Install
You can install Trellis with any of the following methods:

### Pip
```
pip install trellis-dag
```

### Poetry
```
poetry add trellis-dag
```

### Conda
```
conda install trellis-dag
```
