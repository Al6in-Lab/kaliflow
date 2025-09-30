#!/usr/bin/env python3
import argparse
import os
import subprocess
import sys
import yaml
from datetime import datetime
from pathlib import Path
import json

CONFIG_NAME = "kaliflow.yml"
SESSION_ROOT = Path.home() / "kaliflow_sessions"

def load_config(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)

def init_sample(path):
    sample = {
        "templates": {
            "quick-recon": {
                "desc": "Quick recon: nmap, subfinder, gobuster (web)",
                "commands": [
                    "nmap -sC -sV -oN {out}/nmap_{target}.txt {target}",
                    "subfinder -d {target} -o {out}/subfinder_{target}.txt || true",
                    "gobuster dir -u http://{target}/ -w /usr/share/wordlists/dirb/common.txt -o {out}/gobuster_{target}.txt || true"
                ]
            },
            "web-suite": {
                "desc": "Web-oriented scan",
                "commands": [
                    "nikto -h http://{target} -output {out}/nikto_{target}.txt || true",
                    "whatweb {target} -v > {out}/whatweb_{target}.txt || true"
                ]
            }
        }
    }
    with open(path, "w") as f:
        yaml.dump(sample, f, sort_keys=False)

def ensure_session_dir(name):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = SESSION_ROOT / f"{name}_{ts}"
    path.mkdir(parents=True, exist_ok=True)
    return path

def run_template(config, name, target, extra_vars):
    templates = config.get("templates", {})
    if name not in templates:
        print(f"Template '{name}' not found.")
        sys.exit(2)
    tpl = templates[name]
    sess = ensure_session_dir(name)
    outdir = str(sess)
    meta = {
        "template": name,
        "description": tpl.get("desc", ""),
        "target": target,
        "start": datetime.now().isoformat(),
        "commands": []
    }
    for i, raw_cmd in enumerate(tpl.get("commands", []), start=1):
        cmd = raw_cmd.format(out=outdir, target=target, **extra_vars)
        meta["commands"].append({"cmd": cmd, "index": i})
        log_file = Path(outdir) / f"cmd_{i}.log"
        try:
            with log_file.open("w") as lf:
                proc = subprocess.Popen(cmd, shell=True, stdout=lf, stderr=subprocess.STDOUT, executable="/bin/bash")
                proc.communicate()
        except KeyboardInterrupt:
            break
    meta["end"] = datetime.now().isoformat()
    with open(Path(outdir) / "meta.json", "w") as mf:
        json.dump(meta, mf, indent=2)
    with open(Path(outdir) / "summary.md", "w") as sm:
        sm.write(f"# kaliflow session — {name}\n\n")
        sm.write(f"- target: `{target}`\n")
        sm.write(f"- template: `{name}` — {tpl.get('desc','')}\n")
        sm.write(f"- started: {meta['start']}\n")
        sm.write(f"- finished: {meta['end']}\n\n")
        sm.write("## Commands run\n\n")
        for c in meta["commands"]:
            sm.write(f"```bash\n{c['cmd']}\n```\n\n")
        sm.write("## Logs\n\n")
        for i, c in enumerate(meta["commands"], start=1):
            fn = f"cmd_{i}.log"
            sm.write(f"- [{fn}]({fn})\n")

def list_templates(config):
    for name, tpl in config.get("templates", {}).items():
        print(f"- {name}: {tpl.get('desc', '')}")

def show_template(config, name):
    tpl = config.get("templates", {}).get(name)
    if not tpl:
        sys.exit(2)

def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd")
    runp = sub.add_parser("run")
    runp.add_argument("template")
    runp.add_argument("--target", "-t", required=True)
    runp.add_argument("--var", action="append", default=[])
    sub.add_parser("list")
    showp = sub.add_parser("show")
    showp.add_argument("template")
    sub.add_parser("init")

    args = parser.parse_args()
    cfgpath = Path.cwd() / CONFIG_NAME
    if args.cmd == "init":
        if not cfgpath.exists():
            init_sample(cfgpath)
        return

    if not cfgpath.exists():
        sys.exit(1)

    config = load_config(cfgpath)

    if args.cmd == "list":
        list_templates(config)
    elif args.cmd == "show":
        show_template(config, args.template)
    elif args.cmd == "run":
        extra = {}
        for v in args.var:
            if "=" in v:
                k, val = v.split("=", 1)
                extra[k] = val
        run_template(config, args.template, args.target, extra)

if __name__ == "__main__":
    main()
