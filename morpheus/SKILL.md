---
name: morpheus
description: Authors, translates, runs, validates, and debugs Morpheus/MorpheusML simulation models (Cellular Potts/CPM, ODE, PDE/reaction-diffusion, and multiscale) using bundled reference models and the MorpheusML tag reference. Use when working with Morpheus XML model files or the morpheus CLI, or when reproducing a published multicellular model in Morpheus.
license: Apache-2.0
metadata:
  author: MorpheusAI
  version: "1.5.0"
---

# Morpheus

MorpheusML is the XML model language of the Morpheus multicellular simulator. Running simulations requires a local Morpheus installation; authoring XML does not.

## Operating Contract

For create, translate, fix, or reproduce tasks, run the model by default when Morpheus is available and refine it from observed outputs. For review or diagnosis, report findings without rewriting or running the model unless asked. Valid XML alone does not establish successful biological or visual reproduction.

## Authoring and Validation Workflow

1. **Ground the target.** State the model class, requested observable, and material assumptions.
   - For paper-based work, use text and methods for mechanisms, entities, equations, parameters, and initial or boundary conditions.
   - Use relevant figures, captions, and surrounding text for qualitative targets such as clustering, fronts, stripes, spots, gradients, lumen formation, or invasion.
   - Record inferred or approximated values instead of presenting them as reported facts.
   - If the source uses another simulator or formalism, translate its biology, mechanisms, parameters, and observables before mapping them to MorpheusML.
