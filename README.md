# Morpheus Skills

An [Agent Skill](https://agentskills.io) that makes Claude or Codex effective at working with **Morpheus**, the multicellular simulation environment from [TU Dresden](https://morpheus.gitlab.io/). The skill covers MorpheusML authoring, example-grounded adaptation, CLI execution, and debugging.

## What Changed

The release build no longer flattens a small hand-picked XML set into a few large markdown files.

Instead, it now packages a static snapshot of the public [Morpheus model repository](https://gitlab.com/morpheus.lab/model-repo) and generates:

- `examples-summary.md` for corpus overview
- `examples-index.md` for grep-friendly lookup
- `examples-manifest.json` for structured metadata
- one folder per model with `overview.md`, XML, `index.md`, and copied non-video attachments

This keeps retrieval sharper than searching giant merged markdown blobs and lets the skill use built-in, contributed, and published models from one release snapshot.

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
        |-- examples-summary.md
        |-- examples-index.md
        |-- examples-manifest.json
        `-- examples/
            `-- <model-key>/
                |-- overview.md
                |-- *.xml
                |-- index.md
                `-- attachments...
```

## Local Build Inputs

Place a local snapshot of the Morpheus model repository at:

```text
./model-repo/
```

or pass an explicit path to the builder:

```bash
python build_release.py --model-repo /path/to/model-repo
```

The source can be a local checkout or another static snapshot of:

- [https://gitlab.com/morpheus.lab/model-repo](https://gitlab.com/morpheus.lab/model-repo)

## Building a Release

```bash
python build_release.py --model-repo ./model-repo
```

Optional flag:

```bash
python build_release.py --model-repo ./model-repo --max-binary-mb 25
```

Video files are always skipped. Large non-text attachments above the configured size cap are also skipped and recorded in the generated per-model overview files.

## Repo Structure

```text
morpheus-skills/
|-- build_release.py
|-- model-repo/                  # local snapshot, ignored by git
`-- morpheus/
    |-- SKILL.md
    |-- LICENSE.txt
    |-- agents/
    |   `-- openai.yaml
    |-- assets/
    `-- references/
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
