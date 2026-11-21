# Your first party member

In [Character sprites](sprites.md) you drew Berto and checked him with a plain
test object. That object just stands there. This chapter makes him a real **party
member**: the engine will know who he is, he can be added to and removed from the
party, and he will follow Kris around the room, walking with the sprites you drew.

A party member is three things that must agree with each other:

| Piece | What it is | Where it lives |
|---|---|---|
| The **actor object** | The thing that appears in the room and walks | `o_actor_berto` |
| The **data struct** | Name, colours, stats, sprite names | `party_m_berto`, a constructor |
| The **registration** | Tells the engine the struct exists, under a name | one line in `o_world` |

The name `"berto"` ties them together, so keep it exactly the same everywhere.

---

## Step 1 — The actor object

1. **Create → Object**, name it **`o_actor_berto`**.
2. Set its **Parent** to **`o_actor`**. (This is what makes it walk, follow the
   leader and collide.)
3. Set its **Sprite** to `spr_berto_down`, and its **Collision Mask** to
   `spr_berto_down` as well. The mask is why Step 1 of the previous chapter
   mattered: the engine's own actors do exactly this (for example
   `o_actor_noelle` uses `spr_noelle_down` for both).
4. In the **Create** event, add:

    ```gml
    // objects/o_actor_berto/Create_0.gml
    event_inherited()
    name = "berto"
    is_party = true
    ```

    This is the whole of `o_actor_noelle`'s Create event with the name changed
    (`objects/o_actor_noelle/Create_0.gml`). `name` must be the **registration
    name** from Step 3. The actor uses it to look its data up, which is how it finds
    your sprites.

---

## Step 2 — The data struct

Put your own constructors in your own script instead of the engine's
`party_init`, so that updating the engine does not collide with your work.

1. **Create → Script**, name it **`rpg_party`** (any name you like).
2. Write the constructor:

    ```gml
    // scripts/rpg_party/rpg_party.gml
    function party_m_berto(_initialized_name) : party_m(_initialized_name) constructor {
        name = "Berto"
        action_letter = "B"
        obj = o_actor_berto

        // colours (used by the menu, the battle UI and the light effects)
        color     = c_orange
        darkcolor = c_maroon
        iconcolor = #FFA040

        // stats
        max_hp  = 80
        hp      = max_hp
        attack  = 10
        defense = 2
        magic   = 1

        // sprites: the name the engine uses to build every sprite name
        s_name = "berto"
    }
    ```

What each part does:

- `: party_m(_initialized_name)` makes it a *child* of the base party member. Every
  field you do not write keeps the base value, which is how a constructor can be
  this short.
- `obj` is the actor object from Step 1.
- `s_name` is the `{name}` in `spr_{name}_down` and friends. It has to match the
  names of the sprites you made: `s_name = "berto"` finds `spr_berto_down`.
- `name` is the text shown to the player. For the engine's own characters it holds
  a localisation key (`"party_kris_name"`); `loc()` returns the text unchanged if
  no such key exists (`scripts/loc/loc.gml:68`), so a plain `"Berto"` works until
  you add translations.

!!! warning "Berto will fight like Susie, for now"
    Anything the base `party_m` provides and you do not override is **Susie's**:
    the battle sprites (`battle_sprites`), and the placeholder menu icons
    (`spr_ui_default_icon` and `spr_ui_default_head`) that every new character gets.
    So Berto works in a fight, but looks like Susie in it. Giving him his own
    battle sprites and icons is a later chapter.

---

## Step 3 — Register him

The engine only knows about party members that were registered with
`party_m_initialize(name, constructor)`
(`scripts/party_init/party_init.gml:12`). The engine registers its own four there:

```gml
function party_init() {
    party_m_initialize("kris", party_m_kris)
    party_m_initialize("susie", party_m_susie)
    party_m_initialize("ralsei", party_m_ralsei)
    party_m_initialize("noelle", party_m_noelle)

    global.party_names = []
}
```

Do not edit that function. Add one line in **`o_world`**, in the **Game Start** event
(`objects/o_world/Other_2.gml`), right after the call to `party_init()`:

```gml
party_init()
party_m_initialize("berto", party_m_berto)   // <-- yours
global.party_names = [   // <-- if you wish to change the default team members, change them here
    "kris", "susie", "ralsei"
]
party_apply_equipment()
```

Registering is not the same as being *in the party*. `global.party_names` is the
list of who is in the party right now, and Berto is not in it yet.

!!! tip "Keep your edits to `@Engine` to one line"
    `o_world` is part of the engine, so every line you change there can conflict
    when you [update the engine](../getting-started/installation.md#updating-the-engine).
    One registration line is easy to carry over; keep the rest in your own scripts.

---

## Step 4 — Test: add Berto to the party

Open `room_test_characters` from the previous chapter. First **delete the
`o_test_berto` instance** from the room, since the real Berto replaces it.

Run the game, go to the room, and use the console's **Party Select**: hold
++tab++ + ++p++. The list is built from every registered party member, so **Berto
appears in it** next to the engine's four. Move to him with the arrow keys and press
++enter++: the console prints that he was added to your party, and he appears behind
Kris. Press ++enter++ on him again to remove him.

Walk around. You should see:

- Berto **follows** Kris, a step behind, in the party line;
- he **animates while walking** and **stops on the first frame** when you stop;
- he turns with Kris, using your `up`, `down`, `left` and `right` sprites.

If you would rather have him in the party from the start, add `"berto"` to
`global.party_names` in the same `o_world` Game Start event.

---

## Common problems

| Symptom | Likely cause |
|---|---|
| Berto is not in Party Select | The registration line (Step 3) is missing, or its name does not match |
| Berto is a grey square | The sprite names do not match `s_name`; see *Naming scheme* in the previous chapter |
| He walks, but the animation is too fast or too slow | Change the sprite's **Fps** in the sprite editor (the engine's own use 4) |
| He floats above, or sinks into, the ground | The sprite origin is not at the feet |
| Walls stop him at the chest | The object's collision mask is not the manual box from `spr_berto_down` |
| The game stops at startup with an error about `party_m_berto` | The script with the constructor is missing, or the name is misspelled in `o_world` |

I have checked each step against the engine's source, but have not run a custom
character through it in GameMaker. If one of the table's causes does not match what
you see, treat it as a bug in this chapter.

## Next

The next chapter gives Berto his own **battle sprites**, so that he stops looking
like Susie in a fight.
