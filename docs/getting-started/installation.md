# Installation

## What you need

| Requirement | Notes |
|---|---|
| **GameMaker** | The project was last saved with IDE `2024.1400.5.1065`. Opening it in an older IDE will fail; a newer one will offer to upgrade the project format. |
| **Git** | Not strictly required, but the engine ships as a Git repository and you will want the safety net. Fonts and rooms are binary-ish assets that are painful to undo by hand. |
| **A code editor** | Optional. GameMaker's built-in editor is fine; an external one is handy for the batch edits this book occasionally suggests. |

The engine is MIT licensed, so you can ship what you build with it.

## Getting the project

```bash
git clone https://github.com/profsergiocosta/tldr-engine.git
cd tldr-engine
```

Open `tldr-engine.yyp` in GameMaker.

!!! tip "Work on a branch"
    Before you change anything, branch. You will be regenerating font assets and editing rooms, and both produce diffs that are hard to read and easy to get wrong.

    ```bash
    git switch -c my-game
    ```

## First run

Press **Run** (++f5++). You should land in the engine's demo content.

Now open the console with ++tab++ and type `help`. The commands are:

| Command | What it does |
|---|---|
| `room_select` | Jump to any room in the project |
| `encounter_select` | Start any encounter immediately |
| `party_select` | Choose who is in your party |
| `encounter_end` | End the current battle turn |
| `language_switch` | Cycle the language |
| `save_wipe` | Erase save data |

If all of that works, the engine is installed correctly.

## The lay of the land

You do not need to know all of this yet, but it helps to know where things live.

```text
objects/
  o_actor…        the player and party members
  o_actor_e…      enemies, in the overworld and in battle
  o_enc…          everything about a battle in progress
  o_turn…         attack patterns — one object per attack
  o_ow_…          overworld props: NPCs, signs, chests
  o_dev_…         editor helpers you place in rooms
scripts/
  enc_enemies/    the enemy() base struct
  enc_sets/       the enc_set() base struct
  enc_scripts/    battle functions (damage, mercy, starting a fight)
  custom/         engine-wide helpers, including a custom instance_create
  loc/            localization
rooms/
  room_ex_…       example rooms — read these, they are the real documentation
datafiles/loc/    translation and font-mapping JSON
```

!!! note "Where your own content goes"
    The engine keeps its examples in `ex_`-prefixed scripts and expects you to write yours elsewhere. Two empty-ish scripts are already set aside:

    - `scripts/rpg_enc_enemies/rpg_enc_enemies.gml` — your enemies
    - `scripts/rpg_enc_sets/rpg_enc_sets.gml` — your encounters

    Keeping your code out of the `ex_` files makes it much easier to pull engine updates later.

## A custom `instance_create` you should know about

The engine overrides `instance_create` (`scripts/custom/custom.gml:297`):

```gml
function instance_create(obj, xx = 0, yy = 0, dpth = 0, post_var_struct = {})
```

Two things differ from what you might expect, and both matter:

1. The struct is applied **after** the Create event runs, so it overrides defaults instead of being overwritten by them.
2. It only assigns fields that **already exist** on the instance. Inventing a new field in the struct is **silently ignored**.

That second rule catches everyone once. If you need to attach your own data to an instance, either declare the variable in that object's Create event first, or assign it after creation:

```gml
var inst = instance_create(o_enc_bullet, xx, yy, depth);
inst.my_own_field = 5;    // works; passing it in the struct would not
```

## Next

Before you write a line of game code, deal with [fonts and accents](fonts-and-accents.md) if your game is not in English. It affects every string you will ever write, and it is much less annoying to fix now than after you have written a hundred lines of dialogue.
