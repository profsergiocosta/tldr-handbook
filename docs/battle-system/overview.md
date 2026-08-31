# How a fight works

Before any code: this genre makes assumptions that are invisible from the outside. If you have never played DELTARUNE or Undertale, the engine's design will look arbitrary until you understand what it is modelling.

---

## Part 1 — The design

### Every fight is a conversation

A tlDR battle is a hybrid of two things that do not normally mix: a **turn-based menu** and a **bullet hell** — a real-time dodging game.

The important difference from a traditional RPG is that **you are almost never required to kill anything**. Every fight has two endings:

- **Violent** — reduce the enemy's HP to zero (`Fight`).
- **Peaceful** — convince the enemy to stop fighting and spare it (`Act` + `Spare`).

The genre is designed so the peaceful route is *equally valid*, sometimes more interesting. That changes the player's question from "how do I win" to "how do I make this creature stop fighting me".

### The menu

Each party member gets a row of **five buttons** (`objects/o_enc/Create_0.gml:82`):

| Button | What it does |
|---|---|
| **FIGHT** | Real damage. Reduces `hp`. |
| **ACT** *or* **MAGIC** | One shared slot. It is **ACT** for a character who has the `item_s_act` spell, and **MAGIC** otherwise. |
| **ITEM** | Use an inventory item. |
| **SPARE** | Only usable when some enemy has `mercy >= 100`. Ends the fight peacefully. |
| **DEFEND** | Damage taken drops to 2/3 and the turn gets shorter. |

!!! warning "Only Kris has ACT"
    In the shipped party data, only Kris carries `item_s_act` (`scripts/party_init/party_init.gml:152`). Susie, Ralsei and Noelle show **MAGIC** in that slot instead. If you test a fight with Susie selected and cannot find the ACT button, that is why — not a bug.

    To give the other characters an enemy-specific action, use the sibling field `acts_special`, which has one entry per character name and appears inside their MAGIC menu. There is a worked example on the virovirokun in `scripts/enc_enemies/enc_enemies.gml:239`.

Choices are resolved in a fixed order regardless of the order you picked them (`objects/o_enc/Create_0.gml:126`):

```text
act → item → power → spare → fight → defend
```

### MERCY, the hidden bar

Every enemy has an internal **MERCY** value from 0 to 100. At 100, **SPARE** becomes usable.

Two things are easy to confuse:

- **`mercy`** (number, 0–100) — this is what **enables the SPARE button**. The engine literally checks `_enemy.mercy >= 100` (`objects/o_enc/Create_0.gml:184`).
- **`can_spare`** (**boolean**, default `true`) — whether this enemy is sparable *in principle*. If `false`, the MERCY bar is drawn crossed out and SPARE never works, whatever the mercy value.

!!! danger "`can_spare` must be a bool, not a function"
    The engine reads it in direct boolean context, every frame, while drawing the bar (`objects/o_enc/Draw_64.gml:229`) and again in `scripts/enc_actions/enc_actions.gml:369`. A method there crashes at runtime. If you want "only sparable when full", that is already the default — leave `can_spare = true`.

What raises MERCY:

- Using the **right ACT** for that specific enemy, sometimes several in sequence.
- Leaving the enemy at **low HP** without killing it. With `low_hp_tired = true` (the default) and HP below `low_hp_tired_threshold` (default `1/2`), it becomes **TIRED** — a state that mercy spells look for.
- Failing to spare: if `can_spare` is true, each failed attempt still adds `mercy_add_pity_percent` (default **20**).

### ACTs are where the character lives

An ACT is not a generic verb. It is written **for that creature**, and it is usually funny, strange, or revealing.

Think of it as an interactive mini-dialogue disguised as a menu: instead of *reading* about the enemy, the player *investigates* it by trying things until something works. That is the whole puzzle.

### The dodging phase does two jobs

Once everyone has chosen, the fight goes visual — the black box, the soul, the bullets. That phase is:

1. **Mechanical** — the enemy's turn. It attacks with a bullet pattern you have to dodge.
2. **Characterisation** — the *shape of the pattern* reflects the creature. A nervous enemy fires slowly and without aim. A furious one fires fast and dense. A playful one makes something silly and almost decorative.

The bullet pattern is not just a reflex test. It is the enemy talking.

### Bullet colours are rules, not physics

This is where tlDR differs most from what people assume.

**The soul never changes.** It is always red and always moves the same way: free in four directions, no gravity, no jump (`enum SOUL_COLOR { RED }`, `objects/o_enc_soul/Create_0.gml:23`). **There is no platforming mode.**

What has colour is the **bullet**, and the colour is a rule about **when that bullet hurts** (`objects/o_enc_bullet/Other_10.gml`):

