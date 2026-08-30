---
name: low-level-design
description: Use when working out the low-level design of a system — a parking lot, an elevator bank, a product catalog, a ride dispatcher, a vending machine — either to produce a worked walkthrough of the model, or to be drilled on building one live against requirements revealed one at a time. Covers LLD and OOD, object and domain modelling, class diagrams, UML, and where design patterns earn their place. For the high-level, distributed side, use system-designing instead.
---

# Low-level design

Scope is inside one service: classes, responsibilities, relationships, and the patterns that earn their place. Replication, sharding, and consistency across machines are the high-level counterpart — `system-designing` covers those.

## Pick the mode first. Always ask.

This skill has two modes with **opposite constraints**. One works from a complete requirement list; the other withholds the next requirement on purpose. Running the wrong one wastes the session and teaches the wrong reflex.

**The mode is a required input. If the person did not name it, ask before doing anything else** — before reading files, before naming a system, before writing a line.

> "Two modes here — do you want a **walkthrough** of the finished model, or a **drill** where I reveal requirements one at a time and you write the code? Which one?"

| Mode | You produce | Requirements | Diagrams | Who writes the code |
|---|---|---|---|---|
| `walkthrough` | A staged, illustrated study document | All known up front | Yes, throughout | You |
| `drill` | A live timed exercise | One at a time, next one hidden | None | **The person being drilled** |

**No default.** Not "walkthrough seems more likely". Not "they said parking lot, so probably a walkthrough". A named system tells you the subject, never the mode.

### Red flags — you are about to guess

- "They probably want the lesson" — ask
- "The last session was a walkthrough" — ask
- "Drill mode needs a system anyway, I'll start there" — ask first, then get the system
- Reading `structure.md` or `running-a-drill.md` before the mode is confirmed
- Producing anything at all before hearing the answer

---

## Mode: walkthrough

Produces a staged, illustrated walkthrough of one system's low-level design: requirements, actors, a model that accumulates phase by phase, UML throughout, running code, and the reasoning behind every fork.

**Core principle: the code runs before the prose exists.** A document written first and verified later contains listings that do not execute, output that was imagined, and counts that were guessed — and the reader cannot tell which parts are real.

The sheet structure derives from Grokking's parking lot lesson; `references/designgurus-model.md` captures that model, and the checklist at its end is what a finished walkthrough gets validated against.

### What makes it a walkthrough rather than a design doc

A design document states the final answer. A walkthrough shows the model being arrived at, including the moment the obvious approach stops working. The reader should be able to predict the next phase before reading it, and be corrected when they are wrong.

Three things carry that weight: leading each phase with the trap rather than the fix, naming the structural fork explicitly, and recording the reasoning at each decision in the first person.

### Steps

1. **Derive the model.** Bound the subject, find the classes, connect them, run SOLID over the result. The procedure is in `references/deriving-the-model.md` — do not skip to classes from a one-line subject.
2. **Build and run the implementation.** One module, one test file, green before anything else. See `references/verification.md`.
3. **Choose phases from the domain**, not from a template. Four gates in `references/structure.md`.
4. **Draw the diagrams** with `scripts/umlgen.py`. Notation key, use case, one class diagram per phase, activity, sequence, state, finished model. See `references/uml-toolkit.md`.
5. **Write the sheets** around the verified listings. Structure in `references/structure.md`.
6. **Verify rendering in a browser** — clipping, theme, overflow. Non-optional; see `references/verification.md`.
7. **Check the result** against the checklist in `references/designgurus-model.md`.

### Quick reference

| Element | Rule |
|---|---|
| Phase count | From the domain. Never a fixed number carried in from another walkthrough. |
| Structural fork | At least one phase must be the moment the obvious model breaks. Name it as such. |
| Prose per phase | Lead with the trap, then the fix. The reasoning transfers; the code does not. |
| Decision notes | First person, at the fork, explaining what was rejected and why. |
| Diagrams | Hand-authored inline SVG on CSS tokens. Never screenshots, never an external library. |
| Numbers | Counted with a command. Never estimated. |
| Every class | Exercised by the running code. A class nothing calls is a box on a diagram. |
| Requirements | Write the number, name the actor. A number becomes a constant; an actor names the owning class. |
| Subtypes | Different data means a field. Different behaviour means a class. |
| Relationships | Substitution, then lifetime, then part-of. Stop at the first yes. Inheritance last. |
| SOLID pass | Two findings is healthy. Zero means the pass was not done. |
| Omissions sheet | Includes self-identified weaknesses in what you did build. |

### Red flags — stop and fix

- About to write a section before the code for it runs
- Writing "roughly forty classes" instead of running `grep -c`
- A diagram whose arrowhead direction you did not check against the dependency direction
- Publishing without rendering the page in a browser
- A walkthrough with no self-identified flaws — not credible, teaches nothing
- Every phase reads as a smooth success, so the reader never sees a model break
- Reaching for a screenshot of a diagram tool instead of authoring SVG
- A subclass whose body only passes a different constant to its parent — that is a field
- A subclass that has to refuse one of its parent's methods — that is a broken hierarchy
- A verb from the requirements with no class to live on — a class is missing
- A class name that traces back to no requirement

### Common mistakes

**Guessing counts.** Count classes, count assertions, quote real output.

**Trusting `getBBox()` for clipping.** It ignores ancestor `transform`, so grouped class boxes go uncounted and every diagram reports clean. Measure from the SVG root.

**Arrowheads by habit.** A dependency points *at* the thing depended on. An aggregation or composition diamond sits at the *owning* end.

**Spending page width on chrome.** A sidebar costs roughly 270px that diagrams pay for in shrunken text.

### Output

Default to a published HTML artifact — load `artifact-design` before writing it, and derive the visual identity from the subject's own world. Markdown works for a repo file; keep the same structure and replace SVG with labelled text diagrams.

---

## Mode: drill

A live, timed exercise. You act as the interviewer. **The person being drilled writes all the code.** You reveal one requirement, wait, critique what they built, then reveal the next.

The full protocol is in `references/running-a-drill.md`. Read it before starting — the reveal discipline is the entire value, and it is easy to break by accident.

Four rules that decide whether the drill is worth anything:

1. **Never reveal a requirement before the current one runs.** Not a preview, not a hint about direction, not "you might want to make that pluggable".
2. **Never write their code.** When they stall, name the fork, not the fix.
3. **Critique in the window** — after the stage works, before the next reveal. Two or three sentences on structure, not style.
4. **Score at the end**, against the rubric in `running-a-drill.md`, with at least two things they actually lost points on.

`references/deriving-the-model.md` is the hidden answer key: it tells you what the model should converge to, so the critique is grounded rather than impressionistic. It is for your eyes during a drill, never pasted to them.
