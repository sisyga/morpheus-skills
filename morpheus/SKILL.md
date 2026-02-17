---
name: morpheus
description: >
  Expert skill for Morpheus, the open-source multicellular simulation environment
  (TU Dresden). Write valid MorpheusML v4 XML models, run simulations via CLI,
  and debug failures. Use when the user asks to: create or write a Morpheus model,
  generate MorpheusML XML, run or execute a simulation, install Morpheus, fix a
  broken model, diagnose simulation errors, interpret logs or output images, or
  work with Cellular Potts Models (CPM), reaction-diffusion PDEs, ODE signaling,
  or multiscale biological simulations.
license: Apache-2.0
compatibility: Requires Morpheus installed locally for simulation execution. XML authoring works without it.
metadata:
  author: MorpheusAI
  version: "1.0.0"
---

# Morpheus Expert Skill

Morpheus is an open-source modeling and simulation environment for multicellular systems from TU Dresden. It uses **MorpheusML v4**, a declarative XML language for CPM (Cellular Potts Model), ODE, PDE, and multiscale biological models in 2D/3D.

## Core Rules

1. **Never invent XML tags or attributes.** Always ground XML in the bundled reference examples.
2. **Prefer minimal modification** of reference XML over writing from scratch.
3. Every model must have: `<Description>`, `<Space>`, `<Time>`, and `<Analysis>`.
4. `<Analysis>` should almost always include `<Gnuplotter>` for visual sanity-checking (even infrequent snapshots). Logger-only CSV models are valid when only data output is needed.
5. When uncertain about a tag, check [references/morpheusml_doc.txt](references/morpheusml_doc.txt) — never guess.
6. MorpheusModel version is always `"4"`.

## Reference Files

This skill bundles the complete MorpheusML documentation and 43 example models across 7 files:

| Need | Read |
|------|------|
| Start a new model | [references/model_template.txt](references/model_template.txt) |
| Look up any tag/attribute | [references/morpheusml_doc.txt](references/morpheusml_doc.txt) |
| Cell sorting, migration, proliferation | [references/cpm-examples.md](references/cpm-examples.md) |
| Reaction-diffusion, Turing patterns | [references/pde-examples.md](references/pde-examples.md) |
| Signaling, cell cycle ODEs | [references/ode-examples.md](references/ode-examples.md) |
| Combined multiscale models | [references/multiscale-examples.md](references/multiscale-examples.md) |
| Game of Life, morphogen gradient | [references/miscellaneous-examples.md](references/miscellaneous-examples.md) |

---

# Part 1: Writing MorpheusML XML

## Workflow

1. **Identify model type** — CPM, PDE, ODE, or Multiscale (see guide below)
2. **Read the matching reference file** (e.g., `references/cpm-examples.md`) and pick a model to base yours on
3. **Read [references/model_template.txt](references/model_template.txt)** as a minimal skeleton
4. **Adapt minimally** — change only what's needed; keep the reference structure intact
5. **Validate** against the checklist below

## Mandatory XML Structure

```xml
<?xml version='1.0' encoding='UTF-8'?>
<MorpheusModel version="4">
    <Description>
        <Title>Model Title</Title>
        <Details>What this model does</Details>
    </Description>
    <Space>
        <Lattice class="square">
            <Neighborhood><Order>optimal</Order></Neighborhood>
            <Size symbol="size" value="100, 100, 0"/>
            <BoundaryConditions>
                <Condition type="periodic" boundary="x"/>
                <Condition type="periodic" boundary="y"/>
            </BoundaryConditions>
        </Lattice>
        <SpaceSymbol symbol="space"/>
    </Space>
    <Time>
        <StartTime value="0"/>
        <StopTime value="1000"/>
        <TimeSymbol symbol="time"/>
    </Time>
    <!-- Model-specific: Global, CellTypes, CPM, CellPopulations -->
    <Analysis>
        <ModelGraph include-tags="#untagged" format="dot" reduced="false"/>
        <Gnuplotter time-step="100" decorate="true">
            <Terminal name="png"/>
            <Plot title="Visualization">
                <Cells value="cell.type"/>   <!-- CPM -->
                <!-- <Field symbol-ref="u"/> -->  <!-- PDE -->
            </Plot>
        </Gnuplotter>
        <Logger time-step="100">
            <Input><Symbol symbol-ref="cellcount"/></Input>
            <Output><TextOutput/></Output>
        </Logger>
    </Analysis>
</MorpheusModel>
```

## Model Type Decision Guide

### CPM (Cellular Potts Model)
**Use for:** cell sorting, migration, proliferation, adhesion, cell shape.
**Requires:** `<CellTypes>`, `<CPM>`, `<CellPopulations>`.
**References:** See [references/cpm-examples.md](references/cpm-examples.md) — CellSorting_2D, Proliferation_2D, Persistence_2D, RunAndTumble, Protrusion_2D, Crypt, PigmentCells.