| `BULLET_COLOR` | Hurts when | What it demands |
|---|---|---|
| **`SOLID`** (default) | always, on contact | dodge — get out of the way |
| **`BLUE`** | only if the soul is **moving** | **stand still** while it passes |
| **`ORANGE`** | only if the soul is **still** | **keep moving** |

`BLUE` and `ORANGE` are mirror images. The player's mental model is "freeze" versus "never stop", and that gives you rhythm variety without inventing new mechanics.

Three non-obvious consequences:

- **`destroy` only applies to `SOLID`.** A blue or orange bullet passes through the soul and keeps existing after hitting.
- **Only `SOLID` bullets grant graze** (`objects/o_enc_soul_grazer/Step_0.gml:12`), so blue and orange give no TP and do not shorten the turn.
- Colours mix freely in one turn. Each bullet carries its own rule.

### The loop, in one sentence

> *"Choose an action → see the result → dodge the counterattack → repeat, until the enemy is ready to be spared (or out of HP)."*

Conscious decision followed by real-time reflex. That is why the genre is sometimes called **turn-based bullet hell**: an RPG in your head, a shooter in your fingers.

---

## Part 2 — The implementation

!!! info "The game runs at 30 FPS"
    `options/main/options_main.yy` sets `option_game_speed: 30`, and nothing calls `game_set_speed` anywhere. Every frame count in this book assumes 30. `timer_end = 60` is **two** seconds, not one.

### Who owns what

| Phase | Object |
|---|---|
| The menu | `o_enc` |
| The arena (visual + surface) | `o_enc_box` |
| The arena walls | `o_enc_box_solid` — `o_enc_box`'s parent |
| The heart | `o_enc_soul` |
| The graze ring around it | `o_enc_soul_grazer` |
| The bullets | `o_enc_bullet`, one instance each |
| One enemy's attack | `turn_object` (`o_turn_*`) |

### `o_enc` — the conductor

`enc_start(set)` creates an `o_enc_anim`, which leads to `o_enc`. It lives from the first frame of the fight to the last and holds the state:

```gml
o_enc.turn_count      // which round (0, 1, 2…)
o_enc.encounter_data  // the enc_set() in use, with its enemies[] array
o_enc.tp              // the magic bar, 0–100, fed by grazing
o_enc.turn_objects    // one turn object per enemy
o_enc.mybox           // the arena instance for this turn
o_enc.mysoul          // the soul instance for this turn
```

### The real order of events

This is the exact sequence from `objects/o_enc/Step_0.gml`, and it is worth memorising because the intuitive version is wrong in two places:

```text
MENU        → you pick actions
EXEC        → actions run (fixed order: act, item, power, spare, fight, defend)
              → ev_party_exec
DIALOGUE    → turn_objects are CREATED     ← the instances already exist here
              → User Event 0 on each turn_object   ("init")
              → ev_dialogue
              → attack targets are chosen
TURN        → o_enc_box and o_enc_soul are created
              → User Event 2 on each turn_object   ("box is created")
              → User Event 1 on each turn_object   ("turn starts")
              → ev_turn_start
              → … the turn runs …
              → ends when EVERY turn_object has been destroyed
              → the box closes
POST_TURN   → turn_count ++                ← already incremented
              → ev_post_turn
```

Two traps:

- **The turn object is created before `ev_turn_start`**, not after. If you need to configure it from an enemy hook, the right place is `ev_dialogue` — or the turn object's own User Events.
- **`turn_count` has already been incremented when `ev_post_turn` runs.** Inside that hook it holds the *next* round's number.

And note what ends a turn: not a timer on `o_enc`, but **every turn object being destroyed**. While one is alive, the box stays open.

### The box

`o_enc_box` is created centred, 75 × 75 by default:

```gml
o_enc_box.x        // centre X
o_enc_box.y        // centre Y
o_enc_box.width    // 75
o_enc_box.height   // 75
```

The walls are **`o_enc_box_solid`**, which is `o_enc_box`'s *parent* — the soul collides against the parent object, so any extra `o_enc_box_solid` instance becomes a wall inside the arena. The box's mask is a **hollow** outline (`spr_enc_box_mask`); a filled mask would leave nowhere to stand.

**Bullets ignore the walls entirely.** Nothing keeps a bullet inside the box. What decides whether it is *drawn* clipped is the `inside` field, not its position.

### The soul

```gml
o_enc_soul.x / .y     // position — aim at this
o_enc_soul.moving     // true only if input was given AND the soul actually moved
o_enc_soul.i_frames   // invincibility frames remaining
o_enc_soul.spd        // base speed (8); holding cancel halves it
```

Collision is detected by the **soul**, not the bullet — there is no Collision event:

```gml
// objects/o_enc_soul/Step_0.gml
if place_meeting(x, y, o_enc_bullet) {
    with instance_place(x, y, o_enc_bullet) {
        event_user(0);     // the bullet's "I hit something" event
    }
}
```

