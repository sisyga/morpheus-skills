# Morpheus Skill

An Agent Skill that helps ChatGPT, Codex, and Claude create, adapt, run, and debug
[Morpheus](https://morpheus.gitlab.io/) multicellular simulations.

The skill provides practical guidance for MorpheusML models built with Cellular Potts
Models (CPM), ordinary differential equations (ODEs), partial differential equations
(PDEs), and coupled multiscale systems.

## What It Can Do

- Create MorpheusML models from a biological or mathematical description.
- Adapt a compatible example instead of inventing unsupported XML structures.
- Translate mechanisms, parameters, and expected behavior from a paper into Morpheus.
- Check model structure, symbols, cell types, equations, boundaries, and outputs.
- Run reduced-scale tests before attempting a full simulation.
- Diagnose parser errors, runtime failures, missing outputs, and unexpected behavior.
- Compare simulation images or numerical outputs with the intended phenomenon.
- Search official Morpheus documentation and model repositories when the bundled
  references are not sufficient.

## Requirements

You do not need Morpheus installed to draft or review MorpheusML XML.

To execute simulations, install Morpheus and ensure the `morpheus` command is available
on your `PATH`. See the official [Morpheus installation
guide](https://morpheus.gitlab.io/download/).

The skill includes curated offline documentation and examples. Internet access is
useful when a task requires newer documentation, source-code details, or a more closely
matching model from the official repository.

## Installation

Download `morpheus.zip` from the [latest
release](https://github.com/sisyga/morpheus-skills/releases/latest).

### ChatGPT Desktop

Open **Skills** in the ChatGPT desktop sidebar and add the downloaded `morpheus.zip`.
After installation, select the skill with `@morpheus` or describe a matching Morpheus
task directly.

### Codex CLI or IDE Extension

You can ask Codex's built-in installer to install the skill from this repository:

```text
$skill-installer Install the morpheus skill from https://github.com/sisyga/morpheus-skills
```

For a manual user-scoped installation on macOS or Linux:

```bash
mkdir -p "$HOME/.agents/skills"
curl -L https://github.com/sisyga/morpheus-skills/releases/latest/download/morpheus.zip \
  -o /tmp/morpheus.zip
unzip -o /tmp/morpheus.zip -d "$HOME/.agents/skills"
```

On Windows PowerShell:

```powershell
$skillsDir = Join-Path $HOME ".agents/skills"
New-Item -ItemType Directory -Force -Path $skillsDir | Out-Null
Invoke-WebRequest \
  "https://github.com/sisyga/morpheus-skills/releases/latest/download/morpheus.zip" \
  -OutFile "$env:TEMP/morpheus.zip"
Expand-Archive "$env:TEMP/morpheus.zip" -DestinationPath $skillsDir -Force
```

Codex discovers user skills in `$HOME/.agents/skills`. If the skill does not appear
immediately, restart Codex. See the official [Codex skills
documentation](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills).

Invoke it explicitly with `$morpheus`, or let Codex select it automatically for a
matching task.

### Claude Code

Extract the release into your personal Claude skills directory:

```bash
mkdir -p "$HOME/.claude/skills"
curl -L https://github.com/sisyga/morpheus-skills/releases/latest/download/morpheus.zip \
  -o /tmp/morpheus.zip
unzip -o /tmp/morpheus.zip -d "$HOME/.claude/skills"
```

## Example Prompts

- “Create a two-dimensional Turing-pattern reaction-diffusion model in Morpheus.”
- “Translate the mechanisms in this paper into a MorpheusML model and document every
  inferred parameter.”
- “Find a published Morpheus model similar to Delta–Notch signaling and adapt it.”
- “Run this model at reduced scale, inspect its outputs, and fix the first concrete
  failure.”
- “Why does this CPM model fragment into disconnected cells?”
- “Check whether every `symbol-ref` and contact name in this XML resolves correctly.”
- “Compare the early and late simulation frames with the expected striped phenotype.”

## How the Skill Uses Sources

The bundled package provides:

- a minimal MorpheusML model template;
- MorpheusML element and attribute documentation;
- curated CPM, PDE, ODE, multiscale, and miscellaneous examples;
- supporting image assets used by selected examples.

For unfamiliar, version-sensitive, or highly specialized features, the skill can also
consult:

- the official [Morpheus model repository](https://morpheus.gitlab.io/model/);
- the [model repository source](https://gitlab.com/morpheus.lab/model-repo);
- the [Morpheus source code](https://gitlab.com/morpheus.lab/morpheus).

Reference models establish valid structures and useful starting points. They do not,
by themselves, prove that a new simulation reproduces the requested biological
behavior. The skill therefore distinguishes structural checks, reduced-scale runtime
evidence, and full-scale results.

## Version 1.3

Version 1.3 adds stronger guidance for:

- grounding models in papers, bundled references, and official online sources;
- translating models from other simulators without copying incompatible syntax;
- testing at reduced scale before committing resources to a full run;
- evaluating both technical success and biological or visual behavior;
- reporting assumptions, evidence, and remaining mismatches explicitly.

## About Morpheus

Morpheus is an open-source modeling and simulation environment for multicellular
systems developed at TU Dresden.

- [Morpheus website](https://morpheus.gitlab.io/)
- [Support and documentation](https://morpheus.gitlab.io/#support)
- [Source code](https://gitlab.com/morpheus.lab/morpheus)
- [Model repository](https://morpheus.gitlab.io/model/)

## License

The skill is licensed under Apache-2.0. See [LICENSE](LICENSE).

Bundled Morpheus model files retain their original upstream licensing and attribution
context.
