# Installation

## What you need

| Requirement | Notes |
|---|---|
| **GameMaker** | The upstream project was last saved with IDE `2026.1.0.27` (`IDEVersion` in `tldr-engine.yyp`, as of November 2026). Opening it in an older IDE may fail; a newer one will offer to upgrade the project format. Check that field if GameMaker complains. |
| **Git** | Not strictly required, but the engine ships as a Git repository and you will want the safety net. Fonts and rooms are binary-ish assets that are painful to undo by hand. |
| **A code editor** | Optional. GameMaker's built-in editor is fine; an external one is handy for the batch edits this book occasionally suggests. |

The engine is MIT licensed, so you can ship what you build with it.

## Getting the project

The engine's author asks you **not** to just download or clone the repository. Create a repository of your own and pull the engine into it, so that you can take future updates with a normal `git pull` (see [Updating the engine](#updating-the-engine) below).

1. Install [GitHub Desktop](https://desktop.github.com/) if you do not have it.
2. Create an empty repository on the GitHub website, then clone it with GitHub Desktop.
3. Open that repository in a terminal (Command Prompt on Windows) and fetch the engine into it:

    ```bash
    git fetch https://github.com/tweenko/tldr-engine.git main
    git reset --hard FETCH_HEAD
    ```

    The official documentation writes the second command with a URL instead of `FETCH_HEAD`; `git reset` needs a commit, so `FETCH_HEAD` (the commit you just fetched) is what actually works.

4. Publish your repository with the big **Publish** button in GitHub Desktop (press *Fetch origin* first if you cannot see it).

Open `tldr-engine.yyp` in GameMaker.

!!! note "About the repository this book links to"
    The official engine is [`tweenko/tldr-engine`](https://github.com/tweenko/tldr-engine). Some line references in this book were checked against a fork, `profsergiocosta/tldr-engine`; behaviour is the same, but when in doubt, treat the official repository as the source of truth. The engine's own [documentation](https://docs.google.com/document/d/14SpnU32P-_HLdNS17gwaIe8Z2mO8AG1KUUGMe_hNdzM/edit?tab=t.0) and [Discord](https://discord.gg/x3t8JTyC2p) are the places to ask when this book is silent.

!!! tip "Work on a branch"
    Before you change anything, branch. You will be regenerating font assets and editing rooms, and both produce diffs that are hard to read and easy to get wrong.

    ```bash
    git switch -c my-game
    ```

## First run

Press **Run** (++f5++). You should land in the engine's demo content.

The first build can take a few minutes; later runs are much faster.

Now try the debug console. It is **not** a text prompt — you never type a command. **Hold ++tab++**, and a small box reading `tab+` appears in the top-left corner. **Keep holding ++tab++ and hold a letter**; when the bar under the command name fills, the command runs (`scripts/console/console.gml`):

| Hold with ++tab++ | Command | What it does |
|---|---|---|
| ++h++ | Help | Shows every command on screen |
| ++r++ | Room Select | Jump to any room in the project |
| ++e++ | Encounter Select | Start any encounter immediately |
| ++p++ | Party Select | Choose who is in your party |
| ++i++ | Item Select | Give yourself any item |
| ++w++ | End an Encounter | Leave the current battle |
| ++t++ | Max out TP | Fill the TP bar |
| ++m++ | Toggle Mute BGM | Mute the music |
| ++l++ | Switch Language | Cycle the language |
| ++d++ | Wipe Save Files | Erase save data |
| ++n++ | Open Intro Sequence | Play the intro |

Inside any picker, ++up++ / ++down++ move, ++enter++ confirms and ++esc++ cancels.

If ++tab++ + ++h++ shows that list, the engine is installed correctly.

## The lay of the land

In the GameMaker Asset Browser you will see two groups made by the engine's authors, **`@Engine`** and **`zzz Examples`**. These are IDE groups, not folders on disk. `@Engine` holds the parts that make up the DELTARUNE mechanics; you may edit them, but every change makes updating harder, so keep such edits small. `zzz Examples` holds the test rooms and recreated DELTARUNE areas.

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
    The engine keeps its examples in `ex_`-prefixed scripts and expects you to write your own game content in dedicated scripts (in Part 3, we guide you to create these):

    - `scripts/rpg_enc_enemies/rpg_enc_enemies.gml` — your enemies
    - `scripts/rpg_enc_sets/rpg_enc_sets.gml` — your encounters

    Keeping your code out of the `ex_` files makes it much easier to pull engine updates later.

## Where to make your first changes

Almost everything you will want to change globally lives in `o_world`:

- **Default party** — `global.party_names` is set in the Game Start event (`objects/o_world/Other_2.gml:141`, with a comment marking the spot).
- **Starting inventory and settings** — also in `o_world`; the Create and Game Start events are the ones that matter, the others rarely do.

Everything else (enemies, encounters, items, party members) is a **constructor**, and constructors can live in any script. Make one new script per kind of constructor, for example `rpg_enc_enemies`, instead of editing the engine's own.

## Naming convention

The engine suggests this scheme for your own assets:

```text
{asset type}_{project prefix}_{category}*_{identifier}_{state}*_{substate}*     (* = optional)
spr_g_rune_togore_down_happy_light
```

Asset-type prefixes: none for scripts, `o_` objects, `spr_` sprites, `room_` rooms, `shd_` shaders. The engine's own examples use the project prefix `ex_`; pick another for your game so your assets never collide with the examples. *State* and *substate* let code find a variant by appending to a sprite name.

## Updating the engine

Updating only works if you set the project up as described above. Commit your work first, then in a terminal opened in your repository:

```bash
git pull --no-rebase https://github.com/tweenko/tldr-engine.git main
```

If an editor opens asking for a commit message, fill it in and close it. Then open GitHub Desktop, resolve any merge conflicts (an editor such as Visual Studio Code makes this easier), and push. Conflicts are most likely in files you edited inside `@Engine`, which is another reason to keep your content in your own scripts.

## A custom `instance_create` you should know about

The engine overrides `instance_create` (`scripts/custom/custom.gml:315`):

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
