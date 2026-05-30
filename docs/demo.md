# 60-second demo — storyboard & recording script

Goal: a recruiter understands *what this is* and *why it's impressive* in under a
minute. Record the deterministic `make demo` run so it is identical every take.

## Setup for recording
```bash
make demo            # warm the index once, off-camera
clear
```
Record a terminal at ~92 columns. Use a tool like `asciinema`, `terminalizer`, or a
screen recorder + `gifski`. Keep it to ~45–55 seconds.

## Beat sheet (timed)

| Time | On screen | Voice-over / caption |
|------|-----------|----------------------|
| 0:00–0:06 | Title rule + Coach intro panel | "A Six Sigma tutor for the Measure phase — grounded in real methodology." |
| 0:06–0:16 | Maria's two panels (briefing + the "Ppk ~ 1.5, we're fine" claim) | "It role-plays a stakeholder who insists the process is fine." |
| 0:16–0:30 | The four cited coaching panels scroll | "It coaches with retrieved, **cited** guidance — every claim traces to a source." |
| 0:30–0:42 | Rubric table fills in with scores + citations | "Then it **grades the learner** against a rubric — not vibes, evidence." |
| 0:42–0:50 | Verdict + transcript panel | "It verified the numbers itself over MCP: real Ppk 0.64, not capable — the stakeholder's claim was wrong." |
| 0:50–0:55 | Hold on transcript (PLAN + MCP CALL lines) | "Plan, tool calls, and result — fully transparent." |

## The one line to land
"An agent that evaluates the human — grounded in retrieved methodology and in
statistics it verifies itself over MCP."

## Export
Save the result as `docs/demo.gif` so the README embed at the top resolves.
