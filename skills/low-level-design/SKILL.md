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

1. **Derive the model.** Bound the subject, find the classes, connect them, then run the seven principles and SOLID over the result — both before any code, while the model is still cheap to change. The procedure is in `references/deriving-the-model.md` — do not skip to classes from a one-line subject.
2. **Build and run the implementation.** One runnable file per phase, plus the final module and its test file. Everything green before any prose. See `references/verification.md`.
3. **Choose phases from the domain**, not from a template. Four gates in `references/structure.md`.
4. **Draw the diagrams** with `scripts/umlgen.py`. Notation key, use case, one class diagram per phase, activity, sequence, state, finished model. See `references/uml-toolkit.md`.
5. **Write the sheets** around the verified listings. Structure in `references/structure.md`.
6. **Verify the prose and the rendering.** Measure sentence length before publishing, then render in a browser and check clipping, theme, and overflow. Both are non-optional; see `references/verification.md`.
7. **Check the result** against the checklist in `references/designgurus-model.md`.

### Quick reference

| Element | Rule |
|---|---|
| Phase count | From the domain. Never a fixed number carried in from another walkthrough. |
| Structural fork | At least one phase must be the moment the obvious model breaks. Name it as such. |
| Prose per phase | Lead with the trap, then the fix. The reasoning transfers; the code does not. |
| Decision notes | Four parts: the choice, the rejected alternative stated fairly, what the choice costs, and what would reverse it. |
| Prose | ASD-STE100 Simplified Technical English. One idea per sentence, 20 words typical, 25 hard maximum. Active voice. One term per concept. |
| Diagrams | Hand-authored inline SVG on CSS tokens. Never screenshots, never an external library. |
| Numbers | Counted with a command. Never estimated. |
| Every class | Exercised by the running code. A class nothing calls is a box on a diagram. |
| Justification | Every class, field, and method traces to a numbered requirement or to a named rule it enforces. State the trace; do not leave it implied. |
| Runnable phases | Two files per phase: the module with a demo `__main__`, and a `unittest` file beside it. The pair runs alone. The page names the file and command beside each listing. |
| Tests | `unittest`, one method per rule, named after the rule. The demo prints; the tests assert. Never both in one block. |
| Requirements | Write the number, name the actor. A number becomes a constant; an actor names the owning class. |
| Subtypes | Different data means a field. Different behaviour means a class. |
| Relationships | Substitution, then lifetime, then part-of. Stop at the first yes. Inheritance last. |
| The seven principles | Run over the model before the code, not reported over the code after. Sheet D states where each one bit. |
| SOLID pass | Two findings is healthy. Zero means the pass was not done. |
| Omissions sheet | Includes self-identified weaknesses in what you did build. |

### Red flags — stop and fix

- About to write a section before the code for it runs
- Writing "roughly forty classes" instead of running `grep -c`
- A diagram whose arrowhead direction you did not check against the dependency direction
- Publishing without rendering the page in a browser
- A walkthrough with no self-identified flaws — not credible, teaches nothing
- A sentence over 25 words, or one holding two ideas behind a dash or colon
- Two words used for one concept — "listing" in one paragraph, "store product" in the next
- A decision note that names no cost, or claims a free win
- A fork whose reasoning is an adjective rather than a count, a number, or a test result
- Running the seven principles after the implementation is written, where they can only produce a flattering report
- A Sheet D principle entry that restates the principle instead of naming what it changed
- All seven principles reported as clean passes, with none of them in tension and none producing a finding
- Every phase reads as a smooth success, so the reader never sees a model break
- Reaching for a screenshot of a diagram tool instead of authoring SVG
- A subclass whose body only passes a different constant to its parent — that is a field
- A subclass that has to refuse one of its parent's methods — that is a broken hierarchy
- A verb from the requirements with no class to live on — a class is missing
- A class name that traces back to no requirement
- A field or method that traces back to nothing — it is scaffolding, and it should be deleted or justified
- A phase whose code cannot be run without the other phases present
- Bare `assert` statements in a `__main__` block, where the first failure hides the rest
- A phase module showing its final-form classes rather than the model as it stood
- Test method names that do not say which rule they check
- Test internals — `assertEqual` calls, fixture plumbing — quoted on the page
- Code that lives only in a scratch directory, so the reader cannot run what the page shows
- A listing on the page with no file name and no command beside it

### Common mistakes

**Guessing counts.** Count classes, count assertions, quote real output.

**Trusting `getBBox()` for clipping.** It ignores ancestor `transform`, so grouped class boxes go uncounted and every diagram reports clean. Measure from the SVG root.

**Arrowheads by habit.** A dependency points *at* the thing depended on. An aggregation or composition diamond sits at the *owning* end.

**Spending page width on chrome.** A sidebar costs roughly 270px that diagrams pay for in shrunken text.

### Output

**The deliverable is a folder in the user's current project, not a scratch directory.** Ask where it goes if the repo has no obvious home. A walkthrough whose code lives somewhere the reader cannot open is a walkthrough they cannot run, and the page's listings then have no warrant.

```
<project>/<subject-slug>/
├── README.md                    how to run every phase and the final system
├── index.html                   the walkthrough page
├── run_all.sh                   every demo, then every test
├── phases/
│   ├── phase1_<name>.py         model at that phase + a __main__ demo
│   ├── test_phase1_<name>.py    its tests, one method per requirement
│   ├── phase2_<name>.py         ...
│   └── test_phase2_<name>.py
├── <subject>.py                 the final accumulated model
└── test_<subject>.py            tests over the final model
```

**Lay it out the way production code is laid out: a module, and its tests beside it.** Two files per phase. The module holds the model and a short `__main__` demo. The tests live in a sibling `test_` file that imports the module.

**The module's `__main__` block is a demo, not a test.** It prints a readable walk through the phase using real domain data, and it asserts nothing. That printed output is what the page quotes as verified output. Bare `assert` in `__main__` is a script: the first failure aborts, and nothing reports what passed.

**Tests use `unittest` from the standard library.** One `TestCase` per requirement or per closely-related group, and **one test method per rule**. Name the method after the rule it checks — `test_a_store_cannot_price_in_a_currency_it_does_not_sell_in` — so a failure report names the requirement that broke. Assertions carry the requirement number in the class docstring, not scattered in comments.

**A phase pair runs alone.** Copy `phase3_overrides.py` and `test_phase3_overrides.py` into an empty directory, delete everything else, and both still work. A test importing its own module is correct and mirrors production. A phase importing *another phase* is not: it breaks reading one pair in isolation and couples the teaching order to an import graph.

Phase modules therefore repeat code from earlier phases on purpose, and each shows the model **as it stood at that phase** — not its final form. If phase 3's `Store` has a `pricing` field that phase 6 introduces, the snapshot is lying about when the design acquired it.

The page then quotes listings **from these files**, and names the file and command beside each listing so a reader can run the thing they just read.

Publish `index.html` as an artifact too when the user wants a shareable link — load `artifact-design` before writing it, and derive the visual identity from the subject's own world. The folder is the deliverable; the artifact is a view of it.

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
