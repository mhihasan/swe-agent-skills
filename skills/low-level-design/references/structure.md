# Lesson structure

Sheets in order. Scale each to the domain; do not pad a sheet that has nothing to say.

## Title block

System, domain, language, phase count, class count, assertion count, diagram count. These are the reader's warrant that the lesson was executed rather than imagined, so every number must be countable.

## Sheet A — System requirements

Turn the one-line subject into a specification. Functional requirements as prose, each traceable to a later phase. Non-functional requirements that actually constrain the model — "money must reconcile to the minor unit" constrains; "should be scalable" does not. Then an explicit out-of-scope list.

Naming the boundary is part of the lesson. A model that pretends to cover search relevance, tax, and fulfilment teaches less than one that says plainly which subsystems it excludes and why each is its own problem.

## Sheet A2 — Reading the diagrams

A UML notation key: annotated three-compartment classifier, the six relationship types, visibility markers, multiplicity.

Spend a paragraph on aggregation versus composition specifically. Both mean "has a", the distinction is the one readers most often get wrong, and the answer is whether the part dies with the whole.

## Sheet B — Actors and use cases

A use case diagram, plus a table of actors, their use cases, and what each touches.

Then find the split between two actors that shapes the model, and state it in one explicit sentence. In a catalog it is the merchandiser editing shared content versus the store manager editing their own price and stock, which justifies the entire multi-tenant design before any code exists. Every domain has an equivalent — a parking lot has the attendant against the facility owner. Find it, because it lets a later phase be justified from the requirements rather than from a pattern, and that derivation is the part a reader can reuse.

## Phases 1 to N

**Choosing them.** A phase qualifies only if it satisfies all four gates:

1. It produces a working slice — something runnable and demonstrable alone.
2. It introduces exactly one significant idea.
3. It depends only on phases before it.
4. It is the question a reader would naturally ask next, having seen the previous one.

Order by dependency, not importance. At least one phase must be a genuine structural fork — where the obvious model breaks and a different one is required — and the lesson must say so explicitly, because that moment is what the reader came for. If a phase is only reachable by inventing a requirement nobody asked for, cut it.

**Each phase carries, in order:**

- Header with number, title, and one line on what this phase gives you.
- Prose that leads with the trap: what most people reach for here and why it does not hold. The reasoning is the transferable part.
- A UML class diagram for the phase.
- A relationships list in plain words, with cardinality and whether each is composition or reference. This doubles as the text alternative to the diagram.
- One code listing lifted verbatim from the module you ran. Twenty to thirty-five lines — the part carrying the idea, not the whole file. Comment only where the reasoning is invisible from the code.
- Real verified output where the phase produces any.
- At least one decision note, marked as such, first person, at the fork. Say what was rejected and what would change the answer. A note that only restates what the code does is wasted; the value is in the alternative that was not taken.

## Sheet C — The finished model

A full class diagram, packages as UML folder shapes, cross-package edges marked identifier-only.

Then state the partitioning principle. For business systems it is usually rate of change rather than subject similarity — pricing changes weekly, stock changes per order, catalog structure changes quarterly — and saying that is worth more than the diagram. A second figure showing the change-rate partition earns its place.

## Sheet D — Principles and patterns

Not a recitation. Each principle tied to the line where it changed a decision.

Cover, in roughly this order: start with the data; the patterns table with what each one bought; SOLID with the concrete bite for each; cohesion and coupling made measurable; composition over inheritance argued by counterfactual; depend on abstractions; separate creation from use; and keep it simple.

Two things make this sheet credible rather than performative. Name the design's own worst coupling before the reader finds it. And list the patterns you deliberately declined and why — declining one with a reason teaches more than applying one.

The counterfactual is what makes composition-over-inheritance land: show that the inheritance version explodes combinatorially, with the actual multiplication.

## Sheet E — What we left out

A table of omissions, each with an honest one-line account of what the real version would need.

Then a separate paragraph naming the weaknesses in what you did build. A lesson with no self-identified flaws is not credible, and a reader who cannot see the seams learns to trust models further than they should be trusted.

## Sheet F — Exercises

Close by handing the work back. A lesson the reader only reads teaches far less than one they extend.

Give three or four concrete exercises drawn from the model itself: introduce a new requirement and predict which phase's structure breaks first; implement a phase that was only drawn; find the design's worst coupling before reading Sheet D's answer; re-partition the packages by a different principle and say what gets worse.

Each exercise should have a checkable outcome, so a reader working alone can tell whether they got it right.

## Writing constraints

Plain prose and code. No emoji, no status markers, no confidence percentages, no "Executive Summary" headers, no bulleted lists where every item opens with the same verb form. Vary sentence length. Concrete detail over generality.

Never state a fact you have not checked.
