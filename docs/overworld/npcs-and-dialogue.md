# NPCs and dialogue

Everything the player can talk to, read or open goes through one mechanism. Learn it once and signs, NPCs, chests and examinable scenery all work the same way.

## How interaction works

When the player presses the confirm key, `o_actor` scans **ahead of itself**, 2 to 15 pixels in the direction it is facing, for anything interactable (`objects/o_actor/Step_0.gml:98`):

```gml
if InputPressed(INPUT_VERB.SELECT) {
    for (var w = 2; w < 15; w ++) {
        var __xw = -lengthdir_x(w, dir + 90)
        var __yw =  lengthdir_y(w, dir + 90)

        var __interactable_instances = instance_place_list_ext(x + __xw, y + __yw,
            array_concat([o_ow_interactable, o_actor_interactable], interactable_instances), false)

        for (var i = 0; i < array_length(__interactable_instances); i ++) {
            with __interactable_instances[i] {
                if other._checkmove()
                    event_user(0)
            }
        }
        if array_length(__interactable_instances) > 0
            break;
    }
}
```

Three consequences worth internalising:

- **It scans forwards, not overlapping.** The player has to be facing the thing. Standing on top of it is not enough.
- **The nearest ring wins.** The loop breaks at the first distance that finds anything, so a sign right in front takes priority over an NPC slightly further away.
- **User Event 0 is the interaction event.** Everything below is just different ways of filling it in.

## The two families

| Parent | Use for | Blocks movement? |
|---|---|---|
| **`o_ow_interactable`** | props: signs, chests, scenery | inherits from `o_ow_depthobj`, which sorts by depth |
| **`o_actor_interactable`** | characters that walk, animate, or need actor behaviour | yes — `collide = true` by default |

Both define the same two fields in their Create event:

```gml
interaction_code = function() {}
interaction_args = []
```

and both call it from User Event 0:

```gml
method_call(interaction_code, interaction_args)
```

So the pattern is always the same: **place the instance, fill in `interaction_code` in its Instance Creation Code.**

## A sign

`o_ow_sign` is the minimum case. Its whole implementation is:

```gml
// objects/o_ow_sign/Create_0.gml
text = "* Undefined sign."

// objects/o_ow_sign/Other_10.gml
dialogue_start(text)
```

So all you do in the room is set the text:

```gml
// Instance Creation Code
text = "{col(y)}* Welcome to the test square.{col(w)}{p}{e}"
```

## An NPC

`o_ow_npc` inherits from `o_ow_interactable` and adds a talking animation: while `talking` is true it plays its sprite, and when the text stops it returns to frame 0 (`objects/o_ow_npc/Step_0.gml`).

For anything beyond a single line, open a **cutscene**:

```gml
// Instance Creation Code of an o_ow_npc
interaction_code = function() {
    cutscene_create()

    if memory_get("npcs", id)
        cutscene_dialogue("{char(gerson, 1)}* You again?{p}{e}")
    else {
        cutscene_dialogue("{char(gerson, 0)}* Hello, stranger.{p}{e}")
        cutscene_func(memory_set, ["npcs", id, true])
    }

    cutscene_play()
}
```

That is the whole shape of NPC scripting in this engine:

| Function | What it does |
|---|---|
| `cutscene_create()` | begins a new cutscene |
| `cutscene_dialogue(text)` | queues a dialogue box and waits for it |
| `cutscene_func(fn, [args])` | queues a function call |
| `cutscene_sleep(frames)` | queues a pause |
| `cutscene_play()` | runs the queue |

`memory_get` / `memory_set` give you persistent flags keyed by category and id — the natural way to make an NPC remember it has met you.

!!! tip "Linking the talking animation"
    The `{link(...)}` markup tag ties the typing text to an NPC so it animates while speaking, and `{unlink(...)}` stops it. See `objects/o_text_typer/Other_10.gml:182`.

## Dialogue markup

Text is not plain — it is a small language interpreted by `o_text_typer` as it types. Tags are written in braces. The full list is in `objects/o_text_typer/Other_10.gml`; these are the ones you will actually use.

### Flow

