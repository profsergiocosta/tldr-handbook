# Hazards, chases, and dodging

Overworld gameplay in DELTARUNE is dynamic and hazardous: enemies roam along patrol paths, spot the party with an exclamation mark, and chase you down. Furthermore, certain areas switch into a **real-time bullet-dodging mode** directly on the map — dodging speeding cars in Cyber City or dancing shadows in the Forest without opening the turn-based battle screen.

tlDR Engine implements both systems:
1. **Enemy Overworld Actors** (`o_actor_e`, `o_trigger_enemy_chase`) — patrol paths, line-of-sight chasing, and battle initialization.
2. **Overworld Dodging System** (`scripts/dodge/dodge.gml`, `o_trigger_dodge`, `o_dodge_controller`) — real-time red SOUL control, ambient bullet collision, and map darken shaders.

This chapter explains both systems, followed by a hands-on tutorial to set up an enemy patrol and a real-time hazard street crossing.

---

## How overworld enemies and dodging work

```mermaid
graph LR
    A["Patrol: o_actor_e on Path"] -->|Player enters chase_dist| B["Alert: snd_exclamation"]
    B -->|Chase Player| C["Contact: enc_start()"]
    D["Step into o_trigger_dodge"] -->|dodge_on()| E["Red SOUL appears on Map"]
    E -->|Dodge o_dodge_bullet| F["Real-time Graze & Damage"]
```

1. **Enemy roaming:** An `o_actor_e` instance moves back and forth along a predefined Path. If the party leader enters `chase_dist` (or enters an `o_trigger_enemy_chase`), the enemy alerts with `snd_exclamation` and sprints toward Kris. Touching the enemy starts the battle encounter (`enc_start`).
2. **Real-time dodging:** Stepping into an `o_trigger_dodge` activates `dodge_on()`. Kris's red SOUL (`o_dodge_soul`) appears on the map, background elements dim (`dodge_darken_self()`), and hazards parented to `o_dodge_bullet` damage party HP directly in real-time.

---

## Tutorial: Your first hazard and chase in 5 steps

Let's build a hazardous hallway with two connected challenges:
1. A roaming enemy patrolling back and forth along a hallway that chases the player when spotted.
2. A street crossing where stepping onto the asphalt spawns the red SOUL to dodge oncoming hazards.

---

### Step 0 — Create the patrol path asset

1. In the GameMaker **Asset Browser**, right-click `Paths` $ightarrow$ **Create** $ightarrow$ **Path**.
2. Name it **`path_corridor_patrol`**.
3. In the Path Editor:
   - Click to add Point 0 at `(0, 0)`.
   - Click to add Point 1 at `(180, 0)`.
   - Set **Connection** to `Straight Lines` and **Closed** to `Reverse` (or `Closed`).
   - Precision: `1`.

This creates a 180-pixel horizontal patrol line.

---

### Step 1 — Place the roaming enemy (`o_actor_e`)

1. Open your room in the Room Editor and select the **`Instances`** layer (depth `300`).
2. Drag an instance of **`o_actor_e`** (or `o_actor_e_killercar`) into your hallway.
3. In the Inspector, open its **Variable Definitions**:

| Variable | Value | Explanation |
|---|---|---|
| **`idle_path`** | `path_corridor_patrol` | The path created in Step 0. |
| **`idle_path_spd`** | `2` | Pacing speed. |
| **`chase_dist`** | `60` | Detection radius in pixels. |
| **`chase_spd`** | `4` | Sprint speed when chasing Kris. |
| **`encounter`** | `new enc_set_ex()` | The encounter struct triggered on contact. |

When the room boots, the enemy walks back and forth along the path. If Kris walks within 60px, it alerts with an exclamation mark and chases Kris until touching or losing sight.

---

### Step 2 — Place the dodge zone (`o_trigger_dodge`)

1. In the next section of the hallway (e.g. a road or obstacle floor), select the **`Instances`** layer.
2. Drag an instance of **`o_trigger_dodge`** onto the floor.
3. Stretch its bounding box (`scaleX` and `scaleY`) to cover the entire hazardous floor.