So **User Event 0 on `o_enc_bullet` is the hit event**. That is where the colour rule is checked, i-frames applied and damage dealt.

### Graze

A second object, **`o_enc_soul_grazer`**, follows the soul with a larger area. A **`SOLID`** bullet touching the ring but not the heart counts as a graze, and pays twice:

1. **TP** — the bullet's `graze` value (default 2) is added to `o_enc.tp`, capped at 100. TP pays for spells.
2. **A shorter turn** — the bullet's `time_points` (default 5) is subtracted from `timer_end` on every turn object with `shorten_by_tension = true`.

Rules the engine enforces:

- Only `SOLID` bullets. Blue and orange are worth nothing.
- Grazing the same bullet again pays `graze/12` and `time_points/30` — you cannot farm one bullet.
- No grazing while invincible (`i_frames > 0`), and none in the first 10 frames of a turn.
- The ring's **size** comes from the grazer sprite's scale, and grows with equipped items (`item_a_pink_ribbon` +20%, `item_a_twin_ribbon` +25%, capped at 2.5×).

!!! info "Why graze exists"
    Without it, the optimal play in a bullet hell is to run to the emptiest corner and wait. That is boring — the player becomes a spectator. Graze inverts the incentive: getting close pays. The dodging phase becomes a decision instead of a wait.

### The bullet

The `Step` event of `o_enc_bullet` is **empty**: movement is GameMaker's native `speed`/`direction`. The defaults (`objects/o_enc_bullet/Create_0.gml`):

```gml
enum BULLET_COLOR { SOLID, BLUE, ORANGE }   // defined in the bullet's own Create

graze       = 2                     // TP granted when grazed
att         = 6                     // attack STAT, not damage
inv         = global.enc_soul_inv   // i-frames granted on hit (40)
time_points = 5                     // frames a graze cuts from the turn

color       = BULLET_COLOR.SOLID
destroy     = true                  // vanish on hit — SOLID only
element     = ""
inside      = false                 // draw clipped inside the box?
```

!!! warning "`att` is not damage"
    Damage is `5 * att`, minus the target's defence, times 2/3 if they are defending (`scripts/party_hp/party_hp.gml:225`). So `att: 4` costs about 20 HP, not 4. Think of it on the same scale as an enemy's `attack` stat.

`inside` does **not** control where a bullet spawns. It controls whether it is drawn onto the box's surface — that is, **clipped by the walls** (`objects/o_enc_bullet/Draw_0.gml`). Draw order comes from depth:

```gml
DEPTH_ENCOUNTER.BULLETS_OUTSIDE  // -6500 — in front of everything, soul included
DEPTH_ENCOUNTER.SOUL             // -6400
DEPTH_ENCOUNTER.BOX              // -6300
DEPTH_ENCOUNTER.BULLETS_INSIDE   // -6200 — behind the box frame
```

The bullet's **drawing** lives in User Event 1 (`Other_11.gml`), not `Draw`. In a child bullet object: override `Other_11` for looks, `Other_10` for the hit, `Step_0` for movement.

### The turn object

This is the object **you** write. It inherits from `o_turn`, is created during `DIALOGUE`, and **destroying it is how a turn ends**.

| Event | File | When | For |
|---|---|---|---|
| Create | `Create_0.gml` | once, on birth | your variables |
| User Event 0 | `Other_10.gml` | once, right after Create | **init** — `timer_end`, `pattern_pool` |
| User Event 2 | `Other_12.gml` | once, when box and soul exist | the arena; the base picks `pattern` here |
| User Event 1 | `Other_11.gml` | once, when the turn actually starts | **spawn bullets** |
| Step | `Step_0.gml` | every frame | continuous logic |
| Destroy | `Destroy_0.gml` | on destruction | clean up |

Two separate mechanisms end a turn, and they are easy to confuse:

**`timer_end`** lives in the *parent's* Step, inherited via `event_inherited()`:

```gml
// objects/o_turn/Step_0.gml
if turn_started
    timer ++
if !is_undefined(timer_end) && timer > timer_end
    instance_destroy()
```

`timer` counts **up**, and only after User Event 1. With `timer_end = undefined` the turn never ends on its own.

**`__support_destroy_check()`** does **not** look at `timer_end`. It exists for support enemies (`am_support = true`): it destroys this turn when no *main* turn is left (`objects/o_turn/Create_0.gml:31`). On a normal turn it does nothing.

!!! danger "Nothing collects orphaned bullets"
    Bullets that leave the box keep existing. Every turn object is responsible for its own cleanup, in its Destroy event — the engine does this in `o_ex_turn_complex_box/Destroy_0.gml`. Skip it and the next round starts with last round's litter flying across the screen.

## Where to go next

- [Your first enemy](your-first-enemy.md) — build one end to end.
- [The arena](the-arena.md) — make the box part of the performance.
- [Reference](../reference/enemy-struct.md) — the field tables.
