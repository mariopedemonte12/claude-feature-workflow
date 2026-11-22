---
name: design-patterns
kind: guide
summary: When a design pattern solves a problem present in the code now, and when it is speculative
use-in: [plan, implement]
signals:
  - terms: ["pattern", "strategy", "factory", "adapter", "observer", "refactor"]
---
# Design Patterns Reference

A pattern is a named solution to a recurring problem. Apply one only when **its problem is present in the code now**. If the "use when" column does not describe the current code, the pattern is speculative and becomes an anti-pattern.

Prefer the language's native form: a first-class function often replaces Strategy or Command, a closure replaces a one-method class, a module replaces a Singleton, an iterator protocol replaces a hand-written Iterator.

## Creational

| Pattern | Use when | Misuse signal |
| --- | --- | --- |
| Abstract Factory | Families of related objects must be created consistently and the family varies (e.g. per platform) | One family only |
| Builder | An object has many optional parts or a multi-step valid construction | Two or three fields; named or optional arguments would do |
| Factory Method | The concrete type is decided at runtime by input or configuration | A factory that always returns the same type |
| Prototype | Creating by copying a configured instance is cheaper or simpler than building one | Objects that are cheap to construct |
| Singleton | Exactly one instance is a real constraint of the domain or resource | Used as global mutable state; hides dependencies and blocks tests. Prefer passing the instance in |

## Structural

| Pattern | Use when | Misuse signal |
| --- | --- | --- |
| Adapter | An existing interface must fit the one your code expects (third-party SDK, legacy API) | Wrapping an interface that already fits |
| Bridge | Two dimensions vary independently (abstraction × implementation) | Only one dimension varies |
| Composite | Clients must treat single items and trees of items uniformly | Flat collections |
| Decorator | Behavior is added to objects in combinations at runtime (logging, caching, retries) | A single fixed addition; edit the function instead |
| Facade | A subsystem's many calls need one simple entry point for its clients | A facade that forwards every call one-to-one |
| Flyweight | Huge numbers of similar objects exhaust memory, with measurements showing it | No measured memory problem |
| Proxy | Access must be controlled, delayed or remote (lazy loading, permission check, remote stub) | A proxy that only forwards |

## Behavioral

| Pattern | Use when | Misuse signal |
| --- | --- | --- |
| Chain of Responsibility | A request passes through a sequence of independent handlers (middleware, validation pipeline) | A fixed sequence of two steps |
| Command | Actions must be queued, logged, undone or retried as values | Commands executed immediately and discarded |
| Interpreter | A small language or rule grammar is evaluated repeatedly | A one-off parse; use a parser library |
| Iterator | Traversal of a custom collection must hide its structure | The language's iteration already covers it |
| Mediator | Many components talk to each other and the web of references is hard to change | Two components |
| Memento | State must be snapshotted and restored without exposing internals (undo) | No restore requirement |
| Observer | Several independent consumers react to state changes or events | One consumer; call it directly |
| State | Behavior changes with a lifecycle state and conditionals on the state spread across methods | Two states with one branch |
| Strategy | An algorithm is chosen at runtime among real, existing alternatives | One strategy; "in case we need another" |
| Template Method | Several variants share a fixed skeleton and differ in steps | One variant; or composition with functions is simpler |
| Visitor | Many operations run over a stable set of node types (ASTs, documents) | Node types change often |

## Architectural patterns often met in features

| Pattern | Use when | Misuse signal |
| --- | --- | --- |
| Dependency Injection (constructor or parameter) | Logic needs I/O, time or randomness that tests must replace | A container or framework introduced for a handful of objects |
| Ports and Adapters | The domain must stay independent of several infrastructures that actually vary or are tested in isolation | Ports with one adapter and no test double |
| Repository | Domain code needs collection-like access to persisted aggregates, separated from the query technology | A repository that only re-exposes the ORM one method at a time |
| Result / Either value | Expected failures are part of the domain and callers must handle them | Wrapping truly exceptional errors |
| Unit of Work / transaction script | Several writes must succeed or fail together | Single writes |

## Recording a pattern

When the implementation uses a pattern, the implementation report names it and states the present problem that justifies it, in one line: `Strategy: tax rules differ for CL and AR (FR-4), both implemented now.`
