---
name: morpheus
description: Expert skill for Morpheus, the open-source multicellular simulation environment from TU Dresden. Write valid MorpheusML v4 XML models, run simulations via CLI, and debug failures. Use when the user asks to create a Morpheus model, generate MorpheusML XML, run or execute a simulation, install Morpheus, fix a broken model, diagnose simulation errors, interpret logs or output images, or work with Cellular Potts Models, reaction-diffusion PDEs, ODE signaling, or multiscale biological simulations.
license: Apache-2.0
compatibility: Requires Morpheus installed locally for simulation execution. XML authoring works without it.
metadata:
  author: MorpheusAI
  version: "1.1.0"
---

# Morpheus Expert Skill

Morpheus is an open-source modeling and simulation environment for multicellular systems from TU Dresden. It uses MorpheusML v4, a declarative XML language for CPM (Cellular Potts Model), ODE, PDE, and multiscale biological models in 2D/3D.

## Important Rules

1. **Never invent XML tags or attributes.** Always ground XML in the bundled reference examples.
2. **Prefer minimal modification** of reference XML over writing from scratch.
3. Every model must contain Description, Space, Time, and Analysis sections.
4. Analysis should almost always include Gnuplotter for visual sanity-checking (even infrequent snapshots). Logger-only CSV models are valid when only data output is needed.
5. When uncertain about a tag, check `references/morpheusml-doc.md` -- never guess.
6. MorpheusModel version is always "4".

## Reference Files

This skill bundles the complete MorpheusML documentation and 43 example models.

**Read these files as needed:**

- `references/model-template.md` -- Minimal valid MorpheusML skeleton to start any new model
- `references/morpheusml-doc.md` -- Complete MorpheusML tag and attribute reference
- `references/cpm-examples.md` -- 15 CPM examples (cell sorting, migration, proliferation)
- `references/pde-examples.md` -- 5 PDE examples (Turing patterns, reaction-diffusion)
- `references/ode-examples.md` -- 7 ODE examples (signaling, cell cycle)
- `references/multiscale-examples.md` -- 12 multiscale examples (CPM + PDE + ODE)
- `references/miscellaneous-examples.md` -- 5 misc examples (Game of Life, morphogen gradient)

---

## Instructions

### Step 1: Identify Model Type

Determine which type of model the user needs:

- **CPM** (Cellular Potts Model) -- cell sorting, migration, proliferation, adhesion, cell shape. Requires CellTypes, CPM, and CellPopulations sections.
- **PDE** (Partial Differential Equations) -- reaction-diffusion, Turing patterns, morphogen gradients. Requires Global with Field, Diffusion, and System with DiffEqn.
- **ODE** (Ordinary Differential Equations) -- signaling networks, cell cycle, gene regulation. Requires System with DiffEqn inside Global or CellType.
- **Multiscale** (CPM + PDE + ODE) -- chemotaxis with signaling, cell cycle with fields, tissue patterning. Combines elements from above.
- **Miscellaneous** -- cellular automata, morphogen gradients.

### Step 2: Read Matching Reference File

Open the matching reference file from the list above and pick the closest example model to base the new model on. For example, for a CPM cell sorting model, read `references/cpm-examples.md` and use CellSorting_2D as a starting point.

### Step 3: Read the Model Template

Read `references/model-template.md` for the minimal valid MorpheusML v4 skeleton.

### Step 4: Adapt Minimally

Change only what is needed. Keep the reference structure intact. Every MorpheusML model must have this structure:

```xml
<?xml version='1.0' encoding='UTF-8'?>
<MorpheusModel version="4">
    <Description>
        <Title>Model Title</Title>
        <Details>What this model does</Details>
    </Description>
    <Space>
        <Lattice class="square">
            <Neighborhood>
                <Order>optimal</Order>
            </Neighborhood>
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
    <!-- Model-specific sections go here -->
    <Analysis>
        <ModelGraph include-tags="#untagged" format="dot" reduced="false"/>
        <Gnuplotter time-step="100" decorate="true">
            <Terminal name="png"/>
            <Plot title="Visualization">
                <Cells value="cell.type"/>
            </Plot>
        </Gnuplotter>
        <Logger time-step="100">
            <Input>
                <Symbol symbol-ref="cellcount"/>
            </Input>
            <Output>
                <TextOutput/>
            </Output>
        </Logger>
    </Analysis>
</MorpheusModel>
```

### Step 5: Validate

Before delivering XML, verify all of these:

- Root element is MorpheusModel with version="4"
- Description section has a Title
- Space has Lattice with Neighborhood, Size, and BoundaryConditions
- Time has StartTime, StopTime, and TimeSymbol
- Every symbol-ref has a matching symbol definition somewhere
- Contact entries reference existing CellType names
- If CPM: MonteCarloSampler has MetropolisKinetics with temperature
- If PDE: Field has Diffusion and System has matching DiffEqn symbol-ref
- Analysis exists with appropriate outputs (Gnuplotter and/or Logger)
- No invented tags -- every tag must exist in a reference example or in `references/morpheusml-doc.md`