`o_trigger_dodge` handles all state management automatically (`objects/o_trigger_dodge/Create_0.gml`):
- **Entering:** Calls `dodge_on()` $ightarrow$ Spawns `o_dodge_soul` over Kris and enables real-time damage.
- **Exiting:** Calls `dodge_off()` $ightarrow$ Destroys `o_dodge_soul` and restores normal overworld control.

---

### Step 3 — Create an overworld hazard bullet (`o_hazard_car`)

Let's make a simple moving obstacle that crosses the road and damages the red SOUL:

1. In the Asset Browser, create an Object named **`o_hazard_car`**.
2. Set its **Parent** to **`o_dodge_bullet`** (`objects/o_dodge_bullet/`).
3. Set its **Sprite** (e.g. `spr_ex_ow_city_car_left` or any hazard sprite).
4. Add a **Create Event**:
   ```gml
   event_inherited(); // Inherits collision and graze code
   spd = 5;
   dir = DIR.LEFT;
   ```
5. Add a **Step Event**:
   ```gml
   event_inherited();
   
   // Move horizontally across the road
   x -= spd;
   
   // Destroy when offscreen
   if x < -50
       instance_destroy();
   ```

---

### Step 4 — Place a hazard spawner in the room

1. In your room, place an `o_trigger` or simple controller at the right edge of the road.
2. In its **Instance Creation Code**, spawn cars periodically:

```gml
// Instance Creation Code of spawner
trigger_code = function() {
    // Spawns a hazard car moving left every 40 frames
    time_source = time_source_create(time_source_game, 40, time_source_units_frames, function() {
        if instance_exists(o_dodge_controller) && o_dodge_controller.dodge_mode {
            instance_create(o_hazard_car, x, y, depth, {});
        }
    }, [], -1);
    time_source_start(time_source);
};
```

---

### Step 5 — Test and verify checklist

Run your game (`F5`) and test both mechanics:

- [ ] The enemy paces smoothly back and forth along its path.
- [ ] Approaching the enemy triggers `snd_exclamation` and starts an active pursuit.
- [ ] Touching the enemy transitions cleanly into the turn-based battle encounter (`enc_set_ex`).
- [ ] Stepping into `o_trigger_dodge` summons Kris's red SOUL and dims the background.
- [ ] Touching an oncoming hazard car flashes the SOUL with invulnerability frames and reduces party HP.
- [ ] Passing very close to the car plays `snd_graze` and rewards TP.
- [ ] Stepping out of `o_trigger_dodge` smoothly removes the SOUL and brightens the screen.

---

## Darkening background props (`dodge_darken_self`)

To make trees, signs, and background buildings visually react to the overworld dodge mode (dimming when the battle zone activates, just like in Cyber City), call `dodge_darken_self()` in their **Draw Event**:

```gml
// Draw Event of your custom prop or sign
draw_self();
dodge_darken_self(); // Applies the overworld combat dark shader overlay
```

---

## Overworld Game Over (`dodge_gameover`)

If party HP reaches zero during overworld dodging, the engine executes `dodge_gameover()` (`scripts/dodge/dodge.gml:34`):

```gml
function dodge_gameover() {
    // 1. Captures application_surface as a frozen screenshot
    // 2. Plays snd_hurt and cuts all music
    // 3. Spawns the soul shatter particle effect
    // 4. Transitions directly to room_gameover
}
```

---

## Common problems

| Symptom | Cause |
|---|---|
| Enemy touches player but battle never starts | `encounter` field on `o_actor_e` is not initialized or invalid |
| Enemy does not chase when player approaches | `chase_dist` is too small, or the enemy is stuck inside an `o_block` collision |
| Red SOUL does not appear in hazard zone | Missing `o_trigger_dodge` or `o_dodge_controller` in the room |
| Dodging remains stuck on after leaving the area | `o_trigger_dodge` was deleted or did not execute `trigger_exit_code` |
| Overworld bullets do not deal damage | The bullet object was not parented to `o_dodge_bullet` |
