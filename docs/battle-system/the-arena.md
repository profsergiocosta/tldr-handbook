# The arena

Direct continuation of [Your first enemy](your-first-enemy.md). There, Sonso got a personality through his ACTs and bullet patterns. Here he gets **a place**: the box the soul moves in stops being a neutral square and starts acting alongside him.

Nine steps, each testable on its own. You can stop at any of them.

## Before you start

You need Sonso working: `rpg_enemy_sonso()`, `rpg_enc_set_sonso()` and the `o_turn_sonso` object with its four events. If ++tab++ → `encounter_select` → `sonso` opens the fight and the cat attacks, you are ready.

## The idea

In the first chapter, Sonso's mood changed the **bullet pattern**. Here it will also change **the size, tilt and contents of the arena**.

This matters because the box is the player's personal space. Shrinking it is not "raising the difficulty" — it is the cat getting too close. Rotating it is not a pretty effect — it is you losing your footing. The player feels it before understanding it.

| Mood | What the arena does | What it says |
|---|---|---|
| `calm` | plain square, 75×75 | he is relaxed |
| `annoyed` | shrinks to 55×55 and shakes | he has cornered you |
| `curious` | grows to 90×90 and turns slowly | he is circling you |

---

## Step 1 — Where you touch the arena

The box is the instance **`o_enc.mybox`** (object `o_enc_box`), created by the engine at the start of each defence turn. It exists from the moment the box opens until it closes.

The right place to configure it is your turn object's **User Event 2** — the event the engine describes as *"box is created"*, called right after the box and soul are born and **before** the turn starts.

If you followed the first chapter, `o_turn_sonso` does not have that event yet. Add it: **Add Event → Other → User Events → User Event 2** (file `Other_12.gml`).

!!! warning "Call the parent in this event"
    The `o_turn` base uses User Event 2 to draw `pattern` from `pattern_pool`. Overriding it without `event_inherited()` breaks pattern selection for any enemy that uses a pool. The first line is always `event_inherited()`.

### What you can change

| Property | Effect |
|---|---|
| `width` / `height` | arena size (default 75×75) |
| `x` / `y` | where it sits on screen |
| `image_angle` | tilt |
| `sprite_index` + `mask_index` + `sprite_back` | the arena's shape |
| `color` | frame colour |

### A two-minute experiment

Write this and run:

```gml
// Other_12.gml — User Event 2 ("box is created")
event_inherited()

o_enc.mybox.width  = 140
o_enc.mybox.height = 50
```

You should get a wide, short arena, like a slot. Put it back to `75`/`75` after checking — step 2 does it properly.

!!! info "Why not in Create or User Event 0"
    In those two events the box **does not exist yet** — `o_enc.mybox` only appears when the battle state turns `TURN`. Reading it earlier does not give you `noone`; it raises a *variable not set* error and stops the game.

---

## Step 2 — The arena reacts to the mood

Now wiring the arena to the character. In the same `Other_12.gml`:

```gml
// Other_12.gml — User Event 2
event_inherited()

switch pattern {                    // remember: pattern IS the cat's mood
    case "annoyed":
        o_enc.mybox.width  = 55     // he corners you
        o_enc.mybox.height = 55
        break

    case "curious":
        o_enc.mybox.width  = 90     // he circles you, with room to spare
        o_enc.mybox.height = 90
        break

    default:
        o_enc.mybox.width  = 75
        o_enc.mybox.height = 75
        break
}
```

`pattern` was set in User Event 0 (`pattern = enemy_struct.mood`), and User Event 2 runs after it, so it already holds the right mood.

**Test:** enter the fight, use `Call`, and notice the next round's arena is visibly smaller. Use `Ignore` and it opens up. If you built the `DEBUG` ACT from the first chapter, it is faster still.

!!! tip "Shrinking beats speeding up"
    A 55×55 arena with the same bullets is tenser than a 75×75 arena with bullets 30% faster — and it is more legible, because the player **sees** the change before feeling it. Prefer changing space before changing speed.

---

## Step 3 — The arena shakes and turns

Size is a state; movement is an emotion. Let us make the box shake when the cat is annoyed and turn slowly when he is curious.

This goes in the **Step**, since it happens every frame. But the Step needs a guard that User Event 2 did not:

