# Your first room

From an empty canvas to a living overworld area, in eight steps. Every step ends with something you can **run and walk through**, bringing together collision, signs, an NPC with memory, a glowing prophecy mural with atmospheric lighting, and a doorway to the next area.

If you have read [Rooms and collision](rooms-and-collision.md), [NPCs and dialogue](npcs-and-dialogue.md), and [Tiles and tilesets](tiles-and-tilesets.md), this chapter puts those pieces into one complete, playable room.

---

## What we are building

A quiet sanctuary called **`room_sanctuary`**.

The party arrives at the bottom of the room. On the left sits an introductory sign; in the middle, a friendly NPC greets the player and remembers if they speak again. Walking toward the altar at the top of the room triggers an atmospheric shift: the room dims with warm golden light, the camera frames the shrine, and a glowing prophecy mural materializes above the wall. Finally, an archway on the right leads to the next area.

| Area element | Object | What it demonstrates |
|---|---|---|
| The Controller | `o_dev_world` | World initialization and dark/light mode switch |
| The Party Spawn | `o_dev_playermarker` | Party follower formation and camera attachment |
| The Walls | `o_block` | Sub-pixel collision and diagonal sliding |
| The Sign | `o_ow_sign` | Simple dialogue with color formatting |
| The Guide NPC | `o_ow_npc` | Cutscenes, portraits, and memory flags |
| The Prophecy Mural | `o_ow_prophecy` | Surface shaders, animated auras, floating text |
| The Altar Trigger | `o_trigger` | Ambient lighting (`lighting_on`) and camera panning |
| The Exit Door | `o_trigger_warp` | Room transition with landing marker |

---

## Step 0 — Create the room and layer stack

1. In the **Asset Browser**, right-click your rooms folder → **Create → Room**. Name it **`room_sanctuary`**.
2. In the Room Settings inspector, set the room dimensions: **Width: `640`**, **Height: `480`** (exactly 2×2 default game screens).
3. Set the grid to **20 × 20 pixels** (Snap: `20` X, `20` Y).

### Set up the layer hierarchy

Organize your layers by depth in the Room Editor's layer panel. Follow the engine's canonical depth convention:

```text
Layer Name          Type        Depth      Contents
─────────────────────────────────────────────────────────────────────────────
t_foreground        Tiles       -4000      Awnings, pillars, canopy over player
collisions          Instances       0      o_block (invisible solid walls)
decor               Instances     200      Props that do not block
Instances           Instances     300      Controllers, player, NPCs, signs, triggers
t_buildingstop      Tiles         500      Top of walls and roofs
t_buildings         Tiles         600      Walls and vertical structures
t_grounddecor       Tiles         700      Carpets, weeds, decorative tiles
t_ground            Tiles        1000      Walkable floor tiles
Background          Background   1200      Solid background color (#161224)
```

!!! tip "Why depth order matters"
    Remember: **larger numbers are further back**. Placing `t_foreground` at `-4000` ensures it draws over the party and NPCs, while `Instances` at `300` ensures characters walk in front of the floor (`1000`) but behind the tops of walls (`500`).

---

## Step 1 — The two essential objects

Switch to the **`Instances`** layer (depth `300`) and place these two objects:

1. **`o_dev_world`**: Drop it anywhere in the room (e.g. at `(20, 20)`).
   - In its **Variables** panel, ensure `world` is set to `WORLD_TYPE.DARK` (or `WORLD_TYPE.LIGHT` if your room is in the Light World).
2. **`o_dev_playermarker`**: Place it at `(320, 380)` where the party should spawn.

!!! danger "Do NOT place `o_camera` in your room"
    In the tlDR Engine, `o_camera` is a **persistent global singleton** created automatically on game start (`objects/o_world/Other_2.gml:6`). Placing a manual `o_camera` inside a room creates a duplicate instance with `target = noone` at `(0, 0)` that steals the view and **turns the screen completely black**.

    Leave camera tracking to `o_dev_playermarker`, which automatically finds the global camera and binds it to the party leader on creation.

### Test now

Press **Run** (++f5++). Open the console with ++tab++, type `room_select`, and pick `room_sanctuary`.

You should see Kris (and your party members) standing in the middle of a blank room, able to walk in four directions with smooth camera follow.

---

## Step 2 — Laying the floor and solid walls

