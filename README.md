# kaliflow - Kali CLI Workflow Runner

A minimal, YAML-driven CLI workflow runner for Kali Linux pentesters. Designed to automate and organize common pentesting tasks into reusable workflows.

## Repository Layout

```
kaliflow/
├── kaliflow.py
├── kaliflow.yml
├── README.md
├── LICENSE
└── .gitignore
```

## Features

* Define templates in YAML for repeated workflows.
* Timestamped session folders in `~/kaliflow_sessions/`.
* Logs each command's output into separate files.
* Generates `meta.json` and `summary.md` per session for easy reporting.
* Minimal dependencies, CLI-first.

## Requirements

* Python 3
* `pyyaml` library (`sudo apt install python3-yaml` or `pip install pyyaml`)
* Tools referenced in templates (nmap, gobuster, subfinder, nikto, etc.)

## Installation

```bash
git clone https://github.com/<yourusername>/kaliflow.git
cd kaliflow
chmod +x kaliflow.py
```

## Quickstart

Create a sample config:

```bash
./kaliflow.py init
```

List available templates:

```bash
./kaliflow.py list
```

View a template's details:

```bash
./kaliflow.py show quick-recon
```

Run a template against a target:

```bash
./kaliflow.py run quick-recon --target example.com
```

Pass extra variables to templates:

```bash
./kaliflow.py run web-suite --target 10.10.10.5 --var port=8080
```

Each run creates a new session folder with:

* `cmd_1.log`, `cmd_2.log`, ... for command outputs
* `meta.json` containing session metadata
* `summary.md` for a quick report

## Extensibility Ideas

* Add `--parallel` to run commands concurrently.
* Integrate with tmux to run commands in separate panes.
* Add hooks to upload session folders to remote storage.
* Support advanced templating with Jinja2.

## License

MIT License. See LICENSE file.
