# Your first enemy

From an empty file to a playable fight, in nine steps. Every step ends with something you can **run**, and you never write more than about twenty lines without testing.

If you have not read [How a fight works](overview.md), read at least Part 1 first. This chapter assumes you know what MERCY and ACTs are for.

---

## What we are building

A stray cat called **SONSO**.

He is not a monster. He is a cat — and the design joke is that **the obvious button is the wrong one**. The player will try to `Call` the cat ("here, kitty"), because that is what you do with a cat. Sonso will turn his back, offended, and attack harder.

What works is the opposite: **`Ignore`**. Look away. Then he comes to you on his own.

That is the heart of this genre — the enemy is not a bag of HP, it is a small social puzzle. And the best part: his **mood** changes the **bullet pattern**. The player learns they made a mistake not by reading text, but because the attack got worse.

| Mood | How you get there | What he says | The attack |
|---|---|---|---|
| `calm` (initial) | start of the fight | "does nothing, deliberately" | **Swipes** — three horizontal claw marks, alternating sides |
| `annoyed` | use **Call** | "hisses, ears back" | **Hiss** — fast drizzle plus a **blue pounce** (let go of the stick!) |
| `curious` | use **Ignore** | "pretends to look elsewhere" | **Purr** — an **orange** ring closing in slowly (do not stand still!) |

Two uses of `Ignore` (+50 MERCY each) and he sits down. Peaceful ending.

!!! tip "Why a cat?"
    Because the mechanic *is* the character. You never have to write a line of dialogue saying the cat is proud — the player finds out by getting hit. When you invent your own enemy, start there: **which human behaviour becomes a button rule?**

---

## Step 0 — Where everything lives

Four pieces, four places:

| Piece | Where you write it | Name we will use |
|---|---|---|
| The enemy **sheet** (`enemy()`) | `scripts/rpg_enc_enemies/rpg_enc_enemies.gml` | `rpg_enemy_sonso()` |
| The **encounter** (`enc_set()`) | `scripts/rpg_enc_sets/rpg_enc_sets.gml` | `rpg_enc_set_sonso()` |
| The **turn** (bullet pattern) | a new object, parent `o_turn` | `o_turn_sonso` |
| The **actor** (the body on screen) | none! we use `o_actor_e` | — |

Both scripts already exist in the project. Only the turn object gets created from scratch, in step 6.

For sprites we use the **tasque** set, which is already in the project and unused by any enemy: `spr_ex_e_tasque`, `spr_ex_e_tasque_hurt`, `spr_ex_e_tasque_spared`. When you draw your own, it is three lines to swap.

!!! warning "The rule that avoids 90% of the pain"
    A bare identifier in GML resolves as an **asset name at compile time**. If the sprite does not exist under that exact name, the project will not compile (`spr_xxx not defined`). A **struct field** with a wrong name, on the other hand, **never errors** — it is silently created and never read.

    So: a wrong sprite name you find immediately; `maxhp` instead of `max_hp` you find an hour into testing.

---

## Step 1 — The minimum enemy that compiles

Open `scripts/rpg_enc_enemies/rpg_enc_enemies.gml`:

```gml
function rpg_enemy_sonso() : enemy() constructor {
    name = "Sonso"
    obj  = o_actor_e          // the engine's generic actor; perfectly fine

    // stats
    hp      = 60
    max_hp  = 60              // mind the underscore: maxhp does NOT exist
    attack  = 4
    defense = 1
    carrying_money = 12

    // sprites (already in the project)
    s_idle  = spr_ex_e_tasque
    s_hurt  = spr_ex_e_tasque_hurt
    s_spare = spr_ex_e_tasque_spared

    dialogue = "* Meow."

    turn_object = o_turn_default   // for now: one stationary bullet
}
```

That is all. Everything else — `mercy`, `acts`, `can_spare`, the hooks — comes from the `enemy()` base with usable defaults.

!!! info "About `attack = 4`"
    `attack` is a **stat**, not damage. The formula is `5 * att` minus the party member's defence (`scripts/party_hp/party_hp.gml:225`), so 4 costs about **20 HP** per hit — a reasonable early-game number. For a harmless cat, use 2.