### 2.1 Draw the floor
Select the **`t_ground`** layer (depth `1000`), open your tileset (e.g., `tile_ex_church` or `tile_ex_ow_city`), and paint a central hall roughly 20 tiles wide and 16 tiles high.

### 2.2 Place collision blocks
Switch to the **`collisions`** layer (depth `0`):

1. Drag **`o_block`** from the Asset Browser to the room.
2. Stretch the instances along the top, left, right, and bottom boundaries of the walkable hall.
3. If your room has diagonal corners, place **`o_block_diag`** and rotate or flip them to match the slope.

```text
    ┌──────────────────[ o_block ]──────────────────┐
    │                                               │
[ o_block ]         (Walkable Area)             [ o_block ]
    │                                               │
    └──────────────────[ o_block ]──────────────────┘
```

**Test:** Run the game. Walk directly into the walls and push diagonally against them. The party should slide along the edges without getting stuck or clipping outside.

---

## Step 3 — A readable sign

Place a sign near the entrance so the player has something to inspect.

1. Select the **`Instances`** layer (depth `300`).
2. Drag **`o_ow_sign`** into the room at `(220, 360)`.
3. Open its **Instance Creation Code** and enter:

```gml
text = "{col(y)}* Sanctuary of the Ancients.{br}{resetx}* Seekers of the prophecy may proceed north.{col(w)}{p}{e}"
```

### How the markup works:
- `{col(y)}` sets the text to yellow.
- `{br}{resetx}` moves to the next line at the left margin.
- `{col(w)}` restores white text.
- `{p}` pauses until the player presses the confirm key.
- `{e}` cleanly ends the dialogue box.

**Test:** Approach the sign from below, face it, and press confirm (++z++ / ++enter++). The text typer opens, renders the text, and closes on confirm.

---

## Step 4 — A guide NPC with memory and portrait

Let us add a friendly guide NPC who gives directions and remembers when you speak to them again.

1. On the **`Instances`** layer, drag an **`o_ow_npc`** into the room at `(400, 320)`.
2. In its inspector properties, set **Sprite** to `spr_ralsei_d` (or any NPC sprite of your choice).
3. Open its **Instance Creation Code** and paste:

```gml
interaction_code = function() {
    cutscene_create()

    if memory_get("sanctuary", "guide_met") {
        cutscene_dialogue("{char(ralsei, 2)}* The prophecy is just ahead of you, Kris.{p}{e}")
    } else {
        cutscene_dialogue(
            "{char(ralsei, 0)}* Welcome to the inner sanctuary!{br}{resetx}"
          + "* Walk up to the altar to view the sacred mural.{p}{e}"
        )
        cutscene_func(memory_set, ["sanctuary", "guide_met", true])
    }

    cutscene_play()
}
```

### Why this works:
- `memory_get(category, key)` checks a persistent flag.
- `cutscene_func(memory_set, ["sanctuary", "guide_met", true])` queues the flag update inside the cutscene sequence so it only sets once the line finishes.
- `{char(name, expression)}` loads the character's portrait and facial expression in the text box.

**Test:** Talk to the NPC. On the first interaction, they give the welcome speech. Talk to them a second time, and they give the shorter follow-up line.

---

## Step 5 — The prophecy mural

Now we create the visual centerpiece: an ancient mural embedded into the north wall.

1. On the **`Instances`** layer, drag an **`o_ow_prophecy`** to the top center wall at `(320, 160)`.
2. In the instance's **Variables** panel (or Creation Code), set:
   - `prophecy_text`:
     ```text
     THREE HEROES APPEAR AT WORLDS' END.\nTO SEAL THE FOUNTAINS AND ASCEND.
     ```
   - `sprite_index`: `spr_ow_prophecy_heroes` (or `spr_ex_ow_prophecy_main2`).

!!! info "Why the mural is invisible right now"
    If you run the game immediately, the prophecy will appear invisible or black. That is expected! In `o_ow_prophecy/Step_0.gml`, the object sets its `image_alpha` equal to `o_eff_lighting_controller.lighting_alpha`. In normal room lighting, `lighting_alpha` is `0`. It only fades into view when the room's lighting is turned on.

---

## Step 6 — The atmospheric altar trigger

To reveal the mural, place an `o_trigger` on the floor in front of the altar that activates the lighting and pans the camera when the party approaches.