```gml
// Step_0.gml of o_turn_sonso
event_inherited()

if timer == 0
    exit                    // the box and soul do not exist yet

if pattern == "annoyed"
    o_enc.mybox.image_angle = sine(4, 2)        // fast, tight tremor
else if pattern == "curious"
    o_enc.mybox.image_angle = sine(40, 12)      // slow, wide sway

// ... the bullet patterns from the first chapter continue here ...

__support_destroy_check()
```

!!! danger "`if timer == 0 exit` is not decoration"
    The `turn_object` is **born before the box**: it is created during `DIALOGUE`, and `o_enc.mybox` only exists once the state turns `TURN` (`objects/o_enc/Step_0.gml:321`). Since `mybox` is not even initialised in `o_enc`'s Create, reading it early does not return `noone` — it raises a **variable not set error** and the game stops.

    The guard works because `timer` only starts counting after User Event 1, which runs **after** the box is born. If `timer > 0`, the box certainly exists. It is the engine's own idiom — see `objects/o_turn_default_dark/Step_0.gml`.

    The first chapter's code escaped this by accident: every bullet pattern sat inside conditions like `timer % 30 == 0 && timer > 0` or `timer == 10`, which already required `timer > 0`. Add any bare line to the Step and the guard becomes necessary.

`sine(divisor, multiplier)` is an engine function (`scripts/custom/custom.gml:491`): it returns a sine based on `o_world.frames`. Smaller divisor = faster; larger multiplier = wider.

!!! info "The soul is carried along, for free"
    Rotating the box does not let the player pass through the wall. `o_enc_box_solid` measures its own displacement, rotation and scale change every frame (`objects/o_enc_box_solid/Step_1.gml`), and `o_enc_soul/Step_1.gml` uses those values to push and rotate the soul with the arena.

    It works for all three: moving, turning and resizing. A wall that advances **pushes** the player instead of swallowing them.

**Test:** the difference between `sine(4, 2)` and `sine(40, 12)` is the whole point. Run both and notice how the same bullet pattern acquires a different feel.

---

## Step 4 — Changing the arena's shape

So far the box is still rectangular. Changing the shape properly takes **three** sprites:

```gml
// Other_12.gml
o_enc.mybox.sprite_index = spr_ex_box_complex        // the frame
o_enc.mybox.mask_index   = spr_ex_box_complex_mask   // the walls (collision)
o_enc.mybox.sprite_back  = spr_ex_box_complex_back_2x // the interior fill

with o_enc.mybox {
    sprite_w = sprite_get_width(sprite_index)
    sprite_h = sprite_get_height(sprite_index)
}
```

The three must move together:

| Sprite | Role | Watch out |
|---|---|---|
| `sprite_index` | the visible frame | — |
| `mask_index` | **where the soul collides** | must be the **hollow** frame — only the border is solid, the middle is a hole |
| `sprite_back` | the interior fill | if you use nine-slice, it must be 2x |

The trailing `with` is mandatory: the box's Step recalculates scale as `image_xscale = width / sprite_w`, and if `sprite_w` still holds the old sprite's value the size comes out wrong.

!!! warning "The mask is hollow, not filled"
    The soul moves where there is **no** collision (`o_enc_soul/Step_0.gml`). A filled rectangle mask leaves it nowhere to stand. That is why the default `spr_enc_box_mask` is just an outline. When drawing your own, draw **the walls**, not the room.

The ready-made example in the engine is **`o_ex_turn_complex_box`** — worth opening and running (`encounter_select`) before you draw your own.

---

## Step 5 — Obstacles inside the arena

Here is a detail that opens a lot up: **`o_enc_box` is a child of `o_enc_box_solid`**, and the soul tests collision against the **parent**:

```gml
if !place_meeting(x + xstep + sign(xstep)*1.5, y, o_enc_box_solid)
```

So **any extra `o_enc_box_solid` instance becomes a solid wall inside the arena.** Pillars, corridors, a wall that descends mid-turn.

For Sonso, the idea: when he is annoyed, he knocks **cardboard boxes** into the arena.

```gml
// Create_0.gml — keep the list so you can clean up later
event_inherited()

_side  = choose(-1, 1)
_boxes = []
```

