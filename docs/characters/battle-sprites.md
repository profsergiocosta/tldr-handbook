# Battle sprites and icons

Right now Berto fights **as Susie**: you registered him in the
[previous chapter](first-party-member.md), and everything you did not set in
`party_m_berto` came from the base `party_m`, which holds Susie's battle sprites. This
chapter gives him his own, plus his own menu icons.

It is the biggest art job in Part 5, so it is done **one piece at a time**: first you
see him fight with the borrowed sprites, then you replace them in the order the battle
needs them, testing after each.

---

## How the engine finds a battle sprite

Overworld sprites are found **by name** (`spr_berto_down`). Battle sprites are not:
they are listed, directly as assets, in a struct called `battle_sprites` inside the
party member. Here is Noelle's, trimmed (`scripts/party_init/party_init.gml`, in
`party_m_noelle`):

```gml
battle_sprites = {
    idle:       spr_bnoelle_idle,
    hurt:       spr_bnoelle_hurt,
    attack:     [spr_bnoelle_attack, true],
    actend:     [spr_bnoelle_actend, "idle", 1],
    // ...
}
```

Each entry is one of three shapes:

| Shape | Meaning |
|---|---|
| `spr_x` | Just play this sprite (it loops). |
| `[spr_x, true]` | Play once and **freeze on the last frame**. |
| `[spr_x, "idle", 1]` | Play once, then **switch to another entry** (here `idle`) at the given speed. |

This is decided when the animation ends (`objects/o_actor/Other_7.gml`).

The keys, and when the battle asks for each:

| Key | When it is used |
|---|---|
| `idle` | Standing in battle. Also used to measure his height for centring (`party_getbattleheight`). |
| `hurt` | When he takes a hit. |
| `defeat` | When his HP is zero or below. |
| `attack` | During the attack (the FIGHT timing bar), and in the battle intro. |
| `attackready` | Once FIGHT has been chosen for him, while he waits for the attack to start. |
| `attack_eff` | The slash effect shown on the enemy when the attack lands. |
| `actready`, `act`, `actend` | ACT chosen for him, performing the act, returning to idle. |
| `spellready`, `spell` | A spell chosen, casting. |
| `itemready`, `itemuse` | An item chosen, using it. |
| `defend` | The Defend button. |
| `spare` | Sparing an enemy. |
| `victory` | When the fight is won. |
| `intro`, `introb` | The battle intro, depending on `s_battle_intro` (below). |

### What happens if an entry is missing

For most keys, nothing bad: when the battle asks for a sprite the party member does not
have, the actor **keeps whatever it was showing**
(`enc_party_set_battle_sprite`, `scripts/enc_scripts/enc_scripts.gml`). So a character
without an `act` sprite simply does not change pose when you ACT.

Three keys are different, because the engine reads them directly: **`idle`**,
**`hurt`** and **`defeat`**. Treat those, plus **`attack`** and **`attack_eff`**, as
required. I have not run a battle with them deliberately missing, so this is read from
the code, not tested.

!!! danger "Every sprite you name must exist"
    The struct refers to sprites as assets, not as text. If you write
    `spr_bberto_idle` and that sprite does not exist in the Asset Browser, the game does
    not show a placeholder: it fails. Create the sprite first, then add it to the
    struct.

### What `s_battle_intro` does

`s_battle_intro` in the constructor chooses how the battle begins
(`objects/o_enc_anim/Alarm_1.gml` and `Alarm_2.gml`):

| Value | Behaviour |
|---|---|
| `0` | Plays your `intro` sprite as the full intro. |
| `1` | No intro sprite; he goes straight to the `attack` pose. This is the base default. |
| `2` | Uses your `introb` sprite during the intro, then `attack`. |

Leave it at `1`. That way you need neither `intro` nor `introb`.

---

## Step 1 — See him fight as Susie

Before drawing, confirm the pipeline works. Open `room_test_characters`, add Berto to
the party with ++tab++ + ++p++ (right arrow four times, ++enter++), then start a fight
with ++tab++ + ++e++ (Encounter Select) and pick any encounter.

