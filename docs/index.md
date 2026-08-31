# The tlDR Engine Handbook

Welcome to a practical guide to building a game with the **[tlDR Engine](https://github.com/profsergiocosta/tldr-engine)** — an independent, 1:1 DELTARUNE engine written in GameMaker. This book is not a feature list: it is a set of walkthroughs that each end with something **running on your screen**, followed by a reference you can come back to when you forget a field name.

Part of the **[LambdaGeo](https://lambdageo.github.io/ebooks/)** collection of open textbooks.

---

## 📋 About this book

| | |
|---|---|
| **Who it is for** | Anyone who can read a `for` loop in GML and wants to build a game rather than study an engine |
| **Prerequisites** | GameMaker installed; no prior DELTARUNE-style battle experience assumed |
| **Structure** | 9 chapters in 3 parts, plus 3 reference pages |
| **Engine version** | Verified against tlDR Engine commit `7308e305` |
| **Licence** | Text under CC BY 4.0. The engine itself is MIT, © tweenko |

If you have never played DELTARUNE or Undertale, start with **[How a fight works](battle-system/overview.md)**. The genre makes assumptions that are invisible from the outside, and every design decision in the battle system follows from them.

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