1. On the **`Instances`** layer, drag an **`o_trigger`** at `(250, 180)` (just below the mural).
2. **Stretch the trigger** across the entire walkway (e.g. set `scaleX = 7.0` and `scaleY = 2.0` in the inspector, making it 140 × 40 px).
3. Open the trigger's **Instance Creation Code** and paste:

```gml
trigger_code = function() {
    // Lock vertical camera follow and pan up to frame the mural
    o_camera.follow_y = false
    camera_pan(undefined, y - 34, 40, "sine_out", true)

    // Turn on the mystic golden lighting
    lighting_on(0xFFD042, 0xFF392A)
}

trigger_exit_code = function() {
    // Turn off lighting (smooth automatic fade out)
    lighting_off()

    // Restore camera tracking to the party leader
    o_camera.follow_y = true
    camera_unpan(get_leader(), 40, "cubic_out")

    // Allow re-activation when the player steps back in
    triggered = false
}
```

### The result:
- When the player steps into the trigger area:
  1. `lighting_on(0xFFD042, 0xFF392A)` ramps up `lighting_alpha` from 0 to 1.
  2. The room darkens into a golden glow, and the mural smoothly fades in with a shimmering animated aura and glowing text.
  3. The camera pans upward to frame the full artwork.
- When the player steps backward out of the trigger:
  1. `lighting_off()` fades `lighting_alpha` back to 0 (mural vanishes).
  2. `camera_unpan()` returns focus to the leader.
  3. `triggered = false` re-arms the trigger for future visits.

**Test:** Walk up to the mural. Watch the room dim, the camera tilt, and the text shimmer into view. Step backward and watch the sanctuary return to normal.

---

## Step 7 — The doorway to the next area

Finally, let us add a doorway on the right wall that transports the party to another room (such as `room_ex_city`).

1. Place an **`o_trigger_warp`** at `(580, 240)` over the right corridor exit.
2. Stretch it vertically (`scaleX = 1.0`, `scaleY = 3.0`).
3. In its **Variables** panel, configure:
   - `target_room`: `room_ex_city` (or any other room asset in your project).
   - `target_marker`: `"entrance"` (the `m_id` of the landing marker in that room).
   - `exit_direction`: `DIR.RIGHT`.

!!! note "The destination landing spot"
    Make sure the destination room has an **`o_dev_marker_land`** instance with its variable `m_id = "entrance"`. When warping, the engine finds that marker and places the party directly on it.

---

## Testing checklist

Play through your new room and verify each interaction:

- [ ] **Spawning:** The party spawns at `o_dev_playermarker` and follows in a line.
- [ ] **Collision:** You cannot walk through `o_block` walls; diagonal movement slides cleanly.
- [ ] **Sign:** Facing `o_ow_sign` and pressing confirm displays the formatted text box.
- [ ] **NPC Memory:** The NPC gives the initial speech first, and switches to the short dialogue on repeated visits.
- [ ] **Prophecy & Lighting:** Walking into the altar area smoothly dims the room into golden light, frames the camera, and renders the shimmering mural text.
- [ ] **Exit Transition:** Walking into `o_trigger_warp` fades the screen and warps cleanly to the destination room.

---

## Common problems

| Symptom | Cause |
|---|---|
| The room is pitch black and input does not respond | Missing `o_dev_world` on the `Instances` layer |
| The screen is pitch black even with `o_dev_world` | You placed `o_camera` in the room — delete it (`o_camera` is a global singleton) |
| The party never appears | Missing `o_dev_playermarker` |
| The player walks through the wall | `o_block` is on an inactive layer, or its `collide` variable was set to `false` |
| The trigger never activates | The trigger is still 20×20 px — select it and stretch its `scaleX` and `scaleY` |
| The trigger fires once and never again | Missing `triggered = false` inside `trigger_exit_code` |
| The prophecy mural is always black/invisible | The trigger did not call `lighting_on()` or `o_eff_lighting_controller` was disabled |
| The NPC does not turn or speak | The instance is not parented to `o_ow_npc` or `o_ow_interactable` |
| Warping lands the player at the origin `(0, 0)` | The target room is missing an `o_dev_marker_land` with matching `m_id` |

---

## What next?

Now that your overworld room is built and connected, head into **Part 3** to build your battle system:

- [How a fight works](../battle-system/overview.md) — The core concepts behind DELTARUNE-style combat.
- [Your first enemy](../battle-system/your-first-enemy.md) — Build a complete, custom creature from scratch.
