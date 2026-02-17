# Morpheus Skills

An [Agent Skill](https://agentskills.io) that makes Claude an expert in **Morpheus**, the open-source multicellular simulation environment from [TU Dresden](https://morpheus.gitlab.io/). Covers writing MorpheusML v4 XML models, running simulations, and debugging failures.

## What it does

This skill teaches Claude to:

- **Write valid MorpheusML XML** — Cellular Potts Models (CPM), reaction-diffusion PDEs, ODE signaling, and multiscale simulations in 2D/3D
- **Run Morpheus from the CLI** — installation, execution, output interpretation
- **Debug failures** — diagnose errors, fix broken models, analyze logs and output images

It bundles 43 reference XML models and the complete MorpheusML tag documentation so Claude can always ground its answers in real examples rather than guessing.

## Install in Claude Desktop

1. Go to the [Releases](https://github.com/sisyga/morpheus-skills/releases/latest) page
2. Download **`morpheus.zip`**
3. Open **Claude Desktop** → **Settings** → **Capabilities**
4. Ensure **Code execution and file creation** is enabled
5. Click **Upload skill** and select the downloaded `morpheus.zip`

That's it — Claude will automatically use the skill when you ask about Morpheus models.

## Install in Claude Code (CLI)

Download the latest release and extract to your personal skills directory:

```bash
# macOS / Linux
curl -L https://github.com/sisyga/morpheus-skills/releases/latest/download/morpheus.zip -o /tmp/morpheus.zip
unzip -o /tmp/morpheus.zip -d ~/.claude/skills/

# Windows (PowerShell)
Invoke-WebRequest https://github.com/sisyga/morpheus-skills/releases/latest/download/morpheus.zip -OutFile $env:TEMP\morpheus.zip
Expand-Archive $env:TEMP\morpheus.zip -DestinationPath $env:USERPROFILE\.claude\skills\ -Force
```

Then use it in any project:
```
/morpheus
```

Or ask naturally — Claude will invoke it when relevant (e.g., "Create a cell sorting model").

## What's in the ZIP

The release ZIP is flat (no nested subdirectories) for Claude Desktop compatibility.
XML examples are merged into per-category markdown files during the build.

```
morpheus.zip
└── morpheus/
    ├── SKILL.md                       # Main skill instructions
    ├── LICENSE.txt                    # Apache-2.0
    ├── references/
    │   ├── model-template.md          # Minimal valid MorpheusML skeleton
    │   ├── morpheusml-doc.md          # Complete MorpheusML tag reference
    │   ├── cpm-examples.md            # 15 CPM examples (merged from CPM/*.xml)
    │   ├── pde-examples.md            # 5 reaction-diffusion examples
    │   ├── ode-examples.md            # 7 ODE/signaling examples
    │   ├── multiscale-examples.md     # 12 combined CPM+PDE+ODE models
    │   └── miscellaneous-examples.md  # 5 cellular automata, morphogen gradient
    └── assets/
        └── *.tif                      # Image assets used by some models
```

## Prerequisites

- **For XML authoring and debugging:** No prerequisites — works immediately
- **For running simulations:** [Morpheus](https://morpheus.gitlab.io/download/) must be installed locally

## Examples

Ask Claude things like:

- "Create a Turing pattern reaction-diffusion model"
- "Write a CPM cell sorting simulation with two cell types"
- "Run this Morpheus model and check the output"
- "My simulation crashed with 'Symbol not found' — help me fix it"
- "Analyze these simulation output images"

## Repo structure

The repo keeps XML examples in subfolders for easy editing. The build script
flattens them into per-category markdown files for the release ZIP.

```
morpheus/
├── SKILL.md
├── LICENSE.txt
├── references/
│   ├── CPM/*.xml               # 15 Cellular Potts Model examples
│   ├── PDE/*.xml               # 5 reaction-diffusion examples
│   ├── ODE/*.xml               # 7 ODE/signaling examples
│   ├── Multiscale/*.xml        # 12 combined multiscale models
│   ├── Miscellaneous/*.xml     # 5 cellular automata, morphogen gradient
│   ├── model_template.txt      # Minimal valid MorpheusML skeleton
│   └── morpheusml_doc.txt      # Complete MorpheusML tag reference
└── assets/
    └── *.tif                   # Image assets referenced by some models
```

## Building a release ZIP

To build `morpheus.zip` from source:

```bash
# From the repo root
python build_release.py
```

This merges all XML examples into per-category markdown files, renames .txt
references to .md, includes assets, and produces a flat ZIP suitable for
Claude Desktop upload.

## About Morpheus

[Morpheus](https://morpheus.gitlab.io/) is a free, open-source modeling and simulation environment for multicellular systems biology. It integrates cell-based models with ODEs and PDEs using a declarative XML language called MorpheusML.

- **Website:** https://morpheus.gitlab.io/
- **Repository:** https://gitlab.com/morpheus.lab/morpheus
- **Documentation:** https://gitlab.com/morpheus.lab/morpheus/-/wikis/home
- **Model repository:** https://morpheus.gitlab.io/model/

## License

Apache-2.0. See [LICENSE](LICENSE).

The bundled reference XML models are from the [Morpheus model repository](https://morpheus.gitlab.io/model/) (BSD 3-Clause).