CPM essentials:
```xml
<CellTypes>
    <CellType name="cells" class="biological">
        <VolumeConstraint target="200" strength="1"/>
        <SurfaceConstraint target="1" strength="1" mode="aspherity"/>
    </CellType>
</CellTypes>
<CPM>
    <Interaction>
        <Contact type1="cells" type2="cells" value="10"/>
    </Interaction>
    <ShapeSurface scaling="norm">
        <Neighborhood><Order>optimal</Order></Neighborhood>
    </ShapeSurface>
    <MonteCarloSampler stepper="edgelist">
        <MCSDuration value="1"/>
        <MetropolisKinetics temperature="10"/>
        <Neighborhood><Order>optimal</Order></Neighborhood>
    </MonteCarloSampler>
</CPM>
<CellPopulations>
    <Population type="cells" size="1">
        <InitCircle mode="regular" number-of-cells="20">
            <Dimensions center="size.x/2, size.y/2, 0" radius="size.x/3"/>
        </InitCircle>
    </Population>
</CellPopulations>
```

### PDE (Partial Differential Equations)
**Use for:** reaction-diffusion, Turing patterns, morphogen gradients, wave propagation.
**Requires:** `<Global>` with `<Field>`, `<Diffusion>`, `<System>` with `<DiffEqn>`.
**References:** See [references/pde-examples.md](references/pde-examples.md) — TuringPatterns, ActivatorInhibitor_2D, ExcitableMedium_3D.

PDE essentials:
```xml
<Global>
    <Field symbol="u" value="rand_uni(0,1)">
        <Diffusion rate="0.01"/>
    </Field>
    <Field symbol="v" value="rand_uni(0,1)">
        <Diffusion rate="0.5"/>
    </Field>
    <System solver="Runge-Kutta" time-step="0.1">
        <DiffEqn symbol-ref="u">
            <Expression>0.05 * u - u^3 - v + 0.01</Expression>
        </DiffEqn>
        <DiffEqn symbol-ref="v">
            <Expression>0.01 * (u - v)</Expression>
        </DiffEqn>
    </System>
</Global>
```

### ODE (Ordinary Differential Equations)
**Use for:** signaling networks, cell cycle, gene regulation, population dynamics.
**Requires:** `<System>` with `<DiffEqn>` (inside `<Global>` or `<CellType>`).
**References:** See [references/ode-examples.md](references/ode-examples.md) — DeltaNotch, CellCycle, PredatorPrey, MAPK_SBML, LateralSignaling.

### Multiscale (CPM + PDE + ODE)
**Use for:** chemotaxis with signaling, cell cycle with fields, tissue patterning.
**References:** See [references/multiscale-examples.md](references/multiscale-examples.md) — MultiscaleModel, AutocrineChemotaxis, CellCycle, Dictyostelium, VascularPatterning, CellPolarity.

### Miscellaneous
**References:** See [references/miscellaneous-examples.md](references/miscellaneous-examples.md) — GameOfLife, FrenchFlag, ParticleAggregation.

## Gnuplotter Plot Content

- CPM models → `<Cells value="cell.type"/>` or `<Cells value="cell.id"/>`
- PDE models → `<Field symbol-ref="u"/>` (use the field symbol name)
- CPM+PDE → both `<Cells>` and `<Field>` in same or separate `<Plot>` blocks

## Validation Checklist

Before delivering XML, verify:
- [ ] Root element is `<MorpheusModel version="4">`
- [ ] `<Description>` has `<Title>`
- [ ] `<Space>` has `<Lattice>` with `<Neighborhood>`, `<Size>`, `<BoundaryConditions>`
- [ ] `<Time>` has `<StartTime>`, `<StopTime>`, `<TimeSymbol>`
- [ ] Every `symbol-ref="X"` has a matching `symbol="X"` defined somewhere
- [ ] `<Contact>` entries reference existing `<CellType>` names
- [ ] If CPM: `<MonteCarloSampler>` has `<MetropolisKinetics>` with `temperature`
- [ ] If PDE: `<Field>` has `<Diffusion>` and `<System>` has matching `<DiffEqn symbol-ref>`
- [ ] `<Analysis>` exists with appropriate outputs (Gnuplotter and/or Logger)
- [ ] No invented tags — every tag exists in a reference example or in `references/morpheusml_doc.txt`

## Common Pitfalls

