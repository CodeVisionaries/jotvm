# jotvm

**`jotvm`** is a pure-functional interpreter for extended JSON Patch.
It enables structured, deterministic transformations of JSON data.


## What is jotvm?

**`jotvm`** (JSON Operational Transformer Virtual Machine) is a lightweight
interpreter for a minimal, composable, and Turing-complete language based on
an extended form of [JSON Patch (RFC 6902)](https://tools.ietf.org/html/rfc6902).

It executes transformations as ordered lists of patch-like operations. These
include arithmetic, array manipulation, patch application, and basic control
flow. The language follows a pure-functional style: all functions are
deterministic and free of side effects.

The goal of `jotvm` is to serve as the computational core for more advanced
applications such as:

- ✅ Reproducible and auditable computation
- 🔒 Verifiable function execution (via cryptographic hashes)
- 🌍 Distributed and decentralized function graphs (e.g. via IPFS)
- 🧠 Building traceable knowledge graphs from data transformations

> 🛠️ **Note:** The language is still evolving. The set of core operations is not
> yet fixed and may change. The current implementation includes `call-func` as a
> primitive, but the boundary between Python-level functionality and
> patch-defined behavior is still under development.

---

## Why jotvm?

- **Pure-functional**: all functions are deterministic and side-effect-free
- **Turing-complete**: supports recursion, branching, and compositional logic
- **JSON-native**: both code and data are represented as JSON
- **Composable**: functions can call other functions, enabling reuse
- **Extensible**: designed to support meta fields, verifiable patches, and
  provenance-aware execution in the future

---

### 🔒 Host-System Isolation by Design

Unlike general-purpose scripting languages such as Python or JavaScript,
`jotvm` is designed to be sandboxed.

- No access to the file system
- No network access or external requests
- No interaction with host environment variables or system processes

All inputs, outputs, code, and memory exist entirely within a single JSON
document. Execution is limited to manipulating this data structure.

Even if a function is shared via IPFS or another decentralized channel, running
it with `jotvm` does not pose a risk to the host system. The worst outcome is
not arbitrary system access, but a potentially invalid or incorrect data
transformation.

#### ⚠️ Resource Exhaustion and Interpreter Stability

While `jotvm` is sandboxed in terms of capabilities, it is **not currently
resource-bounded**. Patches can consume unbounded memory or CPU time if written
carelessly or maliciously. For example:

- A patch might recursively apply itself without termination
- An operation could indefinitely grow an array or object
- Improper input could lead to interpreter crashes

At this stage, the Python interpreter and the host operating system are
responsible for enforcing resource limits (e.g. memory errors or OOM kills).
Future versions may introduce explicit safeguards such as:

- CPU or recursion limits
- Memory quotas or sandboxed runtimes
- Interpreter "fuel" mechanisms (e.g. step counters)

Users running untrusted patches are advised to embed `jotvm` in a resource-
controlled environment (e.g. subprocess with limits, Docker, or serverless
sandbox).

---

## Self-Applicable Patches and Execution Frames

A distinctive feature of `jotvm` is that patches are just JSON and can be
applied to any part of the global memory. This includes memory locations that
contain the patch itself.

This makes possible:

- Patches that verify their own hash before running
- Meta-programming constructs that manipulate or validate other patches
- Bootstrapping mechanisms using self-contained definitions

In `jotvm`, the execution context is defined explicitly by the user through
patch structure. There is no hidden function stack or call frame.

### The Role of `ctrl/apply-patch` and Memory Scope

The `ctrl/call-func` operation executes a patch inside an isolated memory
context. In contrast, the `ctrl/apply-patch` primitive applies a patch to a specific
subtree of the global memory. The target is defined by a JSON Pointer.

If the pointer is the root path (`""`), the patch has access to the entire
global state, including code, memory, and definitions. This means:

- Isolation is not guaranteed unless explicitly enforced
- Patches can alter or inspect other parts of the global document
- Functions and patches can be self-modifying or self-verifying

This makes `jotvm` a reflective and composable system. The degree of isolation
depends on how patches are structured and where they are applied.

---

## Why JSON as Syntax Feels Like an Abstract Syntax Tree (AST)

By using JSON to represent programs directly, `jotvm` eliminates the gap between
source code and abstract syntax trees. In most languages, source code must be
parsed into a structured tree before it can be interpreted. In `jotvm`, the JSON
itself is already the structured representation.

This offers several advantages:

- No custom parser is needed
- Programs are inherently structured and easy to validate or transform
- Code can generate or modify other code within the same format
- JSON integrates smoothly with APIs, databases, and content-addressed storage
- Multiple user interfaces (graphical, textual, DSLs) can target the same format

In short, `jotvm` treats code as data and data as code. JSON serves as both
syntax and program structure.

---

## Future Roadmap (planned features)

- [ ] Move `call-func` logic from the Python core into patch-defined logic
- [ ] Replace `-path` field handling with logic written as patches
- [ ] Support for `meta` and `req` fields in function bundles
- [ ] Use `decimal` module for fully reproducible floating-point arithmetic
- [ ] OS- and host system indepenent JSON serialization and deserialization
- [ ] Cryptographic verification of patch definitions
- [ ] Self-verifying `verify-and-call` patch
- [ ] Standard library of pure functions (math, logic, control)
- [ ] REPL and transpiler for easier function authoring
- [ ] Integration with IPFS or other decentralized storage layers

---

## Getting Started

This package is work in progress but you can already try it out.
Install the package via

```
git clone https://github.com/CodeVisionaries/jotvm.git
cd jotvm
python -m venv venv
source venv/bin/activate
pip install .
```

Afterwards, change into the `examples/` directory and
run one of the example scripts, e.g.
```
python 01_array_funcs.py
```

---

## License

MIT License

---

## AI Transparency Note

This project has benefited from conceptual brainstorming and documentation
assistance using the public version of ChatGPT, accessed without a login.
While the exact model version used is unknown, the interactions were with an
AI system provided by OpenAI, likely based on recent GPT-4-family models.

Discussions with the AI were used to explore core design ideas, reflect on
language semantics, and draft descriptive content such as this README.

However, all source code, formal specifications, and implementation decisions
have been authored exclusively by the project maintainer.

This note is included to encourage transparent development practices and to
acknowledge the growing utility of conversational AI in the early stages of
software architecture and system design.

