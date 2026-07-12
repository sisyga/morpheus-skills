---
name: morpheus
description: Create, adapt, run, and debug Morpheus multicellular simulations and MorpheusML XML models. Use when Codex needs to write or fix MorpheusML, ground a model in bundled Morpheus examples, search built-in, contributed, or published Morpheus models, run Morpheus from the CLI, diagnose parser or runtime failures, or interpret simulation outputs and example media.
---

# Morpheus

Morpheus is an open-source multicellular simulation environment from TU Dresden. It uses MorpheusML XML for Cellular Potts Models, PDEs, ODEs, and mixed multiscale models.

## Core Rules

1. Never invent XML tags or attributes. Ground every non-trivial element in the bundled references or an upstream source listed below.
2. Prefer adapting the closest example over writing large sections from scratch.
3. Start new models from `references/model-template.md`.
4. Treat the example corpus as mixed-version input. Use examples for structure and patterns, then normalize syntax to the target version before delivering final XML.
5. Add `Analysis` only when it helps. It is recommended for debugging and visualization, but it is not mandatory for every valid model.

## Generated Corpus Files

The release build generates a searchable static corpus from a snapshot of the Morpheus model repository.

- `references/examples-summary.md`
  High-level counts by collection and MorpheusML version.
- `references/examples-index.md`
  Grep-friendly catalog of all bundled models. Search here first by title, keyword, tag, organism, collection, or model ID.
- `references/examples-manifest.json`
  Structured metadata for deterministic lookup when exact fields matter.
- `references/examples/<model-key>/overview.md`
  Per-model summary with source path, tags, main XML, versions, and copied attachments.
- `references/examples/<model-key>/*`
  Original model files copied from the static corpus snapshot, including XML, `index.md`, images, and small media attachments.

## Upstream Fallback Sources

Use the bundled references first. Consult upstream only when the bundled documentation or examples do not answer the task:

- [Morpheus source code](https://gitlab.com/morpheus.lab/morpheus) -- inspect the implementation when exact plugin behavior, accepted values, defaults, or parser/runtime details are unclear.
- [Morpheus model repository](https://gitlab.com/morpheus.lab/model-repo) -- search the extensive current library of built-in, contributed, and published models when the bundled examples do not contain a sufficiently close model.

Search only for the plugin or model pattern needed. Stop once the relevant implementation or a close working example provides enough evidence to author, fix, or explain the model.

## Retrieval Workflow

1. Identify the task type: CPM, PDE, ODE, multiscale, CLI execution, or debugging.
2. Search `references/examples-index.md` for the closest example by:
   - biological process
   - formalism such as CPM, PDE, ODE, multiscale
   - model ID such as `M2051`
   - tags, organism, author, or collection (`Built-in Examples`, `Contributed Examples`, `Published Models`)
3. Open the chosen `references/examples/<model-key>/overview.md`.
4. Open the main XML file in the same folder.
5. Open `index.md` and images in that folder only if they add useful biological or geometric context.
6. Consult `references/morpheusml-doc.md` when tags or attributes are uncertain.

## Authoring Workflow

1. Pick the closest bundled example or start from `references/model-template.md`.
2. Keep the reference structure intact and change only what the user actually needs.
3. Preserve valid symbol definitions and make every `symbol-ref` resolvable.
4. If the source example uses an older or newer MorpheusML version than the target model, port the pattern instead of copying syntax blindly.
5. Use relative asset paths only when the referenced files are actually present.

## Version Guidance

- Do not assume every bundled example uses the same MorpheusML version.
- For new models, default to the version used by `references/model-template.md` unless the user, local installation, or the selected example clearly requires another target.
- When adapting historical examples, keep the model idea and update obsolete syntax before returning XML.

## Validation Checklist

Before returning or running a model, verify:

- Root element is `MorpheusModel` with the intended version.
- `Description`, `Space`, and `Time` are present.
- Every `symbol-ref` has a valid definition or built-in meaning.
- Contact names match existing `CellType` names exactly.
- PDE fields, diffusion blocks, and equations refer to the same symbols.
- Asset paths point to files that actually exist.
- No tag or attribute was invented.
- `Analysis` matches the task: include it for debugging or visualization, omit it when it only adds noise.

## Morpheus-Specific Heuristics

- CPM models usually need `CellTypes`, `CPM`, and `CellPopulations`.
- PDE models usually need `Global`, `Field`, and a matching `System` with `DiffEqn`.
- ODE models usually keep `System` blocks in `Global` or in each `CellType`.
- Multiscale models often combine CPM motion, one or more fields, and cell-level or global ODE systems.
- Use example media only to understand geometry, initial conditions, or expected qualitative outcomes.

## Running Morpheus

Typical commands:

```bash
morpheus -f model.xml
morpheus -f model.xml --outdir out/ --num-threads 1
```

Windows often needs the full executable path:

```powershell
"C:\Program Files\Morpheus\morpheus.exe" -f model.xml
```

Useful outputs:

- `model_graph.dot` confirms the XML parsed.
- `plot-*.png` shows generated visualizations.
- `logger.csv` contains logged time-series data.

## Troubleshooting

- Unknown tag: search `references/morpheusml-doc.md` and compare with a nearby working example.
- Symbol not found: list definitions and usages, then fix the mismatch.
- Missing output files: inspect `Analysis` first.
- Parser crash or hang: reduce lattice size, stop time, and optional analysis frequency.
- Wrong qualitative behavior: compare initial conditions, boundary conditions, diffusion rates, adhesion values, and temperatures against the closest example.

## Output Expectations

- Return minimal, valid MorpheusML instead of speculative XML.
- When you base a model on a bundled example, name the example you adapted.
- When the task depends on execution, inspect stdout, stderr, and output files before concluding the run succeeded.