```gml
// Other_12.gml — after what you already have
if pattern == "annoyed" {
    repeat (2) {
        var _c = instance_create(o_enc_box_solid,
            o_enc_box.x + irandom_range(-25, 25),
            o_enc_box.y + irandom_range(-25, 25),
            DEPTH_ENCOUNTER.BOX - 1)

        _c.sprite_index = spr_pixel
        _c.image_xscale = 14
        _c.image_yscale = 14
        _c.image_blend  = c_olive
        _c.visible      = true      // o_enc_box_solid is born invisible

        array_push(_boxes, _c)
    }
}
```

```gml
// Destroy_0.gml
event_inherited()
instance_destroy(o_enc_bullet)

for (var i = 0; i < array_length(_boxes); i ++)
    if instance_exists(_boxes[i])
        instance_destroy(_boxes[i])
```

Three details:

**`o_enc_box_solid` is born invisible** (`"visible": false` in its `.yy`) and without a sprite. It needs `sprite_index` and `visible = true` to become something the player can see — otherwise you have made a ghost wall, which is miserable to play against.

**`spr_pixel` is 1×1**, so `image_xscale` is literally the size in pixels. Handy for prototyping; swap in a real sprite later.

**Cleaning up in Destroy is not optional.** Nothing in the engine collects these objects, exactly as with bullets. Without it, round two starts with round one's boxes still there.

!!! tip "A moving obstacle pushes"
    Because `o_enc_box_solid` tracks its own movement, an obstacle you animate with `animate(...)` **pushes the soul** rather than passing through it. A wall creeping in from one side is an entire attack with no bullets at all.

---

## Step 6 — The background

The background is the one part of the battle the engine draws **behind** everything, and it changes the mood with the least effort. Before replacing it, it is worth understanding what is there.

### 6.1 How the default background works

It all comes from one object, **`o_eff_bg`**, created by the engine at depth `DEPTH_ENCOUNTER.BACKGROUND` when the fight starts (`o_enc_anim/Alarm_1.gml:72`). Its `Draw` stacks **three layers**:

| Layer | What it is | Controlled by |
|---|---|---|
| 1. Black curtain | a black rectangle covering the screen, hiding the overworld | `image_alpha` (rises 0 → 1 on its own, 0.1 per frame) |
| 2. The grid | `spr_enc_bg` drawn **twice**, at different speeds and opacities — that is where the sense of depth comes from | `image_blend`, and only exists if `bg_type == ENC_BG.GRID` |
| 3. The veil | another black rectangle over everything | `fade` — the engine animates it to `0.75` when the defence turn starts |

Layers 1 and 2 only appear with `bg_type = ENC_BG.GRID`. Layer 3 **always** exists, even with `NONE` — it is what darkens the scene when the box opens, and you probably want to keep it.

!!! info "The background is drawn in room coordinates, not GUI"
    The battle happens in a **320×240** window anchored to the camera. That is why every background draw adds `guipos_x()` and `guipos_y()`, which are the camera's position (`scripts/custom/custom.gml:2`). Without that offset your background sits in the wrong corner as soon as the camera is not at the origin.

    Do not confuse this with the interface (names, HP, buttons), drawn in `Draw GUI` at 640×480 — twice the size.

### 6.2 Level 1 — recolour the grid

The grid is drawn with `image_blend`, so changing the colour of the whole background is **one line**. And since Sonso already has moods, you can tie the two together.

In `o_turn_sonso`'s `Step_0.gml`, alongside the arena block:

```gml
// ---------- the arena reacts to the mood ----------
if pattern == "annoyed" {
    o_enc.mybox.image_angle = sine(4, 2)
    o_eff_bg.image_blend = make_color_rgb(255, 120, 90)   // the world heats up
}
else if pattern == "curious" {
    o_enc.mybox.image_angle = sine(40, 12)
    o_eff_bg.image_blend = make_color_rgb(150, 190, 255)  // and cools down
}
else
    o_eff_bg.image_blend = c_white                        // neutral
```

Two test rounds and you will see how much this changes the reading of the scene without a single new bullet. It is the highest return per line in this whole chapter.

!!! warning "`o_eff_bg` does not exist outside a battle"
    It is born with the fight and destroys itself at the end. Inside a `turn_object` that is safe — if the turn exists, the battle exists. Anywhere else, guard with `if instance_exists(o_eff_bg)`.

### 6.3 Level 2 — your own background

When the grid does not fit, turn it off and draw your own.

**First, turn the grid off** in `enc_set()`:

```gml
    bg_type = ENC_BG.NONE
```

