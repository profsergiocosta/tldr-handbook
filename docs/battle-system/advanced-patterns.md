# Advanced patterns

Everything here builds on [Your first enemy](your-first-enemy.md) and [The arena](the-arena.md). These are techniques rather than a walkthrough — pick the ones your fight needs.

---

## Custom bullets

`o_enc_bullet` is a base class. A child object inherits the colour rules, the graze logic, the damage handling and the clipping behaviour, and lets you override exactly the part you want.

Create an object with **Parent: `o_enc_bullet`**, then override one of three events:

| Override | To change | Remember |
|---|---|---|
| `Step_0.gml` | movement | `event_inherited()` first — the base Step is empty, but that will not always be true |
| `Other_11.gml` | **how it looks** | this is the draw event, not `Draw` |
| `Other_10.gml` | **what happens on hit** | this is where colour, i-frames and damage are handled |

The base's `Draw_0` decides *where* to draw — screen or box surface — and then calls `event_user(1)`. That is why custom visuals go in `Other_11`.

### A minimal custom bullet

```gml
// o_bullet_feather / Create_0.gml   (Parent: o_enc_bullet)
event_inherited()

att   = 3
graze = 4
wobble = random(360)
```

```gml
// o_bullet_feather / Step_0.gml
event_inherited()

wobble += 4
direction += dsin(wobble) * 3      // drifts side to side as it falls
```

```gml
// o_bullet_feather / Other_11.gml
image_angle = direction - 90
draw_self()
```

### Homing done properly

The naive version — recalculating `direction` toward the soul every frame — makes a bullet that is impossible to dodge, which is not a difficulty setting, it is a broken fight.

The engine's own homing bullet, `o_enc_bullet_dark`, does something better: it accepts a `homing_target` in its creation struct and steers with `friction` and a shrinking scale, so it curves rather than snaps. Read its Create event for the full technique.

For most cases, **aim once at spawn**:

```gml
instance_create(o_enc_bullet, xx, yy, DEPTH_ENCOUNTER.BULLETS_OUTSIDE, {
    speed: 3,
    direction: point_direction(xx, yy, o_enc_soul.x, o_enc_soul.y)
})
```

That reads as "aimed" to the player, and it is dodgeable.

---

## Animated bullet paths

`speed`/`direction` handles straight lines. For anything else, animate a bullet's fields with the engine's `animate()` function.

`o_ex_turn_complex_box` uses this to make a bullet sweep back and forth forever:

```gml
var inst = instance_create(o_enc_bullet, o_enc.mybox.x, o_enc.mybox.y + 10,
                           DEPTH_ENCOUNTER.BULLETS_INSIDE, { inside: true })

var a = animate(inst.x - 40, inst.x + 40, 60, anime_curve.cubic_in_out, inst, "x", false)
a._add(inst.x - 40, 60, anime_curve.cubic_in_out)
a._start()

anime_set_loop(a, true)
```

The pattern is: `animate(...)` with `start = false`, chain more keyframes with `_add`, then `_start()`. `anime_set_loop` makes it repeat.

Available curves are in `anime_curve` (`scripts/anime_functions/anime_functions.gml`): `linear`, `quad_*`, `cubic_*`, `quart_*`, `quint_*`, `expo_*`, `sine_*`, `circ_*`, `back_*`, `elastic_*`, `bounce_*`, `hold` — each with `_in`, `_out` and `_in_out` variants.

!!! tip "`inside: true` for contained patterns"
    A bullet with `inside: true` is drawn onto the box's surface, so it is **clipped by the walls**. Combined with an animated path, that is how you get bullets that visibly live inside the arena rather than flying through it.

---

## Multiple attack patterns per enemy

An enemy with one attack gets boring by round three. The `o_turn` base has a built-in mechanism for variety.

```gml
// Create_0.gml
event_inherited()

pattern_pool = ["swipes", "hiss", "purr"]
assign_unique_patterns = true      // default
```

The base's **User Event 2** shuffles the pool and assigns `pattern` — using `??=`, so it only fills a pattern you have not already set. With `assign_unique_patterns` on, several enemies of the same type try to get *different* patterns rather than all rolling the same one.

Then branch in the Step, exactly as Sonso branches on mood:

```gml
if pattern == "swipes" { ... }
else if pattern == "hiss" { ... }
else if pattern == "purr" { ... }
```

!!! info "Mood and pool are not mutually exclusive"
    Sonso sets `pattern` from `enemy_struct.mood` in User Event 0, which means the pool never fires. That is deliberate — his attack is driven by state, not chance. If you want *both*, use the mood to choose a **sub-pool**:

    ```gml
    // Other_10.gml
    pattern_pool = (enemy_struct.mood == "annoyed")
        ? ["hiss_fast", "hiss_wall"]
        : ["swipes", "purr"]
    ```

    Leave `pattern` undefined and let User Event 2 roll from the narrowed pool.

---

## Support enemies

Some enemies should not have their own turn — they augment someone else's. That is what `am_support` is for.

`__support_init_default()` marks this turn as support if any non-support turn object already exists. `__support_destroy_check()` then destroys it once no main turn remains. The net effect: **a support enemy adds bullets to whatever the main enemy is doing, and disappears when the main attack ends.**

The template is `o_turn_default_dark`:

```gml
// Other_10.gml
event_inherited()
__support_init_default()

if !am_support
    timer_end = 60          // only a MAIN turn gets a timer
                            // support turns leave timer_end undefined
```

```gml
// Step_0.gml
event_inherited()

if timer == 0
    exit

var _period = clamp(25 - (5 * buff), 15, 25)
if timer % _period == 0 {
    instance_create(o_enc_bullet_dark, /* … */)
}

__support_destroy_check();
```

