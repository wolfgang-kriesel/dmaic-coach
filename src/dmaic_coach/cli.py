"""Command-line entry point for DMAIC Coach."""
from __future__ import annotations

import argparse

import yaml
from rich.console import Console

from .config import SCENARIO, DB_PATH, KB_DIR, load_env
from .rag.ingest import ingest
from .rag.store import VectorStore
from .agent.session import Session


def _ensure_index():
    if VectorStore(DB_PATH).count() == 0:
        ingest(KB_DIR, DB_PATH)


def _load_submission(path):
    return yaml.safe_load(open(path, encoding="utf-8"))


def _ask(prompt, cast=str, default=None):
    raw = input(prompt).strip()
    if not raw:
        return default
    if cast is bool:
        return raw.lower().startswith("y")
    try:
        return cast(raw)
    except ValueError:
        return default


def _interactive_submission(console: Console) -> dict:
    console.print("[bold]Enter your Measure-phase analysis:[/]")
    return {
        "ppk": _ask("  Your Ppk estimate: ", float, 0.0),
        "capable": _ask("  Is the process capable? [y/N]: ", bool, False),
        "baseline_sigma": _ask("  Baseline sigma level: ", float, 0.0),
        "challenged_claim": _ask("  Did you challenge the stakeholder's claim? [y/N]: ", bool, False),
        "notes": _ask("  Notes (one line): ", str, ""),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="dmaic-coach",
        description="RAG-backed Six Sigma Measure tutor that guides, simulates a "
                    "stakeholder, and grades your analysis over MCP.")
    parser.add_argument("--demo", action="store_true",
                        help="run a deterministic scripted session (no input needed)")
    args = parser.parse_args(argv)

    load_env()
    console = Console()
    _ensure_index()
    session = Session(console=console)

    if args.demo:
        submission = _load_submission(SCENARIO.parent / "sample_submission.yaml")
    else:
        submission = _interactive_submission(console)

    session.run(submission)


if __name__ == "__main__":
    main()
