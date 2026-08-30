---
name: low-level-design
description: Use when working out the low-level design of a whole system — a parking lot, an elevator bank, a product catalog, a ride dispatcher, a vending machine — and a worked, staged walkthrough is wanted rather than a short answer or a bare code dump. Covers LLD and OOD, object and domain modelling, class diagrams, UML, and where design patterns earn their place. For the high-level, distributed side, use system-designing instead.
---

# Low-level design

Produces a staged, illustrated walkthrough of one system's low-level design: requirements, actors, a model that accumulates phase by phase, UML throughout, running code, and the reasoning behind every fork.

Scope is inside one service: classes, responsibilities, relationships, and the patterns that earn their place. Replication, sharding, and consistency across machines are the high-level counterpart — `system-designing` covers those.

**Core principle: the code runs before the prose exists.** Everything else here is downstream of that. A lesson written first and verified later contains listings that do not execute, output that was imagined, and counts that were guessed — and the reader cannot tell which parts are real.

## What makes it a walkthrough rather than a design doc

A design document states the final answer. A lesson shows the model being arrived at, including the moment the obvious approach stops working. The reader should be able to predict the next phase before reading it, and be corrected when they are wrong.

Three things carry that weight: leading each phase with the trap rather than the fix, naming the structural fork explicitly, and recording the reasoning at each decision in the first person, so the reader inherits a way of thinking rather than a finished artifact.

## Workflow

1. **Build and run the implementation.** One module, one test file, green before anything else. See `references/verification.md`.
2. **Choose phases from the domain**, not from a template. Four gates in `references/structure.md`.
3. **Draw the diagrams** with `scripts/umlgen.py`. Notation key, use case, one class diagram per phase, activity, sequence, state, finished model. See `references/uml-toolkit.md`.
4. **Write the sheets** around the verified listings. Structure in `references/structure.md`.
5. **Verify rendering in a browser** — clipping, theme, overflow. Non-optional; see `references/verification.md`.

## Quick reference

| Element | Rule |
|---|---|
| Phase count | From the domain. Never a fixed number carried in from another lesson. |
| Structural fork | At least one phase must be the moment the obvious model breaks. Name it as such. |
| Prose per phase | Lead with the trap, then the fix. The reasoning transfers; the code does not. |
| Decision notes | First person, at the fork, explaining what was rejected and why. |
| Diagrams | Hand-authored inline SVG on CSS tokens. Never screenshots, never an external library. |
| Numbers | Counted with a command. Never estimated. |
| Omissions sheet | Includes self-identified weaknesses in what you did build. |

## Red flags — stop and fix

- About to write a section before the code for it runs
- Writing "roughly forty classes" instead of running `grep -c`
- A diagram whose arrowhead direction you did not check against the dependency direction
- Publishing without rendering the page in a browser
- A lesson with no self-identified flaws — not credible, teaches nothing
- Every phase reads as a smooth success, so the reader never sees a model break
- Reaching for a screenshot of a diagram tool instead of authoring SVG

## Common mistakes

**Guessing counts.** A stated number a reader can check is worth more than a vague one. Count classes, count assertions, quote real output.

**Trusting `getBBox()` for clipping.** It ignores ancestor `transform`, so grouped class boxes go uncounted and every diagram reports clean. Measure from the SVG root.

**Arrowheads by habit.** A dependency points *at* the thing depended on. An aggregation or composition diamond sits at the *owning* end. Both are easy to draw backwards and both are read as errors by anyone fluent in UML.

**Spending page width on chrome.** A sidebar costs roughly 270px that diagrams pay for in shrunken text. Put navigation in a horizontal strip and let figures span the container.

## Output

Default to a published HTML artifact — load `artifact-design` before writing it, and derive the visual identity from the subject's own world rather than a generic docs look. Markdown works for a repo file; keep the same structure and replace SVG with labelled text diagrams.
