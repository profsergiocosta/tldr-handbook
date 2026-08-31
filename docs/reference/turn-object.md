# Reference: the turn object

The object that runs one enemy's attack. You write one per attack; it inherits from **`o_turn`** (`objects/o_turn/`).

The single most important fact: **destroying the turn object is how the turn ends.** The battle waits until every turn object is gone.

---

## Setting one up

1. **Create → Object**, no sprite.
2. **Parent: `o_turn`** — without this, nothing works.
3. Add events with **Add Event**. When GameMaker warns the event is inherited and offers to call the parent, accept — it writes `event_inherited();` for you.
4. Point an enemy at it: `turn_object = o_my_turn`.

!!! danger "The event you open may be the parent's"
    Once a Parent is set, the child's event list also shows inherited events, and clicking one opens **the parent's** code. Check the code window's tab title: it must say `o_my_turn : Create`, not `o_turn : Create`. Editing `o_turn` breaks every enemy in the game.

---

## Lifecycle

| Event | File | When | Purpose |
|---|---|---|---|
| Create | `Create_0.gml` | once, on birth | your variables |
| **User Event 0** | `Other_10.gml` | once, right after Create | **init** — `timer_end`, `pattern_pool` |
| **User Event 2** | `Other_12.gml` | once, when box and soul exist | the arena; the base draws `pattern` here |
| **User Event 1** | `Other_11.gml` | once, when the turn actually starts | **spawn bullets** |
| Step | `Step_0.gml` | every frame | continuous logic |
| Destroy | `Destroy_0.gml` | on destruction | clean up everything you spawned |

Note the ordering: **User Event 2 fires before User Event 1.** The engine creates the box, tells every turn object about it, and only then starts the turn.

The object is created during the `DIALOGUE` state — **several frames before the box exists**. Its Step runs the whole time.

!!! danger "Guard the Step"
    `o_enc.mybox` does not exist until the state turns `TURN` (`objects/o_enc/Step_0.gml:321`), and it is not even initialised in `o_enc`'s Create — so reading it early raises a *variable not set* error rather than returning `noone`.

    ```gml
    event_inherited()

    if timer == 0
        exit            // box and soul do not exist yet
    ```

    `timer` only counts after User Event 1, which runs after the box is born. This is the engine's own idiom — `objects/o_turn_default_dark/Step_0.gml`.

---

## Inherited fields

Set in `o_turn`'s Create, available to you from User Event 0 onward.

### Timing

| Field | Default | Meaning |
|---|---|---|
| `timer` | `0` | Frames elapsed. Counts **up**, and only after User Event 1 |
| `timer_end` | `60` | Turn length in frames. `undefined` = never ends on its own |
| `turn_started` | `false` | Set true by the base's User Event 1 |

At 30 FPS, `timer_end = 60` is **two** seconds.

### The enemy

| Field | Meaning |
|---|---|
| `enemy_index` | This enemy's slot in the encounter |
| `enemy_struct` | The `enemy()` struct itself. `enemy_struct.actor_id` is the on-screen instance |

Both are already filled in by the time User Event 0 runs — the engine passes them in the creation struct (`objects/o_enc/Step_0.gml:249`).

### Patterns

| Field | Default | Meaning |
|---|---|---|
| `pattern` | `undefined` | The chosen attack variant |
| `pattern_pool` | `[1]` | Candidates to choose from |
| `assign_unique_patterns` | `true` | Try to give identical enemies different patterns |

The base's **User Event 2** shuffles the pool and assigns `pattern` with `??=` — so **a value you set earlier wins**. Setting `pattern` in User Event 0 is the standard way to drive an attack from enemy state instead of chance.

### Difficulty

| Field | Default | Meaning |
|---|---|---|
| `buff` | `0` | How many **identical** turn objects merged into this one |
| `debuff` | `0` | How many **other** turn objects were alive at init |
| `allow_same_turns` | `false` | `false`: duplicates merge into `buff`. `true`: each enemy gets its own turn |
| `shorten_by_tension` | `true` | Whether grazing may shorten this turn |
| `am_support` | `false` | Support turn — exists only alongside a main turn |

### Helpers

| Function | What it does |
|---|---|
| `__support_init_default()` | Marks this turn as support if a non-support turn already exists |
| `__support_destroy_check()` | Destroys this turn when no main turn is left. **Does not look at `timer_end`** |

---

## The two ways a turn ends

They are separate mechanisms and easy to confuse.

**1. `timer_end`** — handled in the **parent's** Step, inherited via `event_inherited()`:

```gml
// objects/o_turn/Step_0.gml
if turn_started
    timer ++
if !is_undefined(timer_end) && timer > timer_end
    instance_destroy()
```

Forget `event_inherited()` in your Step and the timer never runs — the battle freezes.

**2. `__support_destroy_check()`** — only for support turns (`am_support = true`). It destroys this turn once no main turn remains (`objects/o_turn/Create_0.gml:31`). On a normal turn it does nothing; it is a safety net, not the end of the turn.