That kills layers 1 and 2. Layer 3, the veil, remains — and it is still what gives the arena focus.

**Then create the object.** A night rooftop for the cat, with no new sprites at all — everything with `spr_pixel`, which is 1×1 with its origin at the corner, so `image_xscale` is literally the width in pixels:

```gml
// ---------- o_bg_rooftop / Create_0.gml ----------
depth = DEPTH_ENCOUNTER.BACKGROUND + 10   // LARGER number = further back

// the stars are rolled once, not every frame
stars = []
repeat (40)
    array_push(stars, {
        xx:    random(320),
        yy:    random(150),
        phase: random(360)
    })
```

```gml
// ---------- o_bg_rooftop / Draw_0.gml ----------
var _ox = guipos_x()
var _oy = guipos_y()

// the sky
draw_sprite_ext(spr_pixel, 0, _ox, _oy, 320, 240, 0, make_color_rgb(14, 16, 34), 1)

// the stars, twinkling out of phase
for (var i = 0; i < array_length(stars); i ++) {
    var _s = stars[i]
    var _bright = 0.35 + 0.35 * dsin(o_world.frames * 2 + _s.phase)

    draw_sprite_ext(spr_pixel, 0, _ox + _s.xx, _oy + _s.yy, 1, 1, 0, c_white, _bright)
}

// the rooftop silhouette
draw_sprite_ext(spr_pixel, 0, _ox, _oy + 170, 320, 70, 0, make_color_rgb(6, 7, 16), 1)
```

```gml
// ---------- o_bg_rooftop / Step_0.gml ----------
if !instance_exists(o_enc)
    instance_destroy()
```

**Finally, have it created** in `enc_set()`'s `ev_init` hook, which runs one frame after `o_enc` exists:

```gml
    ev_init = function() {
        instance_create(o_bg_rooftop)
    }
```

Three decisions worth explaining:

**The stars are born in Create, not Draw.** Rolling positions inside `Draw` would make them flicker to new places every frame. Storing them in an array and only reading at draw time is the pattern for any static decoration.

**The self-destroying Step.** Without it the background survives the fight and shows up in the overworld. Tying its life to `o_enc`'s existence covers every ending — victory, flight, defeat — without handling each one.

**The depth is `BACKGROUND + 10`, not `- 10`.** In GameMaker, **a larger depth is further back**. This is the classic mistake here: a smaller number puts your background in front of the enemies.

| Depth | What lives there |
|---|---|
| `-6500` `BULLETS_OUTSIDE` | bullets in front of everything |
| `-6400` `SOUL` | the soul |
| `-6300` `BOX` | the arena frame |
| `-6200` `BULLETS_INSIDE` | clipped bullets, behind the frame |
| `-6100` `ACTORS` | the enemies and the party |
| `-6000` `BACKGROUND` | `o_eff_bg` — grid and veil |
| `-5990` | **your background** |

### 6.4 The dark veil, as a dramatic tool

Layer 3 (`o_eff_bg.fade`) is a black rectangle over everything. The engine animates it to `0.75` when the defence turn starts (`o_enc/Step_0.gml:241`) and back to `0` when it ends.

Since it is just a variable, you can use it deliberately. Darken further when the cat is annoyed, for instance — the world disappears and only the arena is left:

```gml
// in Other_12.gml, after configuring the box
if pattern == "annoyed"
    animate(o_eff_bg.fade, 0.92, 20, anime_curve.sine_out, o_eff_bg, "fade")
```

`animate(from, to, frames, curve, instance, "field")` is the engine's animation function (`scripts/anime_custom/anime_custom.gml:17`). No need to undo it: the engine returns `fade` to zero at the end of the turn.

### Testing the background

| Step | Do this | What it proves |
|---|---|---|
| 1 | Set `o_eff_bg.image_blend = c_red` and run | if it does not go red, `bg_type` is already `NONE` or your code is in the wrong event |
| 2 | Switch to `ENC_BG.NONE` with no object at all | the background must go **black** with the veil; if the grid persists, you edited the wrong `enc_set()` |
| 3 | Create `o_bg_rooftop` with a garish colour (`c_lime`) | if it does not appear, it is the depth; if it appears **in front of** the enemies, also the depth |
| 4 | Move the camera before entering the fight | if the background slides, you forgot `guipos_x()` / `guipos_y()` |
| 5 | Win or flee the fight | the background must vanish with it; if it lingers in the overworld, the `Step` is missing |