Note the shape: the support turn has **no timer of its own**. It lives exactly as long as the main attack does.

---

## Difficulty that scales with the encounter

Two counters are handed to every turn object in User Event 0:

| Field | Meaning |
|---|---|
| `buff` | how many **identical** turn objects were merged into this one — 0 when the enemy is alone |
| `debuff` | how many **other** turn objects (of any type) were alive at init |

`buff` goes up when you put two of the same enemy in an encounter; `debuff` goes up when the enemy is fighting alongside different creatures.

Use them instead of writing separate patterns:

```gml
var _period = clamp(30 - 8 * buff, 14, 30)      // denser with more of the same
var _damage = max(2, 4 - debuff)                 // gentler in a crowded fight
```

This is how one enemy definition covers "alone", "in a pair" and "in a mixed group" without branching.

---

## Driving the enemy's sprite during its attack

`enemy_struct.actor_id` is the on-screen instance of the enemy this turn belongs to. Animating it during the attack is what makes a pattern feel like it came *from* the creature.

`o_ex_turn_dentos` does this with cutscene calls, which queue neatly instead of fighting the Step:

```gml
// Step_0.gml
event_inherited()
var inst = enemy_struct.actor_id

if pattern == "explosions" {
    if timer > 0 {
        if timer % 60 == (enemy_index * 20) % 60 {
            current_cutscene = cutscene_create()

            cutscene_set_variable(inst, "image_speed", 0)
            cutscene_set_variable(inst, "image_index", 3)
            cutscene_animate(0, 3, 10, "linear", inst, "shake")
            cutscene_sleep(15)
            cutscene_set_variable(inst, "image_index", 0)
            cutscene_animate(3, 0, 20, "linear", inst, "shake")

            cutscene_func(/* spawn the bullet here */)

            cutscene_play()
        }
    }
}
```

Two things to steal from this:

**`(enemy_index * 20) % 60`** staggers the attack when several of the same enemy are on the field, so they do not all fire on the same frame.

**`shake`** is a field on `o_ow_depthobj`, which every actor inherits — animating it from 0 to 3 and back is a ready-made recoil.

Simpler, without cutscenes:

```gml
if timer == 20 {
    enemy_struct.actor_id.sprite_index = spr_my_enemy_attack
    enemy_struct.actor_id.image_index  = 0
}
```

The parent's Destroy returns the sprite to idle for you — as long as your Destroy calls `event_inherited()`.

!!! tip "Drawing the enemy in front of the bullets"
    Set `actor_id.depth_override` to bring the attacking enemy forward, as `o_ex_turn_sguy` does:

    ```gml
    var o = enemy_struct.actor_id
    o.depth_override = DEPTH_ENCOUNTER.BULLETS_OUTSIDE - (o.y - guipos_y())
    o.depth = o.depth_override
    ```

    Set it back to `undefined` when the attack ends.

---

## Ending a turn on a condition

`timer_end` covers most attacks. When the turn should last exactly as long as the pattern does, set `timer_end = undefined` and destroy the object yourself:

```gml
// Other_10.gml
event_inherited()
__support_init_default()
timer_end = undefined            // disable the automatic ending
```

```gml
// Step_0.gml
event_inherited()
if timer == 0 exit

// ... spawn bullets ...

if timer > 30 && !instance_exists(o_enc_bullet)
    instance_destroy()           // ends when the last bullet is gone

__support_destroy_check()
```

!!! danger "The most common way to freeze a battle"
    `timer_end = undefined` with no exit condition means the turn never ends and the fight locks up. If you use it, write the `instance_destroy()` in the same sitting. The console command `encounter_end` gets you out while testing.

---

## Making graze part of the design

Every bullet carries two numbers that shape how the player *wants* to move:

| Field | Default | Effect |
|---|---|---|
| `graze` | 2 | TP awarded for brushing past |
| `time_points` | 5 | frames cut from `timer_end` for brushing past |

Turning these up on wide, slow bullets invites the player into the pattern. Turning them down — or to zero — on a dense curtain says *this one is not for showing off*.

`time_points` only applies to turn objects with `shorten_by_tension = true` (the default). Set it to `false` on a scripted attack whose timing must not change.

!!! info "The design test"
    If a pattern cannot be grazed at all, the player earns no TP, cannot cast, and the fight flattens out. Ask of every attack: **where is the reward for playing close?**

---

## Reusable helper objects

For anything with its own lifetime — a warning marker, a laser charging up, a projectile that spawns other projectiles — make a separate object rather than tracking state in the turn.

`o_ex_bullet_dentos_eye` is the pattern: a bullet that, at a certain point, spawns a different bullet:

```gml
// Step_0.gml of the parent bullet
instance_create(o_ex_bullet_dentos_diamond, x, y, depth, {
    speed: .2,
    direction: /* … */
})
```

Just remember the cleanup rule: **your turn object's Destroy is responsible for everything it spawned.** If the helper can outlive the turn, destroy it there too:

```gml
// Destroy_0.gml
event_inherited()
instance_destroy(o_enc_bullet)
instance_destroy(o_my_helper_object)
```

---

## A checklist for a new attack

Before you call a pattern finished:

- [ ] Can it be dodged cleanly once the player understands it?
- [ ] Does the first second give time to react — nothing spawns on top of the soul?
- [ ] Is there somewhere worth grazing?
- [ ] If it uses `BLUE` or `ORANGE`, is the bullet big or dense enough to force the rule? A small blue bullet just gets dodged and teaches nothing.
- [ ] Does it look like it came from *this* creature, and not from a bullet library?
- [ ] Does the turn object clean up everything it spawned?
- [ ] Does the turn actually end — every path, including the ones you did not plan?