For a turn that should last exactly as long as its pattern:

```gml
// Other_10.gml
timer_end = undefined

// Step_0.gml
if timer > 30 && !instance_exists(o_enc_bullet)
    instance_destroy()
```

!!! danger "`timer_end = undefined` with no exit condition freezes the fight"
    Write the `instance_destroy()` in the same sitting. `encounter_end` in the console gets you out while testing.

---

## Cleanup

**Nothing in the engine collects what your turn spawned.** Bullets fly out of the box and keep existing; extra `o_enc_box_solid` obstacles stay put.

```gml
// Destroy_0.gml
event_inherited()               // returns the enemy to its idle sprite
instance_destroy(o_enc_bullet)  // and everything else you created
```

`event_inherited()` matters here too: the parent's Destroy restores `enemy_struct.actor_id.sprite_index` to `s_idle` (`objects/o_turn/Destroy_0.gml`). Without it, an enemy that changed sprite mid-attack stays frozen in the attack pose.

---

## Creating bullets

```gml
instance_create(o_enc_bullet, xx, yy, DEPTH_ENCOUNTER.BULLETS_OUTSIDE, {
    att:         6,                     // attack STAT — damage is 5*att minus defence
    color:       BULLET_COLOR.SOLID,    // when this bullet hurts
    speed:       3,                     // px per frame
    direction:   270,                   // 0=right, 90=up, 180=left, 270=down
    graze:       2,                     // TP granted for a near miss
    time_points: 5,                     // frames a graze cuts from timer_end
    inv:         global.enc_soul_inv,   // i-frames granted on hit (40)
    destroy:     true,                  // vanish on hit — SOLID only
    inside:      false,                 // draw clipped inside the box
    element:     ""
})
```

!!! warning "The creation struct only sets fields that already exist"
    `instance_create` is overridden by the engine (`scripts/custom/custom.gml:297`). It applies the struct **after** the Create event, and skips any field the instance does not already have. Inventing a new field is **silently ignored**. Assign it after creation instead.

### Bullet colours

| `BULLET_COLOR` | Hurts when | Grazeable | Respects `destroy` |
|---|---|---|---|
| `SOLID` | always, on contact | ✅ | ✅ |
| `BLUE` | only if the soul is **moving** | ❌ | ❌ |
| `ORANGE` | only if the soul is **still** | ❌ | ❌ |

### Draw depths

```gml
DEPTH_ENCOUNTER.BULLETS_OUTSIDE  // -6500 — in front of everything
DEPTH_ENCOUNTER.SOUL             // -6400
DEPTH_ENCOUNTER.BOX              // -6300
DEPTH_ENCOUNTER.BULLETS_INSIDE   // -6200 — behind the box frame
DEPTH_ENCOUNTER.ACTORS           // -6100
DEPTH_ENCOUNTER.BACKGROUND       // -6000
```

---

## What you can reach from a turn object

```gml
o_enc.turn_count      // which round (0, 1, 2…)
o_enc.tp              // the magic bar, 0–100
o_enc.mybox           // the arena — ONLY from User Event 2 onward
o_enc.mysoul          // the soul
o_enc_box.x / .y      // arena centre (same instance as o_enc.mybox)
o_enc_box.width       // arena size
o_enc_soul.x / .y     // aim at this
o_enc_soul.moving     // true only if input was given AND the soul moved
enemy_struct          // your enemy's struct
enemy_struct.actor_id // its on-screen instance
```

---

## A complete skeleton

```gml
// ---------- Create_0.gml ----------
event_inherited()

_my_state = 0
_spawned  = []
```

```gml
// ---------- Other_10.gml — User Event 0 (init) ----------
event_inherited()
__support_init_default()

if !am_support
    timer_end = 120        // 4 seconds at 30 FPS
```

```gml
// ---------- Other_12.gml — User Event 2 (box created) ----------
event_inherited()          // ← the base picks `pattern` here

o_enc.mybox.width  = 75
o_enc.mybox.height = 75
```

```gml
// ---------- Other_11.gml — User Event 1 (turn starts) ----------
event_inherited()

// one-off spawns go here
```

```gml
// ---------- Step_0.gml ----------
event_inherited()          // ← makes timer_end work

if timer == 0
    exit                   // box and soul do not exist yet

// per-frame logic here

__support_destroy_check()
```

```gml
// ---------- Destroy_0.gml ----------
event_inherited()
instance_destroy(o_enc_bullet)
```

---

## Worth reading in the engine

| Object | Shows |
|---|---|
| `o_turn_default` | the minimum viable turn |
| `o_turn_default_dark` | support turns, and using `buff` |
| `o_ex_turn_complex_box` | reshaping the arena, animated bullet paths |
| `o_ex_turn_sguy` | `pattern_pool`, driving the enemy's sprite, `depth_override` |
| `o_ex_turn_dentos` | cutscene-driven attacks, staggering multiple enemies |
