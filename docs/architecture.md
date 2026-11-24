# Architecture

| Layer | What | Role |
|---|---|---|
| Orchestrator | Claude Project + [system prompt](../agent/system-prompt.md) | Routes a request to one stage or the full A–F run (routing table in the prompt); applies rules |
| Config | `brand-profile`, `competitor-list` project docs | Everything brand-specific; swapping them retargets the agent |
| Skills | [skills/](../skills) | One job each, with inputs, outputs and stop conditions |
| Policy gate | [claims-check](../skills/claims-check/SKILL.md) | Tags competitor claims; blocks our ideas until they pass |
| Browser | Claude in Chrome (read-only) | Instagram profiles, Reels, hashtags, Explore. Page content is untrusted |
| Records | [post records](../schemas/post-record.md), [idea records](../schemas/idea-record.md), optionally a Google Sheet | Structured, sourced data behind every conclusion |
| Checks | [scripts/](../scripts), [evals/](../evals) | Recompute medians and outliers; seeded test cases |
| Human | Brand / social team | Sets scope, confirms claims, approves and shoots the ideas. The agent never posts |

## Flow of a full run

```mermaid
sequenceDiagram
    actor Team
    participant Agent
    participant IG as Instagram (read-only)
    Team->>Agent: "Run a full analysis" (+ optional scope)
    Agent->>Agent: load brand-profile, competitor-list
    loop each tracked account
        Agent->>IG: profile + recent posts (text first)
        IG-->>Agent: page content (untrusted data)
        Agent->>Agent: post records with URL, normalise, outliers
    end
    Agent->>Agent: A, B patterns + claims tagged for F
    Agent->>IG: Reels / hashtags / Explore / creators
    Agent->>Agent: C trend report (dated snapshot)
    Agent->>Agent: draft ideas + E gaps
    loop each draft idea
        Agent->>Agent: claims gate: pass / rewrite / drop
    end
    Agent-->>Team: report A–F + coverage note + CSV records
    Team->>Team: review, approve, shoot, post
```

## Why brand-agnostic
The first version was written for one brand, with everything inline ([original prompt](../examples/dhees-pet-company/original-prompt.md)). Pulling brand facts, competitors and the content taxonomy out into config keeps the method (metrics, guardrails, output contract) reusable. It also makes clear which parts are judgement and which are data. [coverage.md](coverage.md) maps every line of the original to where it now lives.