---

## Step 7 — Two Sonsos

More enemies is just the array in `enc_set()`:

```gml
function rpg_enc_set_sonso_double() : enc_set() constructor {
    debug_name = "sonso_double"

    enemies = [
        new rpg_enemy_sonso(),
        new rpg_enemy_sonso(),
    ]

    enemies_pos = [
        [ -10, -14, true ],     // [x, y, relative to the default spot]
        [  10,  14, true ],
    ]

    bgm = mus_battle
}
```

Each `new` is an independent struct: the two cats have their own mood, HP and MERCY.

### The surprising part: they do not attack twice

You expect two bullet turns and get **one**. That is not a bug. Look at the `o_turn` base's User Event 0:

```gml
with object_index {
    count ++
    if id != iid && !allow_same_turns
        instance_destroy()      // duplicate turns destroy themselves
}
buff = count - 1                // and the survivor gains "buff"
```

With `allow_same_turns = false` (the default), two enemies of the same type produce **one** turn object with `buff = 1`. The engine assumes two identical simultaneous attacks become visual soup — so instead it hands you a counter to **intensify** the attack with.

Use `buff` in `Step_0.gml`:

```gml
if pattern == "calm" {
    var _period = clamp(30 - 8 * buff, 14, 30)   // with 2 cats: 22 instead of 30
    if timer % _period == 0 && timer < timer_end - 30 {
        // ... the usual swipes
    }
}
```

That is the same trick `o_turn_default_dark` uses.

!!! warning "Only one mood is in charge"
    Since a single turn object survives, `pattern = enemy_struct.mood` in User Event 0 reads **one** of the cats' moods. If you want both to count, read them all in User Event 0:

    ```gml
    var _any_annoyed = false
    for (var i = 0; i < array_length(o_enc.encounter_data.enemies); i ++)
        if enc_enemy_is_fighting(i) && o_enc.encounter_data.enemies[i].mood == "annoyed"
            _any_annoyed = true

    pattern = _any_annoyed ? "annoyed" : enemy_struct.mood
    ```

    If you genuinely want **two independent turns**, set `allow_same_turns = true` in `o_turn_sonso`'s Create. Then brace yourself: two patterns at once in the same box.

**Test:** `encounter_select` → `sonso_double`. Check that two names appear in the list, that you can choose which to attack, and that the attack got denser than with one cat.

!!! info "How many fit?"
    There is no limit in the code, but the enemy name list is drawn at `375 + 30*i` in a 480px-tall interface (`o_enc/Draw_64.gml:190`). In practice: **3 comfortably, 4 tight**. The engine's examples use 2.

---

## Step 8 — Your own win condition

By default the fight ends when every enemy has left the field. But `win_condition` is your function — you can end it for any reason.

A Sonso who just wants to be left alone: survive three rounds without attacking him and he leaves on his own.

```gml
// in enc_set()
    win_condition = function() {
        if o_enc.turn_count >= 3
            return true

        for (var i = 0; i < array_length(o_enc.encounter_data.enemies); ++i)
            if enc_enemy_is_fighting(i)
                return false

        return true    // the default rule: nobody left fighting
    }
```

The engine evaluates this while executing actions (`o_enc/Step_0.gml:216`), so the fight ends on the round after the condition is met.

Other conditions the same structure allows: survive until `o_enc.turn_count == N`, accumulate TP (`o_enc.tp >= 100`), defeat one specific enemy, or a flag an ACT flips.

---

## Step 9 — Where the party stands

The team is positionable too, from `enc_set()`:

```gml
    party_pos = function(i) {           // i = the member's index
        return [
            guipos_x() + 52,
            guipos_y() + 130 - 22 * party_length() + i*44,
        ]
    }
```

That is the default — a column on the left, vertically centred according to party size. For a different staging, return other coordinates:

```gml
    party_pos = function(i) {           // a horizontal row along the bottom
        return [
            guipos_x() + 90 + i*60,
            guipos_y() + 190,
        ]
    }
```

`guipos_x()` and `guipos_y()` are the interface corner — always add them, or the positions drift when the camera moves.

---

## How to test each thing