---

## Step 2 — The encounter

Open `scripts/rpg_enc_sets/rpg_enc_sets.gml`:

```gml
function rpg_enc_set_sonso() : enc_set() constructor {
    debug_name = "sonso"                    // the name shown in the console

    enemies = [ new rpg_enemy_sonso() ]     // note the `new`

    flavor = "* A cat is blocking the way. Technically."

    enemies_pos = [ [0, 0, true] ]          // [x, y, relative to default spot]
    bgm = mus_battle
}
```

!!! warning "`flavor` belongs to `enc_set()`, not `enemy()`"
    It is the **encounter's** text, shown above the menu each round — not the creature's speech. Put `flavor` inside `enemy()` and it simply does nothing, with no error. The creature's line is `dialogue`, and it appears in a bubble.

---

## Step 3 — Test now (do not build a room yet)

1. Run the game.
2. ++tab++ opens the console.
3. Type `encounter_select`.
4. Pick **`sonso`**.

The fight opens immediately. You should see the cat, the five-button menu, the "* Meow." bubble, and — after confirming actions — a black box with one stationary bullet.

If `sonso` is not in the list, the file did not compile. Check the **Output** window.

This loop — edit → ++tab++ → `encounter_select` — is how you will work for the rest of this chapter. **Do not build a room until step 9.**

!!! tip "Console commands that save time"
    `encounter_end` ends the turn instantly (useful when you lock the fight up with a bad `timer_end`), and `party_select` changes who is in the party.

---

## Step 4 — Giving him a voice

Now the cat gets state. We keep the mood **on the enemy struct itself** — GML structs accept new fields without complaint, and the `enemy()` survives the whole fight, so it is the right place for short-term memory.

Replace `dialogue = "* Meow."` with this, and add the two new fields above it:

```gml
    // --- Sonso's own state (our fields, not the engine's) ---
    mood  = "calm"      // "calm" | "annoyed" | "curious"
    calls = 0           // how many times the player insisted on calling

    dialogue = method(self, function() {
        switch mood {
            case "annoyed":
                return "* Sonso hisses. His ears are flat."

            case "curious":
                return "* Sonso pretends to look the other way."

            default:
                if o_enc.turn_count == 0
                    return "* A cat stares at you. He is not impressed."

                return choose(
                    "* Sonso licks a paw.",
                    "* Sonso yawns.",
                    "* Sonso does nothing. On purpose."
                )
        }
    })
```

Two things matter here.

**Why `method(self, ...)`?** Because the function reads `mood`, a field of the enemy itself. `method(self, ...)` binds the function to the struct so `mood` resolves. It is the idiom the engine uses (`scripts/enc_enemies/enc_enemies.gml:363`).

**`dialogue` receives no arguments.** The base struct's comment says it "can accept the slot as arg0", but the call site is `variable_callable_to_value(enemies[i].dialogue)` — with **no arguments** (`objects/o_enc/Step_0.gml:254`). Writing `function(slot)` gives you `undefined`. If you need the index, use `self.slot`, which the engine fills in (`objects/o_enc_anim/Alarm_1.gml:69`).

The encounter's `flavor` can react too. Back in `enc_set()`:

```gml
    flavor = function() {
        if o_enc.turn_count == 0
            return "* A cat is blocking the way. Technically."

        switch o_enc.encounter_data.enemies[0].mood {
            case "annoyed": return "* The air is tense. And furry."
            case "curious": return "* Sonso is closer than he was."
            default:        return "* Smells like a warm roof."
        }
    }
```

**Test.** The text does not change yet — nothing touches the mood — but round 0 already reads differently from the rest.

---

## Step 5 — The ACTs: the puzzle

### What an ACT is

In the battle menu, **ACT** is the middle button — the one that hurts nobody. While `FIGHT` removes HP and `ITEM` uses inventory, ACT opens a submenu of **actions written specifically for that creature**: Check, Call, Ignore, Compliment, Dance, whatever the scene needs.

That is where the peaceful route runs: the right ACT fills the **MERCY** bar, and MERCY at 100 lights up **SPARE**.

### Where the code goes

