# Seed catalog: layered, clean and hexagonal architectures

For projects organized by technical layer (`controllers/`, `services/`, `repositories/`), or by Clean / Onion / Ports-and-Adapters rings.

| Seed | Smell | Why it hurts | Instead | Detect |
| --- | --- | --- | --- | --- |
| L-01 | Inner layer depends on an outer one (domain imports the framework, ORM or HTTP types) | The core cannot be tested or changed without infrastructure | Dependencies point inward; the outer layer adapts | dependency-cruiser, import-linter, ArchUnit, depguard |
| L-02 | Layer skipping: controller calls the repository or database directly | Business rules get bypassed or duplicated | Go through the service or use case layer | Import rule tools |
| L-03 | Fat controller or handler holding business rules | Rules cannot be reused from jobs, CLIs or tests | Thin handler: parse, call the use case, map the result | Function-length limit on handlers; manual |
| L-04 | Anemic domain model plus service doing everything | Invariants are enforced in services, inconsistently | Put invariants and behavior with the data they protect | Manual |
| L-05 | Leaking persistence models (ORM entities) to the API or UI | Schema changes break clients; fields leak | Map to response types at the boundary | ast-grep on return types of handlers; manual |
| L-06 | Pass-through layer: a method that only forwards to the next layer | Ceremony without a rule; more files to change | Remove the layer for that path, or give it the rule it lacks | Manual |
| L-07 | Port with a single adapter and no test double | Abstraction cost without its benefit | Use the concrete dependency until a second adapter or a test needs the port | Manual |
| L-08 | Transaction boundaries inside repositories | Multi-step operations cannot be atomic | Transaction controlled by the use case | Manual |