Berto fights, with Susie's sprites and Susie's placeholder icon. (If the game crashes the first time he attacks, with `weapon_element` in the error, he has no weapon: see the danger box in [Your first party member](first-party-member.md), Step 2.) Use ++tab++ + ++w++ to
leave the fight. If this step fails, fix it before drawing anything.

---

## Step 2 — Replace `idle`, `hurt` and `defeat`

These three come first because the engine reads them directly.

### What to draw

Look at what the engine's own characters use, so yours are consistent:

| Sprite | Size (Noelle) | Frames | Fps | Origin |
|---|---|---|---|---|
| `spr_bnoelle_idle` | 26 × 46 | 5 | 6 | 14, 46 |
| `spr_bnoelle_hurt` | 32 × 46 | 1 | 0 | 15, 46 |
| `spr_bnoelle_defeat` | 23 × 46 | 1 | 0 | 11, 46 |

Two rules to copy:

- **The origin is at the feet**, as in the overworld (the bottom row of the sprite, on the
  horizontal centre of the body). Keep it in the **same place for all of a character's
  battle sprites**: if `idle` has the origin at `(14, 46)` and `attack` at `(30, 20)`,
  Berto jumps every time the sprite changes. A pixel of difference, like Noelle's
  `hurt`, is fine.
- Different poses may be **different widths** (Noelle's idle is 26 wide, her act is
  51 wide), but the **height stays the same** (46) so the feet stay on the ground.

Animated sprites use the Fps of the engine's own: about 6 for idle. `hurt` and
`defeat` are a single frame, so Fps does not matter for them.

### Wire them in

1. Create **`spr_bberto_idle`**, **`spr_bberto_hurt`** and **`spr_bberto_defeat`**, with
   the origin at the feet.
2. In `party_m_berto` (your script), add below `s_name`:

    ```gml
    s_battle_intro = 1

    battle_sprites.idle   = spr_bberto_idle
    battle_sprites.hurt   = spr_bberto_hurt
    battle_sprites.defeat = spr_bberto_defeat
    ```

    This only works because each party member gets its **own** copy of the base
    `battle_sprites` struct. You are replacing three entries in Berto's copy; the other
    entries are still Susie's, and Susie is not affected.

3. Run, add Berto, start a fight. In the fight, Berto stands as himself. Take a hit on
   purpose (let an enemy attack) to see `hurt`, and let his HP reach zero to see `defeat`.

!!! warning "A mixed set will look off"
    While the other entries are still Susie's, he changes from his sprite to hers when
    he attacks, and the origins will not line up. That is expected. The next steps
    remove it.

---

## Step 3 — The attack

Now the fight itself: **`attackready`** (FIGHT highlighted), **`attack`** (the action)
and **`attack_eff`** (the slash on the enemy).

| Sprite | Size (Noelle) | Frames | Fps | Origin |
|---|---|---|---|---|
| `spr_bnoelle_attackready` | 23 × 46 | 1 | 0 | 11, 46 |
| `spr_bnoelle_attack` | 37 × 46 | 5 | 10 | 14, 46 |
| `spr_bnoelle_attackeff` | 44 × 45 | 4 | 15 | 22, 22 |

`attack_eff` is the exception to the feet rule: it is an **effect**, so its origin is its
**centre** (22, 22 on a 44 × 45 sprite), because it is drawn on top of the enemy.

```gml
battle_sprites.attackready = spr_bberto_attackready
battle_sprites.attack      = [spr_bberto_attack, true]
battle_sprites.attack_eff  = spr_bberto_attackeff
```

`attack` is `[sprite, true]`: it plays once and **freezes on its last frame**, which is
how the engine holds the pose at the end of the swing.

Test: in a fight, choose FIGHT for Berto (he takes his ready pose) and attack.

---

## Step 4 — The rest

These are optional (see *What happens if an entry is missing*), and each can be added
later, one at a time. A character without them just does not change pose for that
action.

