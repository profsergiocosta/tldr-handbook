# Light World and dialogue

Berto walks, fights and has his own numbers. Two things are still missing before he can
be a character in a story: how he looks in the **Light World**, and a **face and voice**
for his dialogue. They are independent, so you can do either first.

---

## Part 1 — The Light World

### How the engine picks the Light World sprite

In a Light World room the engine adds `_light` to the end of every sprite name it looks for
(`party_m_get_cardinal` in `scripts/party_scripts/party_scripts.gml`). For Berto:

| Dark World | Light World |
|---|---|
| `spr_berto_down` | `spr_berto_down_light` |
| `spr_berto_up` | `spr_berto_up_light` |
| `spr_berto_left` | `spr_berto_left_light` |
| `spr_berto_right` | `spr_berto_right_light` |

Per the comment on `asset_get_index_state` (`scripts/custom/custom.gml`), if the `_light`
sprite **does not exist, the normal sprite is used instead**. So nothing breaks if you skip
this part: Berto simply looks the same in both worlds.

If you do draw them, follow the same rules as in
[Character sprites](sprites.md): 4 frames, origin at the feet, Fps 4. The engine's own
Light World sprites follow the same naming (`spr_kris_down_light`,
`spr_noelle_down_light`, ...).

### Step 1 — Draw and name the four sprites

Create `spr_berto_down_light`, `spr_berto_up_light`, `spr_berto_left_light` and
`spr_berto_right_light`. Light World characters are usually drawn smaller and plainer
(the engine's are the school-day versions of the characters).

### Step 2 — A Light World test room

1. Duplicate `room_test_characters` (right-click the room → *Duplicate*) and name the copy
   `room_test_light`.
2. Select the **`o_dev_world`** instance in it, and in the **Inspector** open its
   *Variable Definitions*. Set **`world`** to **`WORLD_TYPE.LIGHT`**
   ([Party and the Light World](../systems/party-and-light-world.md) has the details).
3. Run, go to the room with ++tab++ + ++r++, add Berto with ++tab++ + ++p++, and walk.

Berto should use his `_light` sprites, and the pause menu (++c++) is the Light World one.

### Equipment in the Light World

When the **leader** enters the Light World, the engine converts their weapon and armour
to their `lw_counterpart`. An item whose `lw_counterpart` is `undefined` (the default) has
no Light World version, and per the engine's comment on that field "nothing appears in the
light world" for it (`scripts/item/item.gml`).

This only matters if Berto is the leader (see the next chapter). When he is, give his
items a counterpart, for example the engine's `item_w_lw_pencil`:

```gml
// inside item_w_berto_staff in your rpg_items script
lw_counterpart = item_w_lw_pencil
```

`lw_counterpart` is a **script reference**, not a string: write `item_w_lw_pencil`, not
`"item_w_lw_pencil"`.

---

## Part 2 — Face and voice

Dialogue text can name a speaking character: `{char(susie, 14)}* Hey, Kris.` The
engine looks `susie` up in a registry of **typer characters**, which supplies the face
portrait and the voice blips. To make `{char(berto, 1)}` work, Berto needs an entry.

### What the engine's own look like

```gml
// scripts/typer_chars/typer_chars.gml
function typer_char_noelle() : typer_char() constructor {
    name = "noelle"

    face_sprite = spr_face_noelle
    voice = snd_text_noelle
}
```

`typer_char` (the base) has more fields you can set: `font`, `voice_pitch_calc`,
`voice_interrupt` and `voice_skip`. The engine's example `ex_typer_gerson`
(`scripts/ex_typer_chars/`) uses a custom voice that plays every third frame at a random pitch.

### Step 3 — The face sprite

Create **`spr_face_berto`**. It is a single sprite whose **frames are expressions**:
frame 0 is the default face, frame 1 the next expression, and so on. The engine's are about
54 × 62 with the origin in the **centre** (Noelle's: 54 × 62, 51 frames, origin 27, 31).
Frame numbers are what you write in `{char(berto, N)}`.

You can start with two or three expressions and add more later.

### Step 4 — The typer character

In **your own script** (for example `rpg_party`), add:

```gml
function typer_char_berto() : typer_char() constructor {
    name = "berto"                // the name used in {char(berto, 0)}

    face_sprite = spr_face_berto
    voice = snd_text              // the engine's default blip; change it later
}
```

`name` is what you type in the dialogue tag, and it does not have to match the party
registration name, although it is simpler if it does.

A custom voice is a sound asset: import a short blip as a sound, and put it in `voice`
instead of `snd_text`. The engine's voices are `snd_text_susie`, `snd_text_ralsei` and
`snd_text_noelle`.

### Step 5 — Register it

Open **`o_world`**'s **Game Start** event (see
[Your first party member](first-party-member.md#step-3-register-him) for how to get there).
Near the end it initialises the typer characters; add yours under the engine's example:

```gml
typer_chars_init()

new ex_typer_gerson().__initialize()
new typer_char_berto().__initialize()      // <-- yours
// << initialize your typer chars here
```

`__initialize` adds the character to the registry (`global.typer_chars`).

### Step 6 — Test with a sign

In `room_test_characters`, place an **`o_ow_sign`**. In its Instance Creation Code:

```gml
text = [
    "{char(berto, 0)}* Hi! I'm Berto.",
    "{char(berto, 1)}* Nice to meet you!"
]
```

Run, walk up to the sign and interact with it as with any sign. You should see Berto's
face, expression 0 and then expression 1, with his voice (the default blip for now).

---

## Common problems

| Symptom | Likely cause |
|---|---|
| Berto looks the same in the Light World | The `_light` sprites do not exist or are misspelled (this is the fallback, not an error), or the room's `world` variable is not `WORLD_TYPE.LIGHT` |
| The text shows but there is no face | `face_sprite` is not set, the sprite is missing, or the `{char(...)}` name does not match `name` |
| The game fails when the text starts | The name in `{char(...)}` was never registered with `__initialize()` in `o_world` |
| An expression number shows the wrong face | Frames start at 0: frame 0 is the first drawing |
| An item vanishes in the Light World | Its `lw_counterpart` is `undefined` |

I read these steps in the engine's code, but did not run a new character through all of
them in GameMaker. If one does not behave as written, treat it as a bug in this chapter.

## Next

[Joining and leaving the party](joining-the-party.md): making Berto join the party in a
scene, and leave it.
