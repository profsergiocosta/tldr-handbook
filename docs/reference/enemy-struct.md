# Reference: `enemy()`

The struct that defines one creature. Base definition: `scripts/enc_enemies/enc_enemies.gml`.

You define an enemy by inheriting from it:

```gml
function my_enemy() : enemy() constructor {
    name = "Something"
    // override only what you need — everything else has a usable default
}
```

!!! danger "Misspelled fields never error"
    GML structs accept any assignment. Writing `maxhp` creates a new field that nothing reads, with no warning. When a value seems to be ignored, check the spelling before anything else.

---

## Identity

| Field | Default | Meaning |
|---|---|---|
| `name` | `"Test"` | Displayed name |
| `obj` | `o_actor_e` | The actor object drawn on screen. Must inherit from `o_actor_e` |

## Stats

| Field | Default | Meaning |
|---|---|---|
| `hp` | `170` | Current health |
| `max_hp` | `170` | Maximum health — **note the underscore** |
| `attack` | `0` | Attack stat |
| `defense` | `0` | Defence stat |
| `status_effect` | `""` | Status text shown next to the name |
| `carrying_money` | `0` | Money awarded on defeat |
| `element` | `undefined` | Element, for resistance calculations |

## Mercy and sparing

| Field | Default | Meaning |
|---|---|---|
| `mercy` | `0` | The MERCY bar, 0–100. **At 100 the SPARE button becomes usable** |
| `can_spare` | `true` | Whether this enemy is sparable at all. **Must be a boolean** |
| `mercy_add_pity_percent` | `20` | MERCY granted by a failed spare attempt |
| `no_mercy_text` | *(a line)* | Shown when the player tries to spare too early |
| `tired` | `false` | TIRED state. Mercy spells look for it |
| `low_hp_tired` | `true` | Become TIRED automatically at low HP |
| `low_hp_tired_threshold` | `1/2` | HP fraction below which that happens |

!!! danger "`can_spare` is a bool, never a function"
    It is read in direct boolean context every frame while drawing the MERCY bar (`objects/o_enc/Draw_64.gml:229`) and again in `scripts/enc_actions/enc_actions.gml:369`. A method there crashes at runtime.

    "Only sparable when the bar is full" is already the default behaviour — the button is gated on `mercy >= 100` (`objects/o_enc/Create_0.gml:184`), not on this field.

## ACTs

| Field | Default | Meaning |
|---|---|---|
| `acts` | one sample "Check" | Array of ACT structs — the ACT submenu |
| `acts_special` | `{}` | One entry per party member name, appearing in **their** MAGIC menu |
| `acts_special_desc` | localized | Label for the special-action group |

### The shape of one ACT

```gml
{
    name: "Pet",                  // menu label
    desc: "Scratch behind the ears",  // description panel
    party: [],                    // who can use it — see below
    tp_cost: 0,                   // optional, 0 by default
    color: c_white,               // menu colour; may be callable

    enabled: true,                // bool or function — greys the entry out
    perform_act_anim: true,       // play the default ACT animation
    return_to_idle_sprites: true, // restore idle sprites afterwards

    exec: function(slot, user) { ... },
    exec_args: []                 // extra arguments, appended after (slot, user)
}
```

### The `party` field

| Value | Meaning |
|---|---|
| `[]` | Anyone can use it |
| `["susie"]` | Susie only |
| `["susie", "ralsei"]` | Joint ACT — requires **both** in the party, shows both icons |
| `-1` | Whole-party ACT |

Listing a character who is not in the party simply hides the entry, with no error.

### The `exec` signature

```gml
exec: function(slot, user) { ... }
```

- `slot` — the enemy's index in `o_enc.encounter_data.enemies`
- `user` — the **name** of the acting party member, a string (`"kris"`)
- Further arguments come from `exec_args`, in order

The engine calls it as `method_call(act.exec, array_concat([target, acting_member], exec_args))` (`scripts/enc_actions/enc_actions.gml:93`).

