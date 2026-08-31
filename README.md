# The tlDR Engine Handbook

A practical guide to building a DELTARUNE-style game with the
[tlDR Engine](https://github.com/profsergiocosta/tldr-engine).

Part of the **[LambdaGeo](https://lambdageo.github.io/ebooks/)** collection of
open textbooks.

Not a feature list — a set of walkthroughs that each end with something running
on screen, plus a reference for when you forget a field name.

> **This book is under construction, and written by a beginner.**
> Please read the section below before relying on it.

## Who is writing this, and why

I am not a game developer. I have never shipped a game, and until recently I had
never opened GameMaker.

I am the **father of a DELTARUNE fan**. My kid wanted to make something in that
world, so I went looking for a way in, found the tlDR Engine, and started taking
notes as I worked out how it fits together. This book is those notes, cleaned up.

That matters for two reasons:

**I ask beginner questions.** Why does my accent not show up? Where exactly does
this code go? Why does my trigger do nothing? Those are not interesting
questions to someone who already knows the engine, which is precisely why they
are rarely written down — and why each one cost me an afternoon. They are
answered here.

**I cannot trust my instincts, because I have none yet.** So I check everything.
Every claim was traced back to a specific line of engine source, which is why the
text is full of references like `objects/o_enc/Step_0.gml:321`. When something
surprised me I went and read the code instead of guessing, and several times the
guess would have been wrong.

That verification work was done with the help of **Claude**, an AI assistant,
reading the engine source alongside me. The writing, the structure, the decisions
about what deserves a chapter, and every mistake that survived, are mine.

Chapters are written as I learn, in the order I needed them. Some are thorough
because I got stuck there for days; others are thin because I have not needed
them yet. Things will move, get rewritten, and occasionally be wrong.

I am sharing it anyway, because the path in was harder than it needed to be and
it seems worth leaving a trail.

## Thanks to the tlDR Engine

None of this would be worth writing about if the engine were not so carefully
built. Coming from software engineering rather than game development, what struck
me most was how much of the design is genuinely *good architecture*:

- **Enemies and encounters are structs with sensible defaults** — inherit and
  override only what you care about. A working enemy is fifteen lines.
- **The object hierarchy does real work.** Your attack inherits from `o_turn` and
  gets its timing for free; `o_enc_box` inherits from `o_enc_box_solid`, which is
  why dropping an extra wall into the arena simply works.
- **Hooks are inert until used.** Every `ev_*` field sits at `-1` doing nothing
  until you assign a function.
- **Localization is a layer, not a sprinkle** — text and fonts resolve through
  `loc()` and a JSON map.
- **Examples are separated from the engine** with an `ex_` prefix, keeping your
  own scripts clean and engine updates easy to pull.
- **There is real tooling.** The in-game console turns a twenty-minute test cycle
  into a five-second one. Someone thought hard about the experience of *building*
  with this, not just playing it.

Thank you to **tweenko** and everyone who contributed. This book is only an
attempt to lower the first step for the next person who arrives the way I did.

## Reading it locally

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

mkdocs serve      # http://127.0.0.1:8000
mkdocs build      # static site in ./site
```

Pushing to `main` publishes to GitHub Pages automatically
(`.github/workflows/deploy.yml` runs `mkdocs gh-deploy`).

## Contents

| Part | |
|---|---|
| **Getting Started** | installing the project; getting accented characters to render |
| **The Overworld** | rooms, collision, NPCs, dialogue, tiles |
| **The Battle System** | how a fight works; a complete worked enemy; the arena; advanced patterns |
| **Reference** | `enemy()`, `enc_set()`, the turn object |

## About the engine references

**Verified against tlDR Engine commit `7308e305`.** Line numbers drift as the engine
changes; file paths and behaviour are far more stable than the numbers. If a
reference does not line up, search for the surrounding code instead — and please
open an issue.

## Contributing

Contributions are genuinely welcome, from anyone at any level. Especially:

- **corrections** — a step that did not work when you followed it is the most
  valuable thing you can report, and worth more than anything I could write from
  the outside
- engine references that have gone stale
- behaviour that differs from what is described
- whole chapters on things I have not reached yet

If you know the engine well, I would rather be corrected than be polite about it.

## Licence

The handbook text is CC BY 4.0. The tlDR Engine itself is MIT, © tweenko.