---

## Gnuplotter Plot Content

- CPM models: use Cells element with value="cell.type" or value="cell.id"
- PDE models: use Field element with symbol-ref pointing to the field symbol name
- CPM+PDE: use both Cells and Field in same or separate Plot blocks

---

## Running Morpheus

### Installation

**Linux:** `flatpak install flathub de.tu_dresden.imc.Morpheus` or build from source at https://gitlab.com/morpheus.lab/morpheus. Binary location: `/usr/bin/morpheus` or `/usr/local/bin/morpheus`

**macOS:** Download .dmg from https://morpheus.gitlab.io/download/. Binary location: `/Applications/Morpheus.app/Contents/MacOS/morpheus`

**Windows:** Download installer from https://morpheus.gitlab.io/download/. Binary location: `C:\Program Files\Morpheus\morpheus.exe`

Verify installation: `morpheus --help`

### Execution

```bash
morpheus -f model.xml           # basic run
morpheus -f model.xml -o out/   # with output directory
```

Key flags: `-f` (model file, required), `-o` (output directory), `-j` (threads), `--help`.

### Timeout Guidance

- 100x100 lattice, 1000 steps: seconds to ~1 min
- 256x256, 5000 steps: minutes
- 512x512+, 10000+ steps: 10+ minutes

### Output Files

- `model_graph.dot` -- dependency graph (from ModelGraph), confirms XML parsed
- `plot-N_NNNNN.png` -- visualization snapshots (from Gnuplotter)
- `logger.csv` -- time-series data (from Logger)

**stdout** shows `Time:` progress lines. "model is up" confirms XML parsed successfully.
**stderr** shows error messages. Empty stderr means a clean run.

### Checking Success

1. Exit code 0 means completed
2. Last Time value matches StopTime
3. PNG files exist if Gnuplotter was configured
4. logger.csv exists if Logger was configured

---

## Troubleshooting

### Diagnostic Workflow

1. **Read stderr** -- first error is usually the root cause
2. **Read stdout** -- check time progression
3. **Check output files** -- PNGs, CSVs, model_graph.dot present?
4. **Cross-reference with XML** -- match errors to specific elements
5. **Consult references** -- compare against working examples

### Common Errors

**Unknown tag "X"**: Invented tag. Search `references/morpheusml-doc.md` for the correct tag name.

**Symbol "X" not found**: Undefined symbol-ref. Ensure every symbol-ref has a matching symbol definition. Built-in symbols include time, cellcount, cell.type, cell.id, cell.center.x, cell.center.y.

**Cannot read file**: Wrong path. Check the -f argument and use absolute paths.

**Segfault**: Malformed lattice or boundaries. Simplify lattice, check bounds, reduce size.

**Timeout or hang**: Model too large. Halve Size and/or StopTime.

**No PNG output**: Missing Gnuplotter. Add Gnuplotter with Terminal name="png".

**No CSV output**: Missing Logger. Add Logger with TextOutput.

**Cannot parse value**: Wrong data type. Check `references/morpheusml-doc.md` for correct types.

**CellType "X" not found**: Contact name mismatch. Match type1/type2 to CellType name exactly.

### Fix Strategies

**Tag/structure errors:** Read closest reference example, compare tag-by-tag, replace broken section.

**Symbol errors:** List all symbol definitions and all symbol-ref usages. Fix mismatches.

**Performance:** Halve lattice Size (most impactful), halve StopTime, increase time-step in Gnuplotter/Logger.

**Wrong results:** Check parameter magnitudes against references. Verify initial conditions. Check boundary conditions (periodic vs noflux). For CPM: temperature too high means random, too low means frozen. For PDE: high diffusion rate can cause instability.

### Common Pitfalls

1. Missing Neighborhood inside Lattice -- always include Order set to optimal
2. Undefined symbol references -- every symbol-ref needs a matching symbol
3. Missing BoundaryConditions -- always define for x and y (and z if 3D)
4. Wrong Contact names -- type1/type2 must exactly match CellType name values
5. Using Cells in Gnuplotter when no CPM cells exist -- use Field for PDE-only models
6. Inventing tags -- if not in any reference file, it does not exist
7. Version mismatch -- always use version="4"
8. Missing SpaceSymbol inside Space

### Image Analysis

**CPM:** Well-defined cell boundaries means healthy. Jagged/fragmented means parameter issues. Distinct clusters means correct sorting.

**PDE:** Regular spots/stripes means correct Turing regime. Smooth gradients means stable diffusion. Spirals/waves means working excitable medium.

**General:** Compare early vs late frames. Static frames means equilibrium or wrong parameters. All-black/white means wrong visualization bounds.