!!! warning "`self` is not the enemy inside `exec`"
    Unlike `dialogue`, `exec` lives inside a struct literal in an array, so it is not bound to the `enemy()`. Reach the enemy explicitly:

    ```gml
    var me = o_enc.encounter_data.enemies[slot];
    ```

## Text

| Field | Default | Meaning |
|---|---|---|
| `dialogue` | `"Test"` | The speech bubble each round. String, or a function |
| `dia_bubble_off_x` / `_off_y` | `0` | Bubble offset |
| `dia_bubble_off_type` | `BUBBLE_RELATIVE.TO_DEFAULT_POS` | What the offset is relative to |
| `dia_bubble_sprites` | box + spike | Bubble sprites |

!!! warning "`dialogue` receives no arguments"
    The base's comment claims it can take the slot as arg0, but the call site is `variable_callable_to_value(enemies[i].dialogue)` — **with no arguments** (`objects/o_enc/Step_0.gml:254`). Writing `function(slot)` gives you `undefined`.

    If you need the index, use `self.slot`, which the engine fills in (`objects/o_enc_anim/Alarm_1.gml:69`). To read your own fields from inside, define it with `method(self, function() { ... })`.

!!! info "The bubble uses a different font"
    It is rendered with `{preset(enemy_text)}`, which switches the font to `loc_font("enc")` — a **different asset** from ordinary dialogue. See [Fonts and accents](../getting-started/fonts-and-accents.md).

## Sprites

| Field | Default | Meaning |
|---|---|---|
| `s_idle` | virovirokun | Idle |
| `s_hurt` | virovirokun | Taking damage |
| `s_spare` | virovirokun | After being spared |

`s_idle` is swapped to `s_spare` automatically when mercy reaches 100 (`scripts/enc_scripts/enc_scripts.gml:111`).

## Battle behaviour

| Field | Default | Meaning |
|---|---|---|
| `turn_object` | `o_turn_default` | The object that runs this enemy's attack |
| `freezable` | `false` | Can be frozen |
| `defeat_marker` | `0` | `m_id` of the marker where it lands on defeat |
| `run_away` | `true` | Flees on fatal damage; `false` means it dies |
| `hurt_sound` | `snd_hurt` | Damage sound |
| `recruit` | `new enemy_recruit()` | Recruitment data |

## Hooks

All default to `-1` (disabled). Assign a function to activate.

| Hook | Called |
|---|---|
| `ev_init` | one frame after `o_enc` is created |
| `ev_pre_dialogue` | before the dialogue phase |
| `ev_party_exec` | when party actions execute |
| `ev_dialogue` | during the dialogue phase, after turn objects exist |
| `ev_turn` | during the turn |
| `ev_turn_start` | as the defence phase begins |
| `ev_post_turn` | after the turn — **`turn_count` has already been incremented** |
| `ev_win` | on victory |
| `ev_hurt` | when the enemy is hurt |

!!! warning "`ev_hurt` runs before the damage is applied"
    In `scripts/enc_scripts/enc_scripts.gml:31` the hook is called first, and `enemy_struct.hp -= hurt` comes after. The `hp` you read inside is the pre-hit value. It is also called with **no arguments**.

To read your own fields inside a hook, bind it:

```gml
ev_hurt = method(self, function() {
    if hp <= max_hp * 0.4
        mood = "annoyed"
})
```

## System fields

Set by the engine. Read them; do not assign them.

| Field | Meaning |
|---|---|
| `actor_id` | The on-screen instance of this enemy |
| `slot` | This enemy's index in the encounter |

`actor_id` is how you animate the creature during its own attack — the turn object reaches it through `enemy_struct.actor_id`.

## Useful functions

```gml
enc_enemy_add_spare(slot, percent, sfx)        // add MERCY
enc_enemy_add_spare_from_var(slot, inst, var)  // MERCY from a variable
enc_enemy_set_tired(slot, true)                // set TIRED
enc_hurt_enemy(slot, amount, user, sfx, fatal) // deal damage
enc_enemy_is_fighting(slot)                    // still in the fight?
enc_enemy_count(only_alive)                    // how many enemies
party_heal(name, amount, caller)               // heal a party member
```
