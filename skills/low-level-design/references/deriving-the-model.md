# Deriving the model

`structure.md` says what the finished walkthrough contains. This says how to get there from a one-line subject — the procedure that turns "design a parking lot" into twelve classes with justified relationships.

The method is adapted from the method chapters of Grokking the Object-Oriented Design Interview, which precede its case studies. See `designgurus-model.md` for the source and for where this skill parts company with it.

## A note on ordering

The source runs five steps — requirements, actors, classes, relationships, then code last. That is the order for *deriving a design*, and it is right.

It is not the order for *authoring a walkthrough*, where the implementation must be green before any prose exists. There is no contradiction: derive the model in the order below, write it as running code, and only then write the lesson around it. Do not read "code last" as licence to publish unexecuted listings.

## Step 1 — Bound the subject

A requirement is one thing the system must do, written so you can tell whether the design does it. "Customers can pay at the exit" qualifies. "The parking lot should be good" does not.

Four questions, in order:

1. **Who uses this?** The actors — people and systems that touch the product. Each brings requirements the others do not.
2. **What can each of them do?** One actor at a time. Each action is a use case. Most of the list comes from here.
3. **What are the limits?** Numbers and rules. How many floors, how long a hold lasts, how many books a member may keep. Limits become constants and validation.
4. **What is out of scope?** The most valuable question and the one most often skipped. It is the only one of the four that makes the problem smaller.

Aim for eight to twelve in-scope lines. Every class you write later should trace back to one of them, and a class that traces to nothing is a class nobody asked for.

**Two habits make the list usable.**

*Write the number.* Not "a member can borrow a few books" but "a member can hold at most five books at a time". The number becomes a constant, and the constant becomes a check in one method.

*Name the actor.* Not "books can be reserved" but "a member can reserve a copy that is currently on loan". Now you know which class the method belongs on.

A requirement written this way is almost a test. You can point at a method and say this line is where requirement five lives.

## Step 2 — Find the classes

**Collect candidates.** Underline every noun in the requirements. The list will be too long, and that is fine — it is a candidate list, and its value is that nothing in it was invented. Underline the verbs too. Verbs become methods, and each one must end up on a class.

**Cut what is not a class.** Five tests:

1. **Is it a value rather than a thing?** An hour is a number. A licence plate is a string. Cash and card are two values of one payment type. Values become fields or enum constants.
2. **Is it the same thing under another name?** Customer and driver are one actor. Merge and pick one name.
3. **Does it have state that changes?** A spot is free or occupied, so it is a class. An hour never changes, so it is not.
4. **Does anything ask it a question?** A candidate becomes a class when other code needs to call it.
5. **Does this type differ in behaviour, or only in a value?**

The fifth test removes more candidates than the other four together, and it is where most designs go wrong.

Compact, large, and handicapped spots all appear in the requirements, and it is tempting to write three classes. Ask what is actually different. Each holds a vehicle, reports whether it is free, and has a number. The only difference is which vehicles fit — a value. One class with a type field covers all three.

Now compare a payment. Cash checks that enough money was handed over; card calls a provider and waits. Different behaviour, so different classes.

**Different data means a field. Different behaviour means a class.**

This is visible in a diagram without reading code: a tree of subclasses whose bodies only pass a different constant to the parent is a field written as several classes.

**Give each class one responsibility**, statable in one sentence that does not need the word "and". When the sentence needs an "and", that is the signal to split. With no clock running there is no excuse not to.

**Place the methods.** Each verb belongs on the class that owns the data it touches. "Find a free spot" touches the collection of spots, which the floor owns. When a method needs data from three classes to do its job, it is in the wrong place — move it to whichever class owns most of what it touches.

**Two invariants worth checking explicitly:**

- A verb with no class to live on means a class is missing.
- A class with no verbs is probably a value.

## Step 3 — Connect the classes

A relationship is a claim about **lifetime** and **substitution**, not about convenience. Getting it wrong is visible in the diagram without reading a line of code.

Ask four questions in order and **stop at the first yes**:

