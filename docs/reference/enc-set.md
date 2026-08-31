# Reference: `enc_set()`

The struct that defines one **encounter** — who is fighting, where they stand, what plays, and how it ends. Base definition: `scripts/enc_sets/enc_sets.gml`.

```gml
function my_encounter() : enc_set() constructor {
    debug_name = "my_fight"
    enemies = [ new my_enemy() ]
}
```

!!! info "`enemy()` vs `enc_set()`"
    An `enemy()` is a **creature**: its stats, its ACTs, its attack. An `enc_set()` is a **scene**: which creatures show up, the music, the round text, the win condition. The same enemy can appear in many encounters.

    The single most common mix-up is putting `flavor` on the enemy. It belongs here.

---

## Identity and cast

| Field | Default | Meaning |
|---|---|---|
| `debug_name` | `"undefined"` | The name shown in the console's `encounter_select` |
| `enemies` | `[]` | Array of `new …()` enemy instances |

Each `new` is an independent struct — two of the same enemy have separate HP, MERCY and state.

!!! info "How many enemies fit"
    No limit in code, but the name list is drawn at `375 + 30*i` in a 480px-tall interface (`objects/o_enc/Draw_64.gml:190`). In practice **3 is comfortable, 4 is tight**. The engine's own examples use 2.

## Text

| Field | Default | Meaning |
|---|---|---|
| `flavor` | a function | The line shown above the menu each round. String **or** function |

```gml
flavor = function() {
    if o_enc.turn_count == 0
        return "* Two Slimes block the path!"

    return choose(
        "* Slime wobbles gently.",
        "* Slime makes a wet noise."
    )
}
```

It is evaluated through `enc_get_flavor()` (`scripts/enc_scripts/enc_scripts.gml:227`), which calls it with no arguments.

## Positioning

| Field | Default | Meaning |
|---|---|---|
| `enemies_pos` | `undefined` | Where each enemy stands |
| `party_pos` | a function | Where each party member stands |

`enemies_pos` takes either an array of triples or a function:

```gml
// [x, y, relative?] per enemy
enemies_pos = [
    [ -4,  -6, true ],     // true  = offset from the default spot
    [ -14,  6, true ],
]

// or a function, useful when the count varies
enemies_pos = function(i, xx, yy) {
    return [ xx - i*10, yy ]
}
```

`party_pos` is a function of the member index:

```gml
party_pos = function(i) {
    return [
        guipos_x() + 52,
        guipos_y() + 130 - 22 * party_length() + i*44,
    ]
}
```

!!! warning "Always add `guipos_x()` / `guipos_y()`"
    These are the camera's position (`scripts/custom/custom.gml:2`). Absolute coordinates drift as soon as the camera is not at the origin.

## Presentation

| Field | Default | Meaning |
|---|---|---|
| `bg_type` | `ENC_BG.GRID` | Background. Only two values: `ENC_BG.GRID` or `ENC_BG.NONE` |
| `bgm` | `mus_battle` | Music |
| `bgm_pitch` | `1` | Pitch |
| `bgm_gain` | `1` | Volume |

With `ENC_BG.NONE` the grid disappears but the darkening veil (`o_eff_bg.fade`) remains. To build your own background, see [The arena](../battle-system/the-arena.md#63-level-2-your-own-background).

## Rules

| Field | Default | Meaning |
|---|---|---|
| `win_condition` | all enemies gone | Function returning `bool`; `true` ends the fight |
| `can_change_turnlen` | `true` | Whether defending shortens the turn |
| `display_target` | `false` | Show which party member is about to be hit |
| `target_calculation` | `ENC_TARGET.RANDOM` | How the enemy picks a target |
| `target_recalculate_condition` | `undefined` | When to re-pick targets mid-turn |
| `enc_var_struct` | `{}` | Free-form variables shared across the encounter |

`ENC_TARGET` has three values (`scripts/enc_scripts/enc_scripts.gml:303`): `RANDOM`, `ANY`, `ALL`. `target_calculation` may also be a function returning an array of party indices.

### Custom win conditions

```gml
win_condition = function() {
    if o_enc.turn_count >= 3            // survive three rounds
        return true

    for (var i = 0; i < array_length(o_enc.encounter_data.enemies); ++i)
        if enc_enemy_is_fighting(i)
            return false

    return true                          // default: nobody left fighting
}
```

Evaluated while actions execute (`objects/o_enc/Step_0.gml:216`), so the fight ends on the round after the condition is met.

## Party actions

| Field | Default | Meaning |
|---|---|---|
| `party_actions` | one default action per member | Extra actions offered in this encounter |

The base fills it automatically:

```gml
for (var i = 0; i < party_length(); ++i)
    struct_set(party_actions, global.party_names[i],
               [new item_s_defaultaction(global.party_names[i])])
```

Set it back to `{}` to strip the default actions from a specific encounter.

## Hooks

Same names as on `enemy()`, all defaulting to `-1`, but scoped to the **whole encounter** rather than one creature.

| Hook | Called |
|---|---|
| `ev_init` | one frame after `o_enc` is created |
| `ev_party_turn` | at the start of the party's turn |
| `ev_party_exec` | when party actions execute |
| `ev_pre_dialogue` | before the dialogue phase |
| `ev_dialogue` | during the dialogue phase |
| `ev_turn` | during the turn |
| `ev_turn_start` | as the defence phase begins |
| `ev_post_turn` | after the turn |
| `ev_win` | on victory |

`ev_init` is the natural place to spawn scene objects — a custom background, a weather effect, a controller for a scripted fight.

## Starting the encounter

| Form | Notes |
|---|---|
| `enc_start(new my_encounter())` | The plain function |
| `new my_encounter()._start()` | Identical — `_start()` just calls `enc_start(self)` (`scripts/enc_scripts/enc_scripts.gml:157`) |
| `encounter` Variable Definition on an `o_actor_e` | Starts when the player touches the actor |
| From a trigger's `trigger_code` | See [Rooms and collision](../overworld/rooms-and-collision.md#triggers) |

## Complete example

```gml
function rpg_enc_set_slimes() : enc_set() constructor {
    debug_name = "slimes"

    enemies = [
        new rpg_enemy_slime(),
        new rpg_enemy_slime(),
    ]

    flavor = function() {
        if o_enc.turn_count == 0
            return "* Two Slimes block the path!"
        return "* The air smells of jelly."
    }

    enemies_pos = [
        [ -4,  -6, true ],
        [ -14,  6, true ],
    ]

    bg_type = ENC_BG.GRID
    bgm     = mus_battle

    ev_init = function() {
        // scene setup goes here
    }
}
```
