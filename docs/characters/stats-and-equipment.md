# Stats, equipment and spells

Berto is registered and has his own sprites, but his numbers are still the base
`party_m`'s: 50 HP, no weapon, no armour, and one test spell. This chapter gives him a
description, three "power" stats for the menu, a weapon, armour and a spell of his own,
testing after each.

You need the previous chapter's `party_m_berto` script. Put the new item constructors in
**another** script of your own, for example **`rpg_items`**, so that the party data and
the items stay separate.

!!! danger "Wipe your save while you iterate"
    Party data is part of the save: when a save file exists, the game **loads Berto's
    stats and equipment from it**, not from your constructor (`save_load` in
    `objects/o_world/Other_2.gml`, the same mechanism that made him disappear in the
    previous chapter). After you change his constructor, old saves keep the old values.
    Use ++tab++ + ++d++ (*Wipe Save Files*) or delete the `save_ch*` files before
    testing a change.

---

## Step 1 — Description and power stats

Open `party_m_berto` and add these fields. Noelle's, for comparison, are
`desc = "party_noelle_desc"` and three `power_stats` (`party_m_noelle` in
`scripts/party_init/party_init.gml`):

```gml
lv   = 1
desc = "A cheerful newcomer with a lot to prove."

power_stats = [
    new party_power_stat("Bravery",    spr_ui_menu_icon_exclamation, 80),
    new party_power_stat("Clumsiness", spr_ui_menu_icon_snow, 12),
    new party_power_stat_images("party_stat_guts", spr_ui_menu_icon_fire, 2),
]
```

- `lv` is the level shown in the menu. The engine's characters use
  `save_get("chapter")` for it; a number is fine.
- `desc` is the description line. As with `name`, a plain string works, because `loc()`
  returns unknown ids unchanged.
- `power_stats` are the three lines of the POWER page. The first two are
  `party_power_stat(name, icon, value)`: a label, an icon and a value. The third, in
  every base-game character, is `party_power_stat_images`, which draws the value as a
  number of repeated icons; `"party_stat_guts"` is the label key the engine already
  translates (*Guts*).
- The icons are sprites the engine ships: `spr_ui_menu_icon_exclamation`, `_snow`,
  `_fire`, `_demon`, `_lollipop`, `_fluff`, and `_none` for no icon.

**Test:** wipe the save, add Berto (++tab++ + ++p++), close Party Select, and open the
menu with ++c++ (or ++ctrl++). His page shows his level, description and the three
stats.

---

## Step 2 — A weapon

A weapon is a constructor that inherits `item_weapon()`. Make it in your `rpg_items`
script:

```gml
// scripts/rpg_items/rpg_items.gml
function item_w_berto_staff() : item_weapon() constructor {
    name = ["Berto's Staff"]
    desc = ["A knobbly walking stick. Attack +3, Magic +2.", "--"]

    weapon_whitelist = ["berto"]    // who may equip it

    stats = {
        attack: 3,
        magic: 2,
    }
    effect = {
        text: "Magic UP",
        sprite: spr_ui_menu_icon_up
    }
    icon = spr_ui_menu_icon_sword

    buy_price = 100
    sell_price = 50
}
item_register(item_w_berto_staff)
```

Four things to notice:

- `weapon_whitelist` lists **registration names** (`"berto"`), not display names. Only
  those characters can equip it. Kris's `item_w_spookysword` uses `["kris"]` the same way
  (`scripts/items_weapons/items_weapons.gml`).
- `stats` are **added** to the character's own stats when equipped, which is why you
  write `attack: 3` and not the total.
- `item_register(...)` after the constructor tags the item for the engine. Every
  base-game item ends with it, so do the same.
- For the Light World, weapons also have an `lw_counterpart`. This chapter leaves it out;
  [the next one](light-world-and-dialogue.md) is about the Light World.

Now equip it in `party_m_berto`:

```gml
weapon = new item_w_berto_staff()
```