`acts` is **a field of the `enemy()` struct**, like `hp` or `s_idle`. It goes **inside** the function you wrote in step 1:

```gml
function rpg_enemy_sonso() : enemy() constructor {
    name = "Sonso"
    hp   = 60
    // ... everything else you already wrote ...

    acts = [        // ←— HERE, still inside the constructor's braces
        { ... },    // each struct is one button in the submenu
        { ... },
    ]
}                   // ←— the brace that closes the constructor
```

It is an **array of structs**: each `{ ... }` is a button, in the order you write them. The `enemy()` base ships with a sample "Check" ACT, and whatever you write **replaces the whole array**.

!!! warning "Only Kris has the ACT button"
    The second menu slot is **ACT** for a character carrying `item_s_act`, and **MAGIC** for everyone else (`objects/o_enc/Create_0.gml:82`). In this project only Kris has it (`scripts/party_init/party_init.gml:152`). If you test with Susie and cannot find ACT, that is why.

    To give the others their own action, use the sibling field `acts_special`, one entry per character — see the virovirokun at `scripts/enc_enemies/enc_enemies.gml:239`.

### Sonso's three ACTs

One that informs, one that **looks** right and is wrong, and one that looks useless and is the answer:

```gml
    acts = [
        {
            name: "Check",
            desc: "Useless analysis",
            party: [],
            exec: function(slot, user) {
                encounter_scene_dialogue(
                    "* SONSO - ATK 4 DEF 1{br}{resetx}"
                  + "* Stray cat. Decides for himself who he likes.{br}{resetx}"
                  + "* Hates being called."
                )
            }
        },
        {
            name: "Call",
            desc: "Here, kitty kitty",
            party: [],
            exec: function(slot, user) {
                var me = o_enc.encounter_data.enemies[slot]
                me.calls ++
                me.mood = "annoyed"

                audio_play(snd_ui_cant_select)

                if me.calls == 1
                    encounter_scene_dialogue("* " + party_getname(user) + " called Sonso.{br}{resetx}* He turned his back.")
                else
                    encounter_scene_dialogue("* " + party_getname(user) + " called again.{br}{resetx}* Now he is OFFENDED.")
            }
        },
        {
            name: "Ignore",
            desc: "Stare intently at literally anything else",
            party: [],
            exec: function(slot, user) {
                var me = o_enc.encounter_data.enemies[slot]
                me.mood = "curious"

                enc_enemy_add_spare(slot, 50)   // half the MERCY bar

                encounter_scene_dialogue("* " + party_getname(user) + " stared at nothing.{br}{resetx}* Sonso took a step closer.")
            }
        }
    ]
```

### Three rules about `exec`

**The signature is `function(slot, user)`.** `slot` is the enemy's index in `o_enc.encounter_data.enemies`; `user` is the **name** of whoever acted, a string (`"kris"`, `"susie"`). The engine calls it as `method_call(act.exec, array_concat([target, acting_member], exec_args))` (`scripts/enc_actions/enc_actions.gml:93`). Extra arguments come from the `exec_args` field.

**Inside `exec`, `self` is NOT the enemy.** Unlike `dialogue`, this function sits inside a *struct literal* in the middle of an array, so it is not bound to the `enemy()`. That is why the first line is always `var me = o_enc.encounter_data.enemies[slot]`.

**Text uses `encounter_scene_dialogue()`, never `dialogue_start()`.** The latter is the overworld box and opens in the wrong place. `{br}{resetx}` is the pair the engine uses to break a line and return to the left margin.

!!! info "The `party` field decides who sees the ACT"
    `[]` = anyone. `["susie"]` = Susie only. `["susie", "ralsei"]` = a joint ACT requiring both in the party. `-1` = a whole-party ACT. Listing someone who is not in the party simply hides it, with no error.

**Test.** Use `Call` and watch the line change next round. Use `Ignore` twice and the **SPARE** button lights up. Spare him — the cat should switch to `spr_ex_e_tasque_spared` and the fight ends.

---

## Step 6 — His own turn object

Until now the cat uses `o_turn_default` — one stationary bullet. Time to give him claws.

### 6.1 Creating the object