1. **Can B be used anywhere A is expected, with no surprises?** Inheritance. If any method of A would have to be refused, the answer is no.
2. **Does B die when A dies?** Composition.
3. **Is B a part of A, but able to exist on its own?** Aggregation.
4. Otherwise it is a plain association.

Most pairs are plain associations, and that is correct. A design where everything inherits from everything has not been thought about. Choose inheritance last.

**Multiplicity is half the claim.** Saying two classes are associated without saying how many leaves the reader guessing, and the number changes the code: `0..1` means the field can be null and every reader must check; `1..*` means a collection that must never be empty, which is a rule somebody has to enforce. Put a number on every line as you draw it.

**Two inheritance failures cover almost all of them.**

*The subclass that only carries a constant.* Three spot classes whose constructors pass different values to the parent and do nothing else. That is a field. A fourth type should be a new enum constant, not a new class.

*The subclass that must refuse something.* A requirement says a guest cannot place an order, so `Guest extends Customer` — and now a guest has an order the requirement forbids. This is question one failing. Move ordering off the shared parent onto the registered customer, so a guest never inherits what it must refuse.

Both have the same shape: inheritance used to share a little data, by classes that never passed the substitution test.

**When unsure, hold rather than extend.** A `FlyingBird` subclass breaks the moment a penguin arrives; a bird that holds a movement style does not. What an object holds can change at run time. What a class extends cannot.

Inheritance is right when the subclasses genuinely behave differently and every one honours the parent's promises. Cash and card payments both really do take money, differently.

## Step 4 — Run SOLID over the finished diagram

Five checks, not a theory to recite. Run them in this order.

| Check | Quick test | Symptom |
|---|---|---|
| Single responsibility | Name the change that would force an edit. Two unrelated changes means two classes | The responsibility sentence needs an "and" |
| Open/closed | Pick one likely new feature. If it edits three classes, the design is closed to the wrong thing | A switch or if-chain over a type |
| Liskov | Re-check every inheritance arrow against substitution | A method that would have to throw, refuse, or do nothing |
| Interface segregation | Every implementer uses everything it promised | Empty method bodies |
| Dependency inversion | A high-level class names an interface, never a concrete low-level one | A class constructing its own collaborator |

**Calibration matters more than the checks.** Two findings out of five, both real and both explainable in a sentence, is what a good pass looks like. Five findings usually means the design needs rework. **Zero findings usually means the pass was not done properly** — which is the same reason the walkthrough must name its own worst coupling.

Two counter-rules. Do not add an interface with one implementer and no second in sight; that is indirection with no benefit. Do not split past the sentence test — single responsibility taken too far yields thirty two-method classes nobody can hold in their head.

## Step 5 — Name the patterns that fit, and the ones that do not

The repo's `design-patterns-expert` skill covers the full catalogue. What matters here is the signal that says a pattern applies, and the anti-signal that says it does not.

| Pattern | Use when | Do not use when |
|---|---|---|
| Strategy | One operation, several interchangeable rules | One rule, no sign of a second |
| Factory | Creation depends on a type value | One concrete class |
| Observer | Several listeners, and the source should not know them | One listener the source already holds |
| State | A lifecycle with many transitions | Three states and one guarded method |
| Singleton | Exactly one instance, genuinely | You only want convenient global access |
| Builder | Many optional fields | Three required fields |

Strategy is the one that answers "what if the rules change", which is the most common pressure a model faces after it ships.

One or two patterns is the right number for a model this size. A design carrying six is usually no longer following its requirements. **Naming the pattern you rejected is worth as much as naming the one you used** — "strategy for the rate, because a second rate is likely; not state for the ticket, because three statuses need only one guard" shows the pattern and its cost together.

## Where this feeds the walkthrough

Steps 1 and 2 become Sheet A and Sheet B. Step 2's class list and step 3's relationships determine the phase boundaries — a phase that cuts across a composition is usually cutting in the wrong place. Step 4's findings are what Sheet D and Sheet E are honest about. Step 5 fills the patterns table, including its declined column.
