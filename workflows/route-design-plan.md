# Route Design Plan

Use this workflow before placing tiles, props, enemies, or scripted events.

## 1. Purpose

- Why does the player enter this route?
- What changes when the player completes it?
- Is it a hub, connector, dungeon, boss approach, or optional area?

## 2. Critical path

Describe the shortest understandable route:

`entrance -> first read -> first pressure -> escalation -> safe threshold -> climax -> exit`

## 3. Optional branch

- Where does the player notice the branch?
- What risk or challenge does it contain?
- What meaningful reward does it provide?
- How does the player return to the critical path?

## 4. Pacing

- Early win:
- First danger:
- Rest beat:
- Highest-pressure moment:
- Recovery before climax:

## 5. Readability

- Primary landmark:
- Secondary landmark:
- How is the exit communicated?
- Which paths must not look equally important?

## 6. Encounter logic

- Chokepoint encounter:
- Reward guardian:
- Optional elite:
- Areas that must remain safe:

## 7. Runtime safety

- Return path exists:
- One-way transition is intentional:
- Save or recovery point before boss:
- Victory state changes:
- Post-victory route:

## 8. Acceptance gate

Run:

```bash
mapflow-lint audit --strict route.json
```

Revise routes scoring below 85 before production.