1. **Asset Browser** → right-click your objects folder → **Create → Object**. Name it **`o_turn_sonso`**.
2. **Sprite: none.** It is an invisible controller.
3. **Parent: `o_turn`.** The Parent field is right below Sprite. Click *No Object Selected* and pick `o_turn`. **This is the easiest step to forget and nothing works without it** — no `timer`, no `enemy_struct`, no `__support_destroy_check()`.
4. Save (++ctrl+s++).

Then point the enemy sheet at it, back in `rpg_enc_enemies.gml`:

```gml
    turn_object = o_turn_sonso
```

!!! danger "The event you open may be the PARENT's"
    Once the Parent is set, `o_turn_sonso`'s event list also shows the events inherited from `o_turn`. Clicking one opens **`o_turn`'s** code — which is why you may find yourself staring at a Create event full of `buff = 0`, `pattern_pool = [1]` and `__support_init_default = function() { ... }`. That is the engine's code.

    Always check the **tab title** of the code window: it must say `o_turn_sonso : Create`, not `o_turn : Create`. Typing over `o_turn` breaks the turn for **every** enemy in the game.

### 6.2 The events, one at a time

Four events. Use **Add Event** inside `o_turn_sonso`. Since `o_turn` already has these events, GameMaker will warn you the event is inherited and offer to call the parent version — **accept**. It writes `event_inherited();` on the first line, which is exactly what you want.

#### Event 1 — Create

**Add Event → Create.** Paste:

```gml
event_inherited()

_side = choose(-1, 1)   // which side the first swipe comes from
```

One variable for now. Rolling it in Create rather than Step makes each fight start differently without being random mid-turn.

#### Event 2 — User Event 0

**Add Event → Other → User Events → User Event 0.** Paste:

```gml
event_inherited()
__support_init_default()

// this turn's pattern IS the cat's mood
pattern = enemy_struct.mood

if !am_support {
    switch pattern {
        case "annoyed": timer_end = 150 break   // 5s — longest and densest
        case "curious": timer_end = 90  break   // 3s — almost affectionate
        default:        timer_end = 120 break   // 4s
    }
}
```

This is the turn's **init**, and it is where character meets mechanic: this turn's `pattern` literally becomes the cat's mood.

Two non-obvious things:

**`enemy_struct` is already filled in.** The engine creates the turn object passing `{enemy_index, enemy_struct}` in the creation struct and only *then* calls User Event 0 (`objects/o_enc/Step_0.gml:249`).

**Your `pattern` will not be overwritten.** The `o_turn` base draws a `pattern` from `pattern_pool` later, in User Event 2 — but with `??=`, so **only if it is still `undefined`**. Yours wins.

#### Event 3 — Step

**Add Event → Step → Step.** Paste:

```gml
event_inherited()          // ← THIS is what makes timer_end work

if timer == 0
    exit                   // the box and soul do not exist yet

// (bullet patterns arrive in step 7)

__support_destroy_check()
```

**`event_inherited()` here is mandatory.** The `timer` that counts and the `timer_end` that ends the turn live in the parent's Step. Forget it and the turn never ends, freezing the battle.

**`if timer == 0 exit` is not decoration either.** The turn object is created during `DIALOGUE`, several frames before `o_enc.mybox` exists, and its Step runs the whole time. It is the engine's own idiom — see `objects/o_turn_default_dark/Step_0.gml`.

#### Event 4 — Destroy

**Add Event → Destroy.** Paste:

```gml
event_inherited()               // returns the enemy to its idle sprite
instance_destroy(o_enc_bullet)  // and collects orphaned bullets
```

**Cleaning up bullets is not optional.** Nothing in the engine collects them — they fly out of the box and keep existing. Without this line, round two starts with round one's litter crossing the screen. The engine does this in `o_ex_turn_complex_box/Destroy_0.gml`.

**`event_inherited()` matters here too.** The parent's Destroy returns the enemy to its idle sprite (`objects/o_turn/Destroy_0.gml`). Without it, an enemy that changed sprite mid-attack stays frozen in the attack pose. `o_turn_default` forgets this call — it only gets away with it because it never changes anyone's sprite.