1. **Missing `<Neighborhood>`** inside `<Lattice>` — always include `<Order>optimal</Order>`
2. **Undefined symbol references** — every `symbol-ref="X"` needs a matching `symbol="X"`
3. **Missing `<BoundaryConditions>`** — always define for x and y (and z if 3D)
4. **Wrong `<Contact>` names** — type1/type2 must exactly match `<CellType name="...">`
5. **`<Cells value="cell.type">`** in Gnuplotter when no CPM cells exist — use `<Field>` for PDE-only
6. **Inventing tags** — if not in any reference file, it doesn't exist
7. **Version mismatch** — always use version="4"
8. **Missing `<SpaceSymbol>`** — include `<SpaceSymbol symbol="space"/>` inside `<Space>`

---

# Part 2: Running Morpheus

## Installation

**Linux:** `flatpak install flathub de.tu_dresden.imc.Morpheus` or build from source at https://gitlab.com/morpheus.lab/morpheus
Binary: `/usr/bin/morpheus` or `/usr/local/bin/morpheus`

**macOS:** Download .dmg from https://morpheus.gitlab.io/download/
Binary: `/Applications/Morpheus.app/Contents/MacOS/morpheus`

**Windows:** Download installer from https://morpheus.gitlab.io/download/
Binary: `C:\Program Files\Morpheus\morpheus.exe`

Verify: `morpheus --help`

## Running a Simulation

```bash
morpheus -f model.xml           # basic run
morpheus -f model.xml -o out/   # with output directory
```

Key flags: `-f <file>` (required), `-o <dir>` (output), `-j <N>` (threads), `--help`.

**Timeout guidance:**
- 100x100 lattice, 1000 steps → seconds to ~1 min
- 256x256, 5000 steps → minutes
- 512x512+, 10000+ steps → 10+ minutes

## Output Files

| File | Source | Description |
|------|--------|-------------|
| `model_graph.dot` | `<ModelGraph/>` | Dependency graph (DOT format) |
| `plot-N_NNNNN.png` | `<Gnuplotter>` | Visualization snapshots |
| `logger.csv` | `<Logger>` | Time-series CSV data |

**stdout:** `Time: <value>` lines showing progress. "model is up" confirms XML parsed.
**stderr:** Error messages. Empty = clean run.

## Checking Success

1. Exit code 0 = completed
2. Last `Time:` line matches `<StopTime>`
3. PNG files exist (if Gnuplotter configured)
4. logger.csv exists (if Logger configured)

---

# Part 3: Debugging

## Diagnostic Workflow

1. **Read stderr** — first error is usually the root cause
2. **Read stdout** — check time progression
3. **Check output files** — PNGs, CSVs, model_graph.dot present?
4. **Cross-reference with XML** — match errors to specific elements
5. **Consult references** — compare against working examples

## Error Patterns & Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `Unknown tag "X"` | Invented tag | Search `references/morpheusml_doc.txt` for correct tag |
| `Symbol "X" not found` | Undefined symbol-ref | Match all `symbol-ref=` to `symbol=` definitions |
| `Cannot read file` | Wrong path | Check `-f` argument, use absolute paths |
| Segfault | Malformed lattice/boundaries | Simplify lattice, check bounds, reduce size |
| Timeout/hangs | Model too large | Halve `<Size>` and/or `<StopTime>` |
| No PNG output | Missing Gnuplotter | Add `<Gnuplotter>` with `<Terminal name="png"/>` |
| No CSV output | Missing Logger | Add `<Logger>` with `<TextOutput/>` |
| `Cannot parse value` | Wrong data type | Check `references/morpheusml_doc.txt` for correct type |
| `CellType "X" not found` | Contact mismatch | Match type1/type2 to `<CellType name="...">` |

## Fix Strategies

**Tag/structure errors:** Read closest reference example, compare tag-by-tag, replace broken section.

**Symbol errors:** List all `symbol="..."` definitions and all `symbol-ref="..."` usages. Fix mismatches. Built-in symbols: `time`, `cellcount`, `cell.type`, `cell.id`, `cell.center.x`, `cell.center.y`.

**Performance:** Halve lattice `<Size>` (most impactful), halve `<StopTime>`, increase `time-step` in Gnuplotter/Logger.

**Wrong results:** Check parameter magnitudes against references. Verify initial conditions. Check boundary conditions (periodic vs noflux). For CPM: temperature too high = random, too low = frozen. For PDE: high diffusion rate = instability.

## Log Analysis

- Last `Time:` value vs `<StopTime>` = progress percentage
- First error/fatal in stderr = root cause (later errors cascade)
- `model_graph.dot` exists = XML parsed successfully
- `[INFO]` messages are normal setup info

## Image Analysis

**CPM:** Well-defined cell boundaries = healthy. Jagged/fragmented = parameter issues. Distinct clusters = correct sorting. Visible growth = working proliferation.

**PDE:** Regular spots/stripes = correct Turing regime. Smooth gradients = stable diffusion. Spirals/waves = working excitable medium.

**General:** Compare early vs late frames. Static frames = equilibrium or wrong parameters. All-black/white = wrong min/max visualization bounds.
