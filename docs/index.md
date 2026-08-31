# The tlDR Engine Handbook

This is a practical guide to building a game with the **tlDR Engine** — an independent, 1:1 DELTARUNE engine written in GameMaker.

It is not a feature list. It is a set of walkthroughs that each end with something running on your screen, plus a reference you can come back to when you forget a field name.

## Who this is for

You know a little GML — enough to read a `for` loop without panicking — and you want to build a game, not study an engine. You have never shipped a DELTARUNE-style battle before.

If you have never played DELTARUNE or Undertale, start with [How a fight works](battle-system/overview.md). The genre makes assumptions that are invisible from the outside, and every design decision in the battle system follows from them.

## How to read this

The chapters are meant to be read in order the first time, but each one stands on its own.

<div class="grid cards" markdown>

- **[Getting started](getting-started/installation.md)**

    Get the project open, get it running, and fix the one thing that bites every non-English speaker on day one.

- **[Overworld](overworld/rooms-and-collision.md)**

    Rooms, collision, NPCs, dialogue and tiles — everything outside of combat.

- **[Battle system](battle-system/overview.md)**

    The heart of the engine. Start with the concepts, then build a complete enemy from scratch.

- **[Reference](reference/enemy-struct.md)**

    Field-by-field tables for `enemy()`, `enc_set()` and the turn object.

</div>

## The one habit worth building

GML structs accept any field you assign to them. Assigning `maxhp` when the engine reads `max_hp` produces **no error at all** — the field is simply created, sits there, and is never read. Half of all "why doesn't this work" in this engine is a misspelled struct field.

So: **copy from a working example rather than typing from memory**, and when something silently does nothing, suspect the field name first.

!!! tip "Your fastest feedback loop"
    Press ++tab++ in game to open the console. `encounter_select` starts any battle instantly, `room_select` jumps to any room, `party_select` changes who is in your party, and `encounter_end` ends the current turn. You will use `encounter_select` more than any other tool in this book — never build a room just to test a fight.

## Conventions used here

Code blocks say which file they belong to on the first line:

```gml
// scripts/rpg_enc_enemies/rpg_enc_enemies.gml
function rpg_enemy_sonso() : enemy() constructor {
    name = "Sonso"
}
```

References to engine source look like `objects/o_enc/Step_0.gml:321` — path, then line. Everything in this book was checked against the source rather than remembered, and those references are there so you can check too.

!!! info "Verified against engine commit `7308e305`"
    Line numbers drift as the engine changes. Paths and behaviour are far more stable than the numbers — if a reference does not line up, search for the surrounding code instead.

The game runs at **30 frames per second**. Every duration in this book is in frames, and 30 frames is one second. This trips people up constantly, because most GameMaker tutorials assume 60.

## Credits

The tlDR Engine is by **tweenko**, MIT licensed, with libraries by Juju Adams and futuregamer25, and a soul/box system loosely based on Callum's (jevilhumor). The [engine repository](https://github.com/profsergiocosta/tldr-engine) and its [Discord](https://discord.gg/x3t8JTyC2p) are the places to go for things this handbook does not cover.