| Entry | Suggested shape |
|---|---|
| `act` | `[spr_bberto_act, true]` |
| `actready` | `spr_bberto_actready` |
| `actend` | `[spr_bberto_actend, "idle", 1]` |
| `spell` / `spellready` | `[spr_bberto_spell, "idle", 1]` / `spr_bberto_spellready` |
| `itemuse` / `itemready` | `[spr_bberto_item, "idle", 1]` / `spr_bberto_itemready` |
| `defend` | `[spr_bberto_defend, true]` |
| `spare` | `[spr_bberto_act, "idle", 1]` (Noelle and Susie reuse their `act`) |
| `victory` | `[spr_bberto_victory, true]` |

These shapes come from Noelle's and Susie's structs. `defend` is a plain sprite for
Noelle and `[sprite, true]` for Susie; either works.

When you have everything, you can stop patching the base struct and **write the whole
struct** in the constructor instead, so that nothing of Susie's is left:

```gml
battle_sprites = {
    act:         [spr_bberto_act, true],
    actready:    spr_bberto_actready,
    actend:      [spr_bberto_actend, "idle", 1],
    attack:      [spr_bberto_attack, true],
    attackready: spr_bberto_attackready,
    defeat:      spr_bberto_defeat,
    defend:      [spr_bberto_defend, true],
    hurt:        spr_bberto_hurt,
    idle:        spr_bberto_idle,
    intro:       spr_bberto_idle,   // unused while s_battle_intro = 1
    introb:      spr_bberto_idle,   // unused while s_battle_intro = 1
    itemuse:     [spr_bberto_item, "idle", 1],
    itemready:   spr_bberto_itemready,
    spell:       [spr_bberto_spell, "idle", 1],
    spellready:  spr_bberto_spellready,
    victory:     [spr_bberto_victory, true],
    spare:       [spr_bberto_act, "idle", 1],
    attack_eff:  spr_bberto_attackeff,
}
```

Remember: every sprite named there must already exist.

---

## Step 5 — Icons

Three small sprites represent him in the menus. Berto currently uses the engine's
placeholders (`spr_ui_default_icon` and `spr_ui_default_head`).

| Field | Where it appears | Size (all base-game ones) | Origin |
|---|---|---|---|
| `s_icon` | The battle box, and the party menu | 35 × 24 | 0, 0 |
| `s_icon_ow` | Party Select and the overworld menu | 25 × 20 | 0, 0 |
| `s_icon_weapon` | The equipment menu | 13 × 18 | 0, 5 |

For icons, the origin is the **top-left**, the opposite of the character sprites.

Create `spr_ui_berto_icon` (35 × 24), `spr_ui_berto_head` (25 × 20) and
`spr_ui_berto_icon_hurt` (35 × 24), and set:

```gml
s_icon    = spr_ui_berto_icon
s_icon_ow = spr_ui_berto_head
```

Notice the third sprite: when a party member is hurt, the battle box swaps the icon
for the one **named after it plus `_hurt`** (`party_get_icon_hurt`,
`scripts/party_get/party_get.gml`). Noelle has `spr_ui_noelle_icon` and
`spr_ui_noelle_icon_hurt`. You never write the hurt one into the constructor; the
engine builds its name, so it must be spelled exactly `<icon name>_hurt`. I have not
tested what happens when it is missing, so create it.

For `s_icon_weapon`, the engine ships a few weapon icons (`spr_ui_menu_weapon_sword`,
`_axe`, `_ring`). Pick the one that matches his weapon until you draw your own.

---

## Common problems

| Symptom | Likely cause |
|---|---|
| The game fails when a fight starts | A sprite named in `battle_sprites` does not exist, or is misspelled |
| Berto jumps sideways or up when the pose changes | The origins of his battle sprites do not match |
| He floats above or sinks into the ground | The battle sprite's origin is not at the feet |
| He shows Susie's pose for an action | That entry is not replaced yet (Step 4), or it is misspelled |
| The slash effect appears off-centre | `attack_eff`'s origin is not its centre |
| The battle box shows a grey placeholder icon | `s_icon` is not set, or the sprite is missing |

I have read each of these steps in the engine's code, but have not run a custom
character through a full fight in GameMaker. If a step does not behave as written,
treat it as a bug in this chapter.

## Next

[Stats, equipment and spells](stats-and-equipment.md) gives Berto his **own stats, weapon, armour and spells**, instead of
the values he inherited from the base party member.