!!! info "The two events you should NOT create"
    `o_turn` also has **User Event 1** (sets `turn_started = true`, which is what starts the `timer`) and **User Event 2** (draws `pattern` from `pattern_pool`). Sonso needs neither — **do not add them** and let the parent handle it. Adding User Event 1 and forgetting `event_inherited()` freezes the battle.

### 6.3 Test

The cat now attacks with… nothing, for 3 to 5 seconds depending on mood. But the box opens and closes on its own, which is exactly what we wanted to confirm before writing any pattern.

---

## Step 7 — Moods become bullet patterns

Everything goes in `Step_0.gml`, between the guard and `__support_destroy_check()`. Remember: **30 frames is one second.**

### Mood `calm` — the Swipes

Three parallel claw marks entering from one side, then the other. The **gap between the claws** is the path — the player has to read where it is and position for it.

```gml
if pattern == "calm" {
    if timer % 30 == 0 && timer < timer_end - 30 {
        _side *= -1                              // alternate left/right
        var _gap = irandom_range(-20, 20)        // where the hole is

        for (var i = -1; i <= 1; i ++) {
            instance_create(o_enc_bullet,
                o_enc_box.x + 80 * _side,
                o_enc_box.y + _gap + i * 26,
                DEPTH_ENCOUNTER.BULLETS_OUTSIDE, {
                    speed: 3,
                    direction: (_side == 1 ? 180 : 0),
                    att: 4
                })
        }
    }
}
```

`_side * 80` spawns them **outside** the box, which is 75px wide. That is deliberate: a bullet that appears on top of the soul is unfair. The player needs to see it coming.

### Mood `annoyed` — the Hiss

You called the cat. Now he fills you with fur and pounces.

```gml
else if pattern == "annoyed" {
    // 1) fast drizzle from above
    if timer % 10 == 0 && timer < timer_end - 50 {
        instance_create(o_enc_bullet,
            o_enc_box.x + irandom_range(-32, 32),
            o_enc_box.y - 60,
            DEPTH_ENCOUNTER.BULLETS_OUTSIDE, {
                speed: 4, direction: 270, att: 4
            })
    }

    // 2) THE POUNCE: a BLUE wall crosses the whole box
    if timer == timer_end - 45 {
        audio_play(snd_spawn_attack)

        instance_create(o_enc_bullet,
            o_enc_box.x - 100, o_enc_box.y,
            DEPTH_ENCOUNTER.BULLETS_OUTSIDE, {
                color: BULLET_COLOR.BLUE,
                speed: 4, direction: 0, att: 5,
                image_xscale: 1.5, image_yscale: 6    // 22 x 90 px — undodgeable
            })
    }
}
```

!!! warning "Blue is the opposite of what it looks like"
    In tlDR, **`BLUE` only hurts a soul that is moving** (`objects/o_enc_bullet/Other_10.gml`). There is no platforming, no jump — the soul is always red and always moves the same. The correct response to a blue bullet is to **let go of the stick**.

    And that is why the wall is 90px tall in a 75px box: if it can be dodged, the player dodges it and never learns the rule. A blue bullet **must** be impossible to avoid.

### Mood `curious` — the Purr

You ignored him and he came closer. The attack becomes a slow orange encirclement: he circles you, and you cannot freeze.

```gml
else if pattern == "curious" {
    if timer == 10 {
        for (var i = 0; i < 10; i ++) {
            var _ang = i * 36                      // 360/10

            instance_create(o_enc_bullet,
                o_enc_box.x + lengthdir_x(90, _ang),
                o_enc_box.y + lengthdir_y(90, _ang),
                DEPTH_ENCOUNTER.BULLETS_OUTSIDE, {
                    color: BULLET_COLOR.ORANGE,
                    speed: 1, direction: _ang + 180,
                    att: 3
                })
        }
    }
}
```

`ORANGE` mirrors blue: **it only hurts a soul that is standing still**. A slowly closing ring is the perfect setting, because the player's instinct is to shrink toward the centre and wait — exactly what kills them.

!!! info "Why does the friendly mood get the harder attack?"
    It is not harder, it is **slower**. `curious` lasts 3 seconds with 10 bullets at speed 1; `annoyed` lasts 5 seconds and spits one bullet every 10 frames. The emotional reading still holds: the annoyed cat is a storm, the curious one is a lazy circling. Difficulty in a bullet hell is **density × time**, not speed alone.

