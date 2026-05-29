"""Guided Measure-phase session: coach + stakeholder + grounded evaluation."""
from __future__ import annotations

import yaml
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ..config import SCENARIO, RUBRIC, DB_PATH, load_env
from ..llm import get_provider
from ..rag.retriever import Retriever, citation
from .tool_client import StatsClient
from .personas import COACH_SYSTEM, stakeholder_system
from .evaluator import Evaluator

_PLAN = [
    "Scope the Measure goal and retrieve the methodology baseline",
    "Hear the stakeholder briefing and record their capability claim",
    "Coach the learner through the Measure steps with cited guidance",
    "Verify the learner's numbers independently via the statistics MCP server",
    "Grade the submission against the Measure rubric, grounded in evidence",
]

_COACH_STEPS = [
    ("data collection plan operational definitions sampling",
     "Start with a data collection plan: operational definitions for the start/stop "
     "events, and a sample spanning operators and shifts."),
    ("measurement system analysis gage R&R",
     "Before trusting the data, sanity-check the measurement system (Gage R&R)."),
    ("process capability Ppk formula overall sigma",
     "With ungrouped individuals, compute overall capability (Pp/Ppk), not Cp/Cpk."),
    ("baseline sigma level DPMO",
     "Close the baseline with a sigma level / DPMO so it is comparable."),
]


class Session:
    def __init__(self, console: Console | None = None):
        load_env()
        self.console = console or Console(width=92)
        self.provider = get_provider()
        self.retriever = Retriever(DB_PATH)
        self.scenario = yaml.safe_load(open(SCENARIO, encoding="utf-8"))
        self.stats = StatsClient()
        self.evaluator = Evaluator(RUBRIC, DB_PATH)
        self.transcript: list[str] = []

    # -- voice helpers -----------------------------------------------------
    def _coach(self, draft: str):
        text = self.provider.say(COACH_SYSTEM, draft)
        self.console.print(Panel(text, title="Coach · Master Black Belt",
                                 border_style="cyan"))

    def _stakeholder(self, draft: str):
        sh = self.scenario["stakeholder"]
        sys = stakeholder_system(sh["name"], sh["role"], sh["voice"])
        text = self.provider.say(sys, draft)
        self.console.print(Panel(text, title=f"{sh['name']} · {sh['role']}",
                                 border_style="magenta"))

    # -- main flow ---------------------------------------------------------
    def run(self, submission: dict):
        sc = self.scenario
        spec = sc["spec"]
        provider_note = f"(LLM voice: {self.provider.name})"
        self.console.rule(f"[bold]DMAIC Coach — {sc['title']}[/]  {provider_note}")

        # 1. scope + grounded intro
        overview = self.retriever.query("Measure phase overview baseline goals", k=1)[0]
        self._coach(
            f"We are in the Measure phase. Goal: establish a trustworthy baseline "
            f"before changing anything. {overview['text'].split(chr(10))[1]} "
            f"{citation(overview)}")
        self.transcript.append(f"PLAN: {' -> '.join(_PLAN)}")

        # 2. stakeholder briefing + claim
        self._stakeholder(sc["briefing"])
        self._stakeholder(sc["stakeholder"]["claim_text"])

        # 3. cited coaching steps
        for query, message in _COACH_STEPS:
            hit = self.retriever.query(query, k=1)[0]
            self._coach(f"{message} {citation(hit)}")

        # present spec + data
        data = sc["data"]
        self._coach(
            f"Specification: LSL={spec['lsl']}, USL={spec['usl']} {spec['unit']} "
            f"(target {spec['target']}). Here is the sample of n={len(data)}. "
            f"Submit your analysis and I will verify it.")

        # 4. independent verification via MCP statistics server
        cap = self.stats.capability(data, lsl=spec["lsl"], usl=spec["usl"],
                                    target=spec["target"])
        oos = sum(1 for x in data if x < spec["lsl"] or x > spec["usl"])
        dp = self.stats.dpmo(oos, len(data))
        verified = {**cap, "baseline_sigma_level": dp["sigma_level"],
                    "observed_out_of_spec": oos}
        for entry in self.stats.log:
            args = {k: v for k, v in entry["args"].items() if k != "data"}
            self.transcript.append(
                f"MCP CALL  dmaic-stats.{entry['tool']}({args}, data[n={len(data)}])")
        self.transcript.append(
            f"VERIFIED  Ppk={verified['Ppk']:.2f}  capable={verified['capable_at_1_33']}  "
            f"baseline_sigma={verified['baseline_sigma_level']:.2f}  "
            f"out_of_spec={oos}/{len(data)}")

        # 5. grounded evaluation
        claim = sc["stakeholder"]["claim_ppk"]
        report = self.evaluator.evaluate(submission, verified, claim)
        self._render_report(submission, verified, claim, report)
        self._render_transcript()
        return report

    # -- rendering ---------------------------------------------------------
    def _render_report(self, submission, verified, claim, report):
        table = Table(title="Measure rubric — grounded evaluation", show_lines=False)
        table.add_column("Criterion", style="bold", width=38)
        table.add_column("Score", justify="center", width=7)
        table.add_column("Evidence / citation", width=44)
        for r in report["criteria"]:
            table.add_row(r["title"], f"{r['score']}/3",
                          f"{r['justification']} {r['citation']}")
        self.console.print(table)
        verdict = (f"Score {report['total']}/{report['max']} ({report['pct']}%). "
                   f"Verified Ppk={verified['Ppk']:.2f} → "
                   f"{'CAPABLE' if verified['capable_at_1_33'] else 'NOT capable'}; "
                   f"stakeholder claimed Ppk≈{claim}. "
                   f"Learner {'correctly challenged' if submission.get('challenged_claim') else 'did not challenge'} it.")
        self.console.print(Panel(verdict, title="Verdict", border_style="green"))

    def _render_transcript(self):
        body = "\n".join(self.transcript)
        self.console.print(Panel(body, title="Reasoning & tool-call transcript",
                                 border_style="yellow"))