2. **Choose a grounded starting model.** Follow [Sources and Tool Routing](#sources-and-tool-routing). Read the closest compatible example and `references/model-template.md`. Start with bundled or MCP references; use the official model repository when they lack a suitable example, and consult the MorpheusML documentation or official source code for unfamiliar constructs or version-sensitive behavior.
3. **Adapt minimally.** Preserve known-good ordering and nesting. Change only the mechanisms, parameters, geometry, initialization, and analysis required by the target.
4. **Validate structure.** Check the [MorpheusML Quick Reference](#morpheusml-quick-reference), then verify every symbol relationship, model-specific section, contact name, equation reference, and configured output before execution.
5. **Run at reduced scale first.** For create, translate, fix, or reproduce tasks, create a separate reduced-scale configuration whenever Morpheus execution is available. Use smaller lattice dimensions, fewer cells or population members, and a shorter `StopTime` as appropriate. Preserve the mechanisms, geometry class, boundary types, and relative parameter relationships needed for the reduced run to remain meaningful. If execution is unavailable, leave runtime and phenotype explicitly unverified and continue to step 8 with structural validation only.
6. **Iterate at reduced scale.**
   - Confirm exit code zero, progression to `StopTime`, configured PNG and/or CSV outputs, and no remaining stderr error.
   - Inspect early and late frames and compare observed morphology or dynamics with the requested phenomenon.
   - Make one conservative, evidence-backed correction at a time and repeat the reduced run.
   - Estimate whether the target-scale run fits the available time and resources. Do not scale up while failures, timeouts, or unexplained behavior remain.
7. **Validate at target scale.** After the reduced-scale gate passes, restore the target dimensions, populations, and duration. Run the target model and repeat both the technical and visual or biological evidence checks. Reduced-scale success does not establish a scale-dependent target phenotype.
8. **Report the result.** Distinguish structural validation, reduced-scale behavior, and target-scale evidence. State anything that could not be executed or verified.

## MorpheusML Quick Reference

### Core Invariants

- Never invent XML tags or attributes. Ground each unfamiliar construct in a compatible bundled or official model, `references/morpheusml-doc.md`, or the official Morpheus source code.
- Prefer a minimal adaptation of the closest reference model over XML written from scratch.
- New models use `<MorpheusModel version="4">` and contain `Description`, `Space`, `Time`, and `Analysis`.
- `Description` contains a `Title`. `Space` contains a `Lattice` with `Neighborhood`, `Size`, and `BoundaryConditions`, plus a `SpaceSymbol`. `Time` contains `StartTime`, `StopTime`, and `TimeSymbol`.
- Every `symbol-ref` resolves to a defined symbol. Every contact pair names existing `CellType` values.
- CPM models include `CellTypes`, `CPM`, and `CellPopulations`. `MonteCarloSampler` has `MetropolisKinetics` with temperature. Biological CPM cell types normally include `ConnectivityConstraint` unless the requested biology or closest reference justifies fragmentation.
- PDE fields include `Diffusion`; their systems contain matching `DiffEqn` references.
- `Analysis` contains outputs appropriate to the task. Use `Gnuplotter` for visual validation and/or `Logger` for numerical output. Logger-only models are valid when no visual phenotype needs inspection.
- In `Gnuplotter`, use `Cells value="cell.type"` or `cell.id` for CPM and `Field symbol-ref="..."` for PDE.

### Model Types

| Class | Typical use | Required model-specific structure |
| --- | --- | --- |
| CPM | Cell sorting, migration, proliferation, adhesion, shape | `CellTypes`, `CPM`, `CellPopulations` |
| PDE | Reaction-diffusion, Turing patterns, morphogen gradients | Global `Field`, `Diffusion`, `System` with `DiffEqn` |
| ODE | Signaling, cell cycle, gene regulation | `System` with `DiffEqn` in `Global` or a `CellType` |
| Multiscale | Chemotaxis with signaling, cell-cycle/field coupling, tissue patterning | Relevant CPM, PDE, and ODE structures combined |
| Miscellaneous | Cellular automata or models outside the classes above | Closest verified reference structure |

## Sources and Tool Routing

Keep source authority distinct:

- Supplied papers and user artifacts establish the requested biology, parameters, and target phenotype.
- Compatible Morpheus models, documentation, and source code establish valid MorpheusML structure and runtime semantics.
- Observed simulation outputs establish what the generated model actually does.
- Reference models are structural and mechanistic evidence, not proof that the requested paper result was reproduced.

### Bundled References

Load only references relevant to the current decision. Every file except the template is too large to read whole: read its `## Contents` section first, then `grep -n` for the entry you need and read only that section.

```bash
grep -n "^# Chemotaxis" references/morpheusml-doc.md        # one tag or plugin
grep -n "^## CellSorting_2D" references/cpm-examples.md     # one example model
grep -n "<Chemotaxis" references/*-examples.md              # examples that use a construct
```

- `references/model-template.md` — minimal MorpheusML v4 skeleton
- `references/morpheusml-doc.md` — tag and attribute reference
- `references/cpm-examples.md` — cell sorting, migration, proliferation, adhesion, and cell shape
- `references/pde-examples.md` — reaction-diffusion, Turing patterns, and morphogen gradients
- `references/ode-examples.md` — signaling, cell-cycle, and gene-regulation systems
- `references/multiscale-examples.md` — coupled CPM, PDE, and ODE models
- `references/miscellaneous-examples.md` — cellular automata and other models
- `assets/` — TIFF domain images loaded by the `Crypt` and `ActivatorInhibitor_Domain` examples through `<Domain><Image path="assets/..."/>`. Morpheus resolves this path relative to the directory it is launched from, so when adapting either model, copy the TIFF next to the new model and update the path, or use an absolute path.

### Official External Sources

The bundled references are a curated offline starting point, not the only or necessarily newest Morpheus resources. When web access is available, consult official sources selectively:

- [Morpheus Model Repository](https://morpheus.gitlab.io/model/) — search built-in, contributed, and published models for closer structural or biological examples. Check each model's category and provenance rather than treating every contribution as normative. The underlying files and history are available in the [model repository on GitLab](https://gitlab.com/morpheus.lab/model-repo).
- [Morpheus source code](https://gitlab.com/morpheus.lab/morpheus) — consult for release-specific feature support, XML parsing, plugin behavior, and runtime semantics when models or documentation are ambiguous.

Match external material to the installed Morpheus version. Models in older MorpheusML versions are valid references, because Morpheus ports them to the current version automatically when it loads them.

### Tool Selection

When the Morpheus MCP server is available, use its tools as the primary interface. Tool names below are fully qualified with the server name `morpheus`; if the server is registered under another name, substitute that name.

- Start a run workspace with `morpheus:create_run`.
- Discover and read references with `morpheus:list_references` and `morpheus:read_reference`.
- Read supplied papers with `morpheus:extract_paper_text`.
- Identify relevant figures with `morpheus:list_paper_figures` or `morpheus:list_paper_visuals`, then render only the pages needed to recover the target phenotype or geometry with `morpheus:render_pdf_pages`.
- Check structure with `morpheus:validate_model_xml`, then write generated XML with `morpheus:write_model_xml`.
- Run with `morpheus:run_morpheus_model`; review with `morpheus:summarize_morpheus_run`, `morpheus:sample_output_images`, and `morpheus:evaluate_technical_run` as appropriate.
- Inspect returned images with an image-capable tool and logs, CSV files, or manifests with `morpheus:read_file_text`.

Use direct filesystem or CLI operations when MCP is unavailable, lacks the needed operation, or the user explicitly requests CLI commands.

### CLI Fallback

Verify the executable with `morpheus --help`, then run:

```bash
morpheus -f model.xml
morpheus -f model.xml -o out/
```

Relevant flags are `-f` for the model file, `-o` for the output directory, and `-j` for threads. Expected artifacts may include `model_graph.dot`, `plot-N_NNNNN.png`, and `logger.csv`. A clean run reaches `StopTime`; artifact presence must match the configured `Analysis` outputs.

## Troubleshooting

Diagnose the first concrete failure before changing the model.

| Symptom | Check first | Minimal response |
| --- | --- | --- |
| Unknown tag or attribute | Exact spelling and nesting in a compatible model or MorpheusML docs | Replace only the unsupported construct |
| Symbol not found | Definitions and every `symbol-ref` | Repair the mismatched reference |
| Cell type not found | `Contact` names against `CellType name` values | Make names identical |
| Cannot parse value | Expected type and expression syntax in the docs | Correct the value, not surrounding structure |
| No PNG or CSV | Configured `Gnuplotter` or `Logger` outputs | Add only the output the task requires |
| Timeout or hang | Lattice size, `StopTime`, and output frequency | Reduce the smallest dominant workload factor |
| Segmentation fault | Lattice, boundaries, initialization, and malformed structures | Compare the failing section with a working reference |
| Valid run, wrong behavior | Initial conditions, boundaries, parameter scale, and source assumptions | Change one evidence-backed cause and rerun |

For CPM outputs, inspect cell boundaries, fragmentation, sorting, and motion. For PDE outputs, inspect expected gradients, spots, stripes, waves, or steady states. Treat all-black, all-white, or static frames as evidence to inspect visualization bounds and model dynamics, not as proof of a specific cause.