**Test all three.** Enter the fight and watch the Swipes. Use `Call` and take a beating. Use `Ignore` and watch the encirclement. This is the moment the enemy stops being a table of numbers and becomes a character.

---

## Step 8 — Polish

### 8.1 The cat reacts to being hit

**Where:** inside `rpg_enemy_sonso()`, in `rpg_enc_enemies.gml` — it is a struct field like any other:

```gml
function rpg_enemy_sonso() : enemy() constructor {
    // ... name, hp, sprites, mood, dialogue, acts ...

    ev_hurt = method(self, function() {      // ←— HERE, inside the constructor
        if hp <= max_hp * 0.4 && mood != "annoyed" {
            mood = "annoyed"
            enc_enemy_set_tired(slot, true)
        }
    })
}
```

`ev_hurt` is one of the `enemy()` **hooks**: fields the engine calls at specific moments. They all ship disabled (`-1`) and come alive the moment you assign a function. The others are `ev_init`, `ev_pre_dialogue`, `ev_dialogue`, `ev_turn`, `ev_turn_start`, `ev_post_turn`, `ev_party_exec` and `ev_win`.

`enc_enemy_set_tired` marks the enemy **TIRED** — a state mercy spells look for.

!!! warning "`ev_hurt` runs BEFORE damage is applied"
    Look at the order in `scripts/enc_scripts/enc_scripts.gml:31` — the hook is called, and only then comes `enemy_struct.hp -= hurt`. The `hp` you read inside is the value from *before* this hit, so the cat only gets annoyed on the blow *after* the one that crossed 40%. For "he notices he is losing" that is actually great — it reads as a reaction. If you need the exact post-damage value, use `ev_post_turn`.

    Also, `ev_hurt` is called with **no arguments** (`enemy_struct.ev_hurt()`). Writing `function(dmg)` gives you `undefined`.

### 8.2 Rewarding graze

**Where:** in `o_turn_sonso`'s `Step_0.gml`, inside the `pattern == "calm"` block. This is not new code — it adds two fields to the `instance_create` you already wrote:

```gml
        for (var i = -1; i <= 1; i ++) {
            instance_create(o_enc_bullet,
                o_enc_box.x + 80 * _side,
                o_enc_box.y + _gap + i * 26,
                DEPTH_ENCOUNTER.BULLETS_OUTSIDE, {
                    speed: 3,
                    direction: (_side == 1 ? 180 : 0),
                    att: 4,
                    graze: 4,          // ←— new: double TP
                    time_points: 8     // ←— new: cuts more off the turn
                })
        }
```

!!! info "What grazing is"
    From the English *graze* — to brush past. It is the bullet-hell term, inherited from the Touhou series. Grazing means passing **so close to a bullet that you almost take damage, without taking it**.

    The soul does not travel alone: **`o_enc_soul_grazer`** sticks to it with a larger area. A bullet touching the heart hurts; one touching only the outer ring is a graze, and pays: **TP** (the magic bar) gains the bullet's `graze` value, and the **turn gets shorter** by `time_points` frames.

    It exists for design reasons. Without graze, the optimal play would be to run to the emptiest corner and wait — the player becomes a spectator. With it, getting close **pays**, and dodging becomes a decision.

    Only **`SOLID`** bullets grant graze, and re-grazing the same bullet is worth only `graze/12` — you cannot farm one bullet.

The default `graze` is 2. The Swipes are wide and slow, easy to brush — doubling the prize is the engine saying *come on through the middle*.

### 8.3 How to test what you just did

Neither of these shows itself. You have to provoke it, and playing whole fights over and over is the slow way.

#### The general trick: a throwaway debug ACT

Add a fourth, temporary ACT:

```gml
        {
            name: "DEBUG",
            desc: "testing only - delete later",
            party: [],
            exec: function(slot, user) {
                var me = o_enc.encounter_data.enemies[slot]
                me.mood = "annoyed"            // swap: "calm" | "annoyed" | "curious"
                enc_enemy_set_tired(slot, true)
            }
        },
```