| What you changed | Fastest way to confirm |
|---|---|
| arena size | enter the fight and compare against a sample encounter (`encounter_select`) |
| size **per mood** | use the `DEBUG` ACT from the first chapter to force each mood |
| rotation / shake | exaggerate first: `sine(2, 25)`. If nothing moves, the code is in the wrong event |
| shape (sprites) | walk into the wall in all four directions. If the soul escapes, the mask is wrong |
| obstacles | they must be **visible**; an invisible wall is a bug, not a challenge |
| your own background | `bg_type = ENC_BG.NONE` first; if the grid persists, you edited the wrong `enc_set()` |
| two enemies | check the attack got denser — if it is identical, `buff` is not being used |
| `win_condition` | force `return true` and watch the fight end immediately |

!!! tip "The test worth more than all the others"
    Play Sonso's three rounds back to back and ask: **can you tell his mood without reading any text?** If the arena shrank and shook, the answer is yes — and the customisation has done its job, which is to perform alongside the character.

---

## Common problems

| Symptom | Cause |
|---|---|
| Instance-not-found error when touching the box | you configured it in Create or User Event 0; the box only exists from User Event 2 |
| Variable-not-set error in Step, right as the fight starts | missing `if timer == 0 exit` — the turn object runs several frames before the box exists |
| `pattern_pool` stopped choosing | you overrode User Event 2 without `event_inherited()` |
| The arena is the wrong size after swapping sprites | you did not recalculate `sprite_w` / `sprite_h` |
| The soul cannot get into the arena | the mask is filled; it must be hollow |
| The soul passes through the wall when the box turns | you changed `image_angle` on something that is not the box |
| Invisible obstacles | `o_enc_box_solid` is born with `visible = false` and no sprite |
| Last round's obstacles are still there | you did not destroy them in the turn object's Destroy |
| Two identical enemies attack as one | expected — use `buff`, or `allow_same_turns = true` |
| Your background does not appear | `bg_type` is still `GRID`, or the object was not created in `ev_init` |
| The background appears **in front of** the enemies | depth is lower than `DEPTH_ENCOUNTER.BACKGROUND` — in GameMaker, larger is further back |
| The background drifts when the camera is not at the origin | you forgot `guipos_x()` / `guipos_y()` in the drawing |
| The background stays on screen after the fight | the `Step` that self-destroys is missing |
| Stars (or other decoration) jitter around | you roll positions inside `Draw`; roll them in `Create` and store an array |
| The fight never ends | `win_condition` never returns `true` |

---

## Quick reference

!!! warning "In the Step, always after `if timer == 0 exit`"
    The box only exists from User Event 2 onward. In the Step, put `if timer == 0 exit` right after `event_inherited()` before touching `o_enc.mybox`.

!!! info "`o_enc_box` and `o_enc.mybox` are the same box"
    The engine uses both forms: `o_turn_default` writes `o_enc_box.x`, `o_ex_turn_complex_box` writes `o_enc.mybox.x`. There is only one instance per turn, so it makes no difference. Use `o_enc.mybox` when you want to make clear it is *this* battle's box.

```gml
// the box (exists from the turn object's User Event 2 onward)
o_enc.mybox.width / .height      // size, default 75x75
o_enc.mybox.x / .y               // position
o_enc.mybox.image_angle          // tilt
o_enc.mybox.sprite_index         // frame
o_enc.mybox.mask_index           // walls (HOLLOW mask)
o_enc.mybox.sprite_back          // interior fill
o_enc.mybox.color                // frame colour
// after swapping sprites: recalculate sprite_w / sprite_h

// obstacles: any extra o_enc_box_solid becomes a wall
instance_create(o_enc_box_solid, xx, yy, DEPTH_ENCOUNTER.BOX - 1)
// remember sprite_index, visible = true, and destroying them in Destroy

// in enc_set()
enemies             // how many and which
enemies_pos         // [[x, y, relative], ...] or function(i, xx, yy)
party_pos           // function(i) -> [x, y]
bg_type             // ENC_BG.GRID | ENC_BG.NONE
win_condition       // function() -> bool
target_calculation  // ENC_TARGET.RANDOM | ANY | ALL
display_target      // show who is about to be hit
bgm / bgm_pitch / bgm_gain

// in the turn object
buff                // how many identical enemies attack together (0 = just one)
allow_same_turns    // false: duplicate turns become buff; true: independent turns

// utilities
sine(divisor, amplitude)                            // per-frame sine
animate(from, to, frames, curve, inst, "field")     // animate any variable
```
