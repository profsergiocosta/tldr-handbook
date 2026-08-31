# The tlDR Engine Handbook

Welcome to a practical guide to building a game with the **[tlDR Engine](https://github.com/profsergiocosta/tldr-engine)** — an independent, 1:1 DELTARUNE engine written in GameMaker. This book is not a feature list: it is a set of walkthroughs that each end with something **running on your screen**, followed by a reference you can come back to when you forget a field name.

Part of the **[LambdaGeo](https://lambdageo.github.io/ebooks/)** collection of open textbooks.

!!! note "A work in progress, written by a beginner"
    I am not a game developer — I am the father of a DELTARUNE fan, learning GameMaker and writing down what I find. This book is unfinished, it changes often, and corrections are genuinely welcome. There is more about that [below](#who-is-writing-this-and-why).

---

## 📋 About this book

| | |
|---|---|
| **Who it is for** | Anyone who can read a `for` loop in GML and wants to build a game rather than study an engine |
| **Prerequisites** | GameMaker installed; no prior DELTARUNE-style battle experience assumed |
| **Structure** | 9 chapters in 3 parts, plus 3 reference pages |
| **Status** | Work in progress — written as I learn, and still moving |
| **Engine version** | Verified against tlDR Engine commit `7308e305` |
| **Licence** | Text under CC BY 4.0. The engine itself is MIT, © tweenko |

If you have never played DELTARUNE or Undertale, start with **[How a fight works](battle-system/overview.md)**. The genre makes assumptions that are invisible from the outside, and every design decision in the battle system follows from them.

---

## 🙋 Who is writing this, and why

I am not a game developer. I have never shipped a game, and until recently I had never opened GameMaker.

I am the **father of a DELTARUNE fan**. My kid wanted to make something in that world, so I went looking for a way in, found the tlDR Engine, and started taking notes as I worked out how it fits together. This book is those notes, cleaned up.

That matters for two reasons, and you should know both before you rely on anything here.

**The first is that I ask beginner questions.** Why does my accent not show up? Where exactly does this code go? Why does my trigger do nothing? Those are not interesting questions to someone who already knows the engine, which is precisely why they are rarely written down — and why every one of them cost me an afternoon. They are answered here.

**The second is that I cannot trust my instincts**, because I have none yet. So I check everything. Every claim in this book was traced back to a specific line of engine source, which is why you keep seeing references like `objects/o_enc/Step_0.gml:321`. When something surprised me, I went and read the code instead of guessing — and several times the guess would have been wrong.

That verification work was done with the help of **Claude**, an AI assistant, reading the engine source alongside me. The writing, the structure, the decisions about what deserves a chapter, and every mistake that survived, are mine.

!!! warning "This book is under construction"
    Chapters are written as I learn, in the order I needed them. Some parts are thorough because I got stuck there for days; others are thin because I have not needed them yet. Things will move, get rewritten, and occasionally be wrong.

    If you find an error, or a step that did not work when you followed it, please [open an issue](https://github.com/profsergiocosta/tldr-handbook/issues) — a correction from someone who actually hit the problem is worth more than anything I could write from the outside. Contributions of whole chapters are very welcome too.

---

## 🙏 Thanks to the tlDR Engine

None of this would be worth writing about if the engine were not so carefully built. Coming from software engineering rather than game development, what struck me most was how much of the design is genuinely *good architecture*, not just working code:

* **Enemies and encounters are structs with sensible defaults.** You inherit from `enemy()` or `enc_set()` and override only what you care about. A working enemy is fifteen lines.
* **The object hierarchy does real work.** Your attack inherits from `o_turn` and gets its timing for free; `o_enc_box` inherits from `o_enc_box_solid`, which is why dropping an extra wall into the arena simply works, with no extra system.
* **Hooks are inert until you use them.** Every `ev_*` field sits at `-1` doing nothing until you assign a function. No callbacks to register, no interfaces to implement.
* **Localization is a layer, not a sprinkle.** Text and font choices resolve through `loc()` and a JSON map, so a whole game can change language without touching a line of GML.
* **Examples are separated from the engine.** Everything demonstrative is prefixed `ex_`, leaving your own scripts clean and engine updates easy to pull.
* **There is real tooling.** The in-game console — `encounter_select`, `room_select`, `party_select` — turns a twenty-minute test cycle into a five-second one. Someone thought hard about the experience of *building* with this, not just playing it.

Thank you to **tweenko** and everyone who contributed to it. This book is only an attempt to lower the first step for the next person who arrives the way I did.

---

## 🎯 Structure

### 📘 Part 1 — Getting Started

Getting the project open, getting it running, and fixing the one thing that bites every non-English speaker on day one.

* **[Installation](getting-started/installation.md)** — requirements, first run, the console commands you will live in, and the engine's custom `instance_create`
* **[Fonts and accents](getting-started/fonts-and-accents.md)** — why `á` renders as nothing, and the seven steps that fix it for good

### 📙 Part 2 — The Overworld

Everything outside of combat: the rooms the player walks through and the things they talk to.

* **[Rooms and collision](overworld/rooms-and-collision.md)** — the three objects every room needs, the layer-depth convention, walls, warps and triggers
* **[NPCs and dialogue](overworld/npcs-and-dialogue.md)** — the interaction scan, cutscenes, and the full dialogue markup language
* **[Tiles and tilesets](overworld/tiles-and-tilesets.md)** — the 20×20 grid, layer ordering, and a practical order for building a room

### 📗 Part 3 — The Battle System

The heart of the engine, built up from concepts to a complete, playable enemy.

* **[How a fight works](battle-system/overview.md)** — the design ideas first, then the objects that implement them
* **[Your first enemy](battle-system/your-first-enemy.md)** — nine steps from an empty file to a fight with a personality
* **[The arena](battle-system/the-arena.md)** — making the box, the background and the enemy count part of the performance
* **[Advanced patterns](battle-system/advanced-patterns.md)** — custom bullets, animated paths, support enemies, and scaling difficulty

### 📕 Reference

Field-by-field tables for the three structures you will write most often: **[`enemy()`](reference/enemy-struct.md)**, **[`enc_set()`](reference/enc-set.md)** and the **[turn object](reference/turn-object.md)**.

---

## 💡 The one habit worth building

GML structs accept any field you assign to them. Writing `maxhp` when the engine reads `max_hp` produces **no error at all** — the field is simply created, sits there, and is never read. Half of all "why doesn't this work" in this engine is a misspelled struct field.

So: **copy from a working example rather than typing from memory**, and when something silently does nothing, suspect the field name first.

!!! tip "Your fastest feedback loop"
    Press ++tab++ in game to open the console. `encounter_select` starts any battle instantly, `room_select` jumps to any room, `party_select` changes your party, and `encounter_end` ends the current turn.

    You will use `encounter_select` more than any other tool in this book — never build a room just to test a fight.

---

## 📐 Conventions

Code blocks name the file they belong to on the first line:

```gml
// scripts/rpg_enc_enemies/rpg_enc_enemies.gml
function rpg_enemy_sonso() : enemy() constructor {
    name = "Sonso"
}
```

References to engine source look like `objects/o_enc/Step_0.gml:321` — path, then line. Everything here was checked against the source rather than remembered, and those references are there so you can check too.

!!! info "Verified against engine commit `7308e305`"
    Line numbers drift as the engine changes. Paths and behaviour are far more stable than the numbers — if a reference does not line up, search for the surrounding code instead.

The game runs at **30 frames per second**. Every duration in this book is given in frames, and 30 frames is one second. This trips people up constantly, because most GameMaker material assumes 60.

---

## 📚 Credits and further reading

* **tlDR Engine** by **tweenko** — MIT licensed. [Repository](https://github.com/profsergiocosta/tldr-engine) · [Discord](https://discord.gg/x3t8JTyC2p)
* Libraries by [Juju Adams](https://www.jujuadams.com/) and [futuregamer25](https://futuregamer25.github.io/)
* The soul and box system is loosely based on the one created by **Callum** (jevilhumor)
* The engine's own `room_ex_*` rooms and `ex_`-prefixed scripts are the best documentation there is — this book points at them constantly