It jumps straight to the state you want to see. It is also the fastest way to check all three bullet patterns from step 7. **Delete it before you call the enemy finished.**

#### Testing `ev_hurt`

The trigger is HP ≤ 40% — with `hp = 60`, below 24. Rather than grinding down to it, lower the health temporarily:

```gml
    hp     = 10
    max_hp = 10
```

One FIGHT crosses the line. What to watch for **the following round** (remember, the hook reads pre-damage HP, so the effect lags a turn):

| Signal | Where to look |
|---|---|
| The enemy's name turns **cyan-blue** | the enemy list in the menu |
| A TIRED icon (`spr_ui_enc_tiredmark`) appears next to the name | same |
| The status now reads `(Tired)` | same |
| The line becomes "Sonso hisses. His ears are flat." | the speech bubble |
| The flavor becomes "The air is tense. And furry." | above the menu |
| The attack becomes the **Hiss** | the dodging phase |

If the name does not change colour, `ev_hurt` did not run: put `show_debug_message("ev_hurt ran!")` as its first line and watch the **Output** window.

#### Testing graze

Graze is too subtle to judge at its final value. **Exaggerate first, calibrate later:**

1. Temporarily change `graze: 4` to **`graze: 40`**. One brush now fills nearly half the TP bar — impossible to miss.
2. Enter the fight and skim past the Swipes without touching them.
3. Watch for **three** signals at once: the sound (`snd_graze`), the ring flashing around the heart, and the **TP bar** climbing on the left.
4. Now change `time_points: 8` to **`time_points: 30`** and notice the turn ending visibly earlier when you play close.
5. Return to the real values and tune to taste.

!!! warning "If graze simply never happens"
    - Is the bullet `BLUE` or `ORANGE`? **Only `SOLID` grazes.**
    - Did you take a hit recently? The grazer is disabled during i-frames.
    - Is it the very start of the turn? The grazer only arms after `o_enc.turn_timer > 10`.
    - Are you brushing the **same** bullet repeatedly? From the second time on it pays `graze/12`.

#### The test that actually matters

Once both work, play the whole fight once with **no** debug and answer: *can you tell the cat's mood changed without reading the text?* If the answer is no, the problem is not the code — the three bullet patterns are still too similar to each other.

### 8.4 Balancing: the numbers that matter

| If testing showed… | Change… |
|---|---|
| the party dies too fast | the bullets' `att` — damage is `5*att`, so 4 → 3 is 5 fewer points per hit |
| the turn drags | `timer_end` in User Event 0 (30 frames = 1s) |
| it is impossible to dodge | the spacing between bullets, not their speed |
| the player never gains TP | the bullets pass too far away — bring the pattern closer to the soul |
| the fight takes too long | the enemy's `hp`, or give more MERCY per ACT |

---

## Step 9 — Putting the cat in the world

Only now is it worth touching a room. There are three ways to start the fight, each with its own gotchas.

### A. From an actor on the map (the canonical way)

Drag an **`o_actor_e`** into the room, select it, and in the inspector's *Variable Definitions* fill **`encounter`** with:

```gml
new rpg_enc_set_sonso()
```

Touching it starts the fight. Other useful variables in the same panel: `enable_chasing`, `chase_spd`, `chase_dist`, `idle_path` (patrol along a Path asset) and `sprite_facing_dir`.

A bonus of this route: the actor already in the room **is reused** as the battle enemy (`o_enc_anim/Alarm_4.gml` tries `actor_find` before creating a new one), so the transition from overworld to fight is continuous.

### B. From a trigger

Drag an **`o_trigger`** into the room and put this in its *Instance Creation Code*:

```gml
trigger_code = function() {
    enc_start(new rpg_enc_set_sonso())
}

trigger_exit_code = function() {
    triggered = false     // re-arm when the player leaves the area
}
```

The code is the easy part. What usually makes a trigger "not work" is **three configuration details**, none of them GML:

**1. Stretch the instance.** `spr_trigger` is **20×20 px** with its origin at the top-left, and `o_trigger` is `visible: false` — you placed an invisible little square the player walks straight past. The engine's own triggers are all stretched: in `room_ex_church` they use `scaleX` between 5 and 7 and `scaleY` 2, giving 100–140 × 40 px.

