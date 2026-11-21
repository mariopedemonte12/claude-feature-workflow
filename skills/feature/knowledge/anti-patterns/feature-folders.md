# Seed catalog: feature folders (vertical slices)

For projects organized by feature (`features/<name>/`, `modules/<name>/`, `slices/…`).

| Seed | Smell | Why it hurts | Instead | Detect |
| --- | --- | --- | --- | --- |
| FF-01 | Cross-feature internal import: a feature imports a file inside another feature's folder | Features can no longer change independently | Import through the other feature's public entry point | dependency-cruiser, eslint-plugin-boundaries, import-linter, ast-grep on import paths |
| FF-02 | Dumping-ground shared folder (`shared/`, `common/`, `utils/`) growing faster than features | Shared code with one user couples unrelated features | Keep code in its feature until a second feature needs it | Manual; count of single-user modules in shared |
| FF-03 | Technical layers recreated inside every feature in advance (`controllers/`, `services/`, `models/` with one file each) | Empty ceremony; navigation cost without benefit | Grow sub-folders only when several files of one kind exist | Manual |
| FF-04 | Feature logic placed in a global technical folder | The feature is scattered; deleting it leaves remains | Put it in its feature folder | Manual; path rules |
| FF-05 | Cyclic dependency between features | Neither can change or be extracted alone | Extract the shared concept or invert the dependency with an event | dependency-cruiser, madge, import-linter |
| FF-06 | Tests far from the feature they test | Tests are forgotten when the feature changes | Tests next to the code, or in the project's mirrored test path | Path rule |
| FF-07 | Shared database tables written by several features without an owner | Invariants are enforced in several places, inconsistently | One owning feature writes; others read or call it | Manual |
