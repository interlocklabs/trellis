# Trellis
## Intro
**Trellis is an [open-source](https://github.com/interlocklabs/exp-4.1.0-trellis) framework for programmatically
orchestrating LLM workflows as Directed Acyclic Graphs (DAGs) in Python.** We've intentionally designed it to give 
developers as much control as possible, and we've written documentation to make it incredibly easy to 
get started.

## Structure
Trellis is composed of only three abstractions: `Node`, `DAG`, and `LLM`.
- Node: the atomic unit of Trellis. Nodes are chained together to form a DAG. 
  `Node` is an abstract class with only *one* method required to implement.
- DAG: a directed acyclic graph of `Node`s. It is the primary abstraction for orchestrating LLM workflows. When you 
  add edges between `Node`s, you can specify a transformation function to reuse `Node`s and connect any two `Node`s.
  Trellis verifies the data flowing between `Nodes` in a `DAG` to ensure the flow of data is validated. 
- LLM: a wrapper around a large language model with simple catches for common OpenAI errors. Currently, the only provider
  that Trellis supports is OpenAI.

## Install
You can install Trellis with any of the following methods:

### Pip
```
pip install trellis
```

### Poetry
```
poetry add trellis
```

### Conda
```
conda install trellis
```