**2. `o_trigger` fires exactly once.** The entry event sets `triggered = true` and **nothing sets it back** — the exit event only touches `trigger_exit`. Hence the `trigger_exit_code` above. This bites especially hard in a battle: when the fight ends, the party returns to where it started — **standing on the trigger**. Without the re-arm it never fires again until the room reloads. The idiom comes from the engine itself, `rooms/room_ex_church/InstanceCreationCode_inst_2B13ACD5.gml:13`.

**3. The player must be in control.** With `controlled_activation = true` (the default), the Step only fires if `get_leader()._checkmove()` is true (`objects/o_trigger/Step_0.gml:4`), which requires `moveable_console`, `moveable_dialogue`, `moveable_battle` and friends to all be true. In practice: **with the console open (++tab++), no trigger fires.**

!!! tip "30-second diagnosis"
    Put `show_debug_message(">>> TRIGGER FIRED")` as the first line of `trigger_code`. If it never appears in the *Output* window as you walk over it, the problem is collision (1) or control (3) — not your battle code.

!!! info "When NOT to re-arm"
    If the encounter is one-off — the cat was defeated and should not come back — just omit `trigger_exit_code`. One-shot is `o_trigger`'s default behaviour.

### C. From code, anywhere

```gml
enc_start(new rpg_enc_set_sonso())

// exactly identical to:
new rpg_enc_set_sonso()._start()
```

`_start()` is only sugar: the method calls `enc_start(self)` (`scripts/enc_scripts/enc_scripts.gml:157`).

---

## Common problems

| Symptom | Cause |
|---|---|
| `spr_xxx not defined` at compile time | an asset that does not exist — check the name in the Asset Browser |
| Accents do not appear | fonts ship with range 32–127 — see [Fonts and accents](../getting-started/fonts-and-accents.md) |
| Fixed a font and the enemy bubble is still wrong | the bubble uses `font_dotumche`, not the one you fixed |
| The encounter is missing from `encounter_select` | the file did not compile; check the **Output** window |
| The battle freezes and never leaves the turn | missing `event_inherited()` in the turn object's `Step_0.gml` |
| Bullets from the last round appear in the next | missing `instance_destroy(o_enc_bullet)` in `Destroy_0.gml` |
| The HP bar is wrong | you wrote `maxhp` instead of `max_hp` |
| The ACT appears but does nothing | you used `func:` instead of `exec:` |
| The ACT's text opens the overworld box | you used `dialogue_start()` instead of `encounter_scene_dialogue()` |
| `mood` always resets | you created a fresh `enemy()` each round, or read a copy instead of `o_enc.encounter_data.enemies[slot]` |
| The turn ignores the mood | `pattern` was set after User Event 2, and the parent's `??=` already filled it |
| The blue bullet hurts nobody | correct behaviour — `BLUE` only hits a soul that is **moving** |
| Crash while drawing the MERCY bar | `can_spare` was written as a function; it must be a bool |
| A field you wrote is ignored | wrong name — GML structs accept anything without complaint |
| The trigger does not start the fight | the instance is still 20×20 — stretch it |
| The trigger worked once and never again | `triggered` never resets on its own; clear it in `trigger_exit_code` |
| No trigger fires while you test | the console (++tab++) is open |

---

## Taking this to your next enemy

Sonso is a mould. Change the theme and the structure repeats:

1. **Pick a human behaviour**, not a monster. Proud, timid, chatty, sleepy, needy.
2. **Find the button that looks right and is wrong.** That is what turns a menu into a puzzle.
3. **Store the mood in a field on the `enemy()`** and have `dialogue`, `flavor` and `pattern` all read it. One variable, three channels of communication.
4. **Use bullet colour as grammar**: `SOLID` = dodge, `BLUE` = stop, `ORANGE` = move. A small blue bullet teaches nothing; a blue wall teaches on the first try.
5. **Make the peaceful route the faster one.** If killing is always more efficient, the player will kill, and all of your writing goes in the bin.

Next: [The arena](the-arena.md), where the box itself joins the performance.