| Tag | Effect |
|---|---|
| `{p}` | pause and wait for the player to press confirm |
| `{c}` | clear the box and continue |
| `{e}` | end the dialogue |
| `{stop}` | stop typing, leave the text up |
| `{s(frames)}` | sleep for N frames |
| `{br}` | line break |
| `{resetx}` | reset the horizontal position |
| `{instant}` | print the rest without typing animation |

`{br}{resetx}` is the pair the engine uses everywhere to start a new line at the left margin. `{p}{e}` is the standard ending for a single box.

### Appearance

| Tag | Effect |
|---|---|
| `{col(c)}` / `{color(c)}` | text colour — `y` for yellow, `w` for white, or a colour name |
| `{reset_col}` | back to the previous colour |
| `{font(name)}` | switch font |
| `{shadow(bool)}` | drop shadow on/off |
| `{scale(n)}`, `{xscale(n)}`, `{yscale(n)}` | size |
| `{xspace(n)}`, `{yspace(n)}` | letter and line spacing |
| `{spr(sprite)}` | draw a sprite inline with the text |
| `{eff(name, …)}` | apply a per-character effect until `{eff_reset}` |

### Characters and voices

| Tag | Effect |
|---|---|
| `{char(name, expression)}` | set the speaking character's portrait and expression |
| `{face(name, expression)}` | portrait only |
| `{f_ex(expression)}` | change the expression mid-line |
| `{voice(sound)}` | the blip sound while typing |
| `{speed(n)}` | typing speed |
| `{mini(text, …)}` | a small secondary box |

### Structure

| Tag | Effect |
|---|---|
| `{choice(a, b, …)}` | present a choice box to the player |
| `{preset(name)}` | apply a whole style preset: `enemy_text`, `god_text`, `light_world` |
| `{box_pos(bool)}` | move the box to the top or bottom of the screen |
| `{link(id)}` / `{unlink(id)}` | animate an NPC while this text types |

!!! warning "`{preset(...)}` changes the font"
    `{preset(enemy_text)}` sets `font = loc_font("enc")` (`objects/o_text_typer/Other_10.gml:98`), which resolves to a **different font asset** from ordinary dialogue. If some text renders without accents while the rest is fine, look for a preset. See [Fonts and accents](../getting-started/fonts-and-accents.md).

## Which function starts the text?

Three entry points, and they behave differently:

| Function | Use when | Notes |
|---|---|---|
| `dialogue_start(text)` | a single box from a prop | returns the instance; freezes the player unless you pass `allow_movement` |
| `cutscene_dialogue(text)` | inside a cutscene | queued, waits for the player |
| `encounter_scene_dialogue(text)` | **inside a battle** | wraps the text in a cutscene that pauses the fight |

Using the wrong one is a classic bug: `dialogue_start()` inside a battle opens the overworld box in the wrong place. In combat, always `encounter_scene_dialogue()`.

## Chests and other props

`o_ow_chest` follows the same recipe — it is an `o_ow_interactable` whose `interaction_code` gives an item and remembers it was opened. When you need a new kind of prop, the fastest route is:

1. Create an object, parent it to **`o_ow_interactable`**.
2. `event_inherited()` first line of Create.
3. Set `interaction_code` per instance in the room, or once in the object's Create if every instance behaves the same.

If the prop should also block movement or animate like a character, parent it to **`o_actor_interactable`** instead.

## Common problems

| Symptom | Cause |
|---|---|
| Nothing happens when you press confirm | the object is not parented to `o_ow_interactable` or `o_actor_interactable` |
| It only works from one side | expected — the scan is directional; the player must face it |
| The dialogue box opens in the wrong place during a fight | used `dialogue_start()` instead of `encounter_scene_dialogue()` |
| The NPC does not animate while talking | `talking` is never set — use the `{link(...)}` tag |
| The text prints the tags literally | a typo in the tag name; unknown commands are not errors |
| The NPC forgets it met you | `memory_set` was never called, or it ran outside the cutscene queue |
| Accents missing only in battle bubbles | `{preset(enemy_text)}` uses a different font — see [Fonts and accents](../getting-started/fonts-and-accents.md) |