**Test:** wipe the save, add Berto, open the menu and look at his stats: **Attack** and
**Magic** should be higher than the base values. In the EQUIP page, the weapon is shown.
The engine applies equipment when the game starts (`party_apply_equipment` in
`o_world`'s Game Start event), so restart the game after changing it.

---

## Step 3 — Armour

Armour is the same shape, inheriting `item_armor()`. The engine's simplest is
`item_a_ambercard` (`scripts/items_armors/items_armors.gml`):

```gml
function item_a_berto_charm() : item_armor() constructor {
    name = ["Berto's Charm"]
    desc = ["A lucky pebble on a string. Defense +2.", "--"]

    stats = {
        defense: 2
    }

    buy_price = 80
    sell_price = 40
}
item_register(item_a_berto_charm)
```

Armour has `armor_blacklist` (the opposite of the weapon whitelist: who may **not** wear
it). Leaving it empty means anyone can.

Equip it in `party_m_berto`. A character has two armour slots:

```gml
armor1 = new item_a_berto_charm()
armor2 = new item_a_ambercard()
```

**Test:** wipe the save, restart, add Berto. His Defense reflects both pieces.

---

## Step 4 — A spell

Spells inherit `item_spell()`. A spell is mostly a **cutscene** that runs in battle. The
smallest working damage spell I could build from the engine's own, `item_s_iceshock`
and `item_s_testdmg`, looks like this:

```gml
function item_s_berto_zap() : item_spell() constructor {
    name = "Zap"
    desc = ["Deals small damage to one enemy.", "Small damage"]
    use_type = ITEM_USE.ENEMY      // the player picks an enemy
    tp_cost = 16                    // percent of the TP bar

    use = method(self, function(spell_user, target, caller = -1) {
        if !enc_enemy_is_fighting(target)
            exit

        cutscene_enc_wait(true)
        cutscene_dialogue(loc_string("item_spell_cast", party_getname(spell_user), string_upper(item_get_name(self))),, false)
        cutscene_sleep(20)
        cutscene_func(function(target, spell_user) {
            var dmg = 40 + party_getdata(spell_user, "magic") * 10
            enc_hurt_enemy(target, dmg, spell_user)
        }, [target, spell_user])
        cutscene_sleep(30)
        cutscene_func(instance_destroy, [o_ui_dialogue])
        cutscene_enc_wait(false)
    })
}
item_register(item_s_berto_zap)
```

How it works, line by line:

- `use_type = ITEM_USE.ENEMY` makes the battle ask which enemy to target. The target
  arrives as `target` (the enemy's slot).
- `use` receives the caster's registration name, `spell_user`.
- `cutscene_enc_wait(true)` ... `cutscene_enc_wait(false)` pause the battle's own
  flow while the spell plays, as in `item_s_iceshock`.
- `cutscene_dialogue(...)` shows "* Berto cast ZAP!" (`"item_spell_cast"` is an existing
  translated template).
- `enc_hurt_enemy(target, dmg, user)` deals the damage and handles the enemy's reaction.
  Here the damage grows with the caster's **magic**, which is why Step 2's `magic: 2`
  matters.
- `cutscene_func(instance_destroy, [o_ui_dialogue])` closes the dialogue box, as
  `item_s_iceshock` does.

!!! info "More effects"
    A real spell would also play a sound (`cutscene_audio_play`) and spawn an effect
    object (`cutscene_instance_create`), as `item_s_iceshock` does with `o_eff_iceshock`.
    This one has none, to keep the example short. The cutscene functions are in the
    [Cutscenes](../overworld/cutscenes.md) chapter.

Give it to Berto in `party_m_berto`:

```gml
spells = [
    new item_s_berto_zap(),
]
```

**Test:** wipe the save, add Berto, and start a fight (++tab++ + ++e++). Fill the TP bar
with ++tab++ + ++t++, open Berto's magic menu, cast **Zap** on an enemy, and watch the
damage.

---

## Common problems

| Symptom | Likely cause |
|---|---|
| The stats do not change after editing | An old save is loading the old data; wipe it (the warning at the top) |
| The game fails at startup with an unknown constructor | The script holding `item_w_berto_staff`, `item_a_berto_charm` or `item_s_berto_zap` is missing or misspelled in `party_m_berto` |
| He cannot equip his own weapon | `weapon_whitelist` does not contain the exact registration name `"berto"` |
| Zap is greyed out | Not enough TP; fill it with ++tab++ + ++t++ |
| Zap does nothing | `use_type` is missing or `use` is not wrapped in `method(self, ...)` |
| The battle stays frozen after the spell | The final `cutscene_enc_wait(false)` is missing |

The last three rows come from reading the engine's own spells, not from breaking mine on
purpose. I read each step in the engine's code, but did not run a custom character
through all of it in GameMaker. If one does not behave as written, treat it as a bug
in this chapter.

## Next

[Light World and dialogue](light-world-and-dialogue.md): his Light World sprites, and
making him speak.
