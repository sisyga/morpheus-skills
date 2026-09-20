# Morpheus Skills

An [Agent Skill](https://agentskills.io) that makes Claude or Codex effective at working with **Morpheus**, the multicellular simulation environment from [TU Dresden](https://morpheus.gitlab.io/). The skill covers MorpheusML authoring, example-grounded adaptation, CLI execution, and debugging.

## Version 1.3

Version 1.3 updates the skill's authoring, validation, execution, and source-routing
guidance. The default release remains self-contained and lean: tracked XML examples
are converted into five curated Markdown references when the ZIP is built.

For offline-heavy use, the builder can optionally add a static snapshot of the public
[Morpheus model repository](https://gitlab.com/morpheus.lab/model-repo), including:

- `examples-summary.md` for corpus overview
- `examples-index.md` for grep-friendly lookup
- `examples-manifest.json` for structured metadata
- one folder per model with `overview.md`, XML, `index.md`, and copied non-video attachments

The optional corpus is not included in the default release. When network access is
available, the skill instead consults the official model repository selectively.

## Install in Claude Desktop

1. Go to the [Releases](https://github.com/sisyga/morpheus-skills/releases/latest) page
2. Download `morpheus.zip`
3. Open Claude Desktop -> Settings -> Capabilities
4. Ensure code execution and file creation are enabled
5. Upload `morpheus.zip`

## Install in Claude Code or Codex

Extract the release to your personal skills directory:

```bash
# macOS / Linux
curl -L https://github.com/sisyga/morpheus-skills/releases/latest/download/morpheus.zip -o /tmp/morpheus.zip
unzip -o /tmp/morpheus.zip -d ~/.claude/skills/

# Windows (PowerShell)
Invoke-WebRequest https://github.com/sisyga/morpheus-skills/releases/latest/download/morpheus.zip -OutFile $env:TEMP\morpheus.zip
Expand-Archive $env:TEMP\morpheus.zip -DestinationPath $env:USERPROFILE\.claude\skills\ -Force
```

## Release Layout

```text
morpheus.zip
`-- morpheus/
    |-- SKILL.md
    |-- LICENSE.txt
    |-- agents/
    |   `-- openai.yaml
    `-- references/
        |-- model-template.md
        |-- morpheusml-doc.md
        |-- cpm-examples.md
        |-- pde-examples.md
        |-- ode-examples.md
        |-- multiscale-examples.md
        `-- miscellaneous-examples.md
```

## Building the Default Release

The default build needs no external model checkout:

```bash
python3 build_release.py
```

## Building the Optional Offline-Full Release

Provide a local checkout or static snapshot of the Morpheus model repository:

```bash
python3 build_release.py \
  --model-repo /path/to/model-repo \
  --output morpheus-offline-full.zip
```

The source can be a local checkout or another static snapshot of:

- [https://gitlab.com/morpheus.lab/model-repo](https://gitlab.com/morpheus.lab/model-repo)

An optional size limit applies to non-text attachments:

```bash
python3 build_release.py \
  --model-repo /path/to/model-repo \
  --output morpheus-offline-full.zip \
  --max-binary-mb 25
```

Video files are always skipped. Large non-text attachments above the configured size cap are also skipped and recorded in the generated per-model overview files.

## Automated Releases

Pull requests and pushes to `master` build and validate the lean ZIP without publishing
it. Pushing a tag such as `v1.3.0` runs the release workflow, verifies that the tag
matches `metadata.version` in `morpheus/SKILL.md`, builds and validates `morpheus.zip`,
then creates the corresponding GitHub release or replaces its existing ZIP asset.

## Repo Structure

```text
morpheus-skills/
|-- build_release.py
|-- validate_release.py
`-- morpheus/
    |-- SKILL.md
    |-- LICENSE.txt
    |-- agents/
    |   `-- openai.yaml
    |-- assets/
    `-- references/
        |-- CPM/*.xml
        |-- PDE/*.xml
        |-- ODE/*.xml
        |-- Multiscale/*.xml
        |-- Miscellaneous/*.xml
        |-- model_template.txt
        `-- morpheusml_doc.txt
```

## Example Prompts

- "Create a Turing pattern reaction-diffusion model in Morpheus."
- "Find a published Morpheus model close to Delta-Notch signaling and adapt it."
- "Run this Morpheus XML and tell me why it fails."
- "Compare my CPM model against a bundled example and fix the symbol errors."

## About Morpheus

- Website: [https://morpheus.gitlab.io/](https://morpheus.gitlab.io/)
- Repository: [https://gitlab.com/morpheus.lab/morpheus](https://gitlab.com/morpheus.lab/morpheus)
- Model repository: [https://gitlab.com/morpheus.lab/model-repo](https://gitlab.com/morpheus.lab/model-repo)

## License

Apache-2.0. See [LICENSE](LICENSE).

The bundled model files come from the Morpheus model repository and keep their original upstream licensing and attribution context.
