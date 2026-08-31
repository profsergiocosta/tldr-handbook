# Rooms and collision

A tlDR room is a normal GameMaker room with a handful of conventions layered on top. This chapter covers the objects every room needs, how the layers are meant to be stacked, how walls work, and how to move the player between rooms.

## The two objects every room needs

Drop these into any new room and it will boot:

| Object | Why |
|---|---|
| **`o_dev_world`** | The controller. It calls `world_switch(world)` on creation, which sets `global.world` and converts party equipment accordingly. Without it, nothing initialises. |
| **`o_dev_playermarker`** | Where the party spawns. It creates the leader with `party_leader_create(...)` and then every other member behind them, and automatically points the camera at the leader. |

`o_dev_world` has one Variable Definition worth knowing: **`world`**, which is `WORLD_TYPE.DARK` by default. Set it to `WORLD_TYPE.LIGHT` for Light World rooms — party sprites and equipment switch accordingly (`scripts/party_scripts/party_scripts.gml:240`).

!!! danger "Do NOT place `o_camera` in your rooms"
    `o_camera` is a **persistent singleton** spawned globally by `o_world` at game startup (`objects/o_world/Other_2.gml:6`). Placing a manual instance of `o_camera` inside a room creates a second camera whose target is `noone` at `(0, 0)`, which steals `view_camera[0]` and **turns the entire screen pitch black**.

    Leave the camera to the engine — `o_dev_playermarker` automatically finds the global camera and binds it to your party leader.

!!! tip "Start from an example room"
    `room_ex_city`, `room_ex_church` and `room_ex_dforest` are the engine's own rooms and they are the real documentation. Duplicating one and gutting it is usually faster than building from an empty room.

## Layer layout

Rooms are organised by depth, and the engine's own rooms follow a consistent order. This is `room_ex_city`, top to bottom:

| Depth | Layer | Kind | Contents |
|---:|---|---|---|
| `-4000` | `t_foreground` | tiles | tiles drawn **over** the player — awnings, treetops, foreground clutter |
| `0` | `collisions` | instances | `o_block` and `o_block_diag` — the walls |
| `200` | `decor` | instances | props that do not block |
| `300` | `Instances` | instances | NPCs, triggers, the player marker, `o_dev_world` |
| `400` | `area` | folder | grouping only |
| `500` | `t_buildingstop` | tiles | |
| `600` | `t_buildings` | tiles | |
| `700` | `t_grounddecor` | tiles | |
| `800` | `t_roaddecor` | tiles | |
| `1000` | `t_road` | tiles | |
| `1200` | `Background` | background | flat colour behind everything |

Remember: **in GameMaker, a larger depth is further back.** The foreground tile layer is at `-4000` precisely so it draws in front of the party.

You do not have to match this exactly, but keeping collisions at `0` and instances around `300` means you can copy code and creation snippets between rooms without surprises.

## Walls

Collision is instance-based, not tile-based. Two objects do the work:

| Object | Shape |
|---|---|
| **`o_block`** | Axis-aligned rectangles. The workhorse. |
| **`o_block_diag`** | Diagonals — slopes the player slides along. |

Place them on the `collisions` layer, stretch them over whatever should be solid, and that is it. They are invisible at runtime.

### The `collide` flag

`o_block` has exactly one variable, set in its Create event:

```gml
// objects/o_block/Create_0.gml
collide = true
```

The player's movement code checks it on every instance it touches (`objects/o_actor/Step_0.gml:180`), which means **you can turn a wall off at runtime**:

```gml
// a door that opens
with (my_door_block)
    collide = false;
```

This is much simpler than destroying and recreating instances, and it keeps the wall in the room editor where you can see it.

### How movement resolves collisions

Worth knowing, because it explains some behaviour that otherwise looks like a bug. The player moves in sub-pixel steps and tests each axis independently (`objects/o_actor/Step_0.gml:176` and `:194`). Horizontal first, then vertical. That is why you slide along a wall instead of sticking to it when you push into it diagonally.

Diagonal blocks get a second pass (`:229`) that also checks whether a regular `o_block` is interfering, so a diagonal that meets a straight wall behaves sensibly at the join.

!!! warning "Blocks are not for the battle arena"
    The soul inside a battle collides with `o_enc_box_solid`, not `o_block`. They are separate systems — see [The arena](../battle-system/the-arena.md).

## Moving between rooms

### The simple way

Anywhere you can run code:

```gml
room_goto(room_my_next_area);
```

Fine for prototyping, but the party will spawn at that room's `o_dev_playermarker`, which is rarely where you want them to arrive.

### The proper way: warp triggers

Use **`o_trigger_warp`**. It fades out, changes room, and then places the leader at a **landing marker** with a chosen facing direction (`objects/o_trigger_warp/Alarm_0.gml`):

```gml
party_leader_warp(MARKER_LAND, target_marker, exit_direction ?? savedir);
```

So the recipe for a doorway is:

1. Put an **`o_dev_marker_land`** in the destination room where the player should appear, and give it an `m_id`.
2. Put an **`o_trigger_warp`** in the source room over the doorway.
3. Fill in its Variable Definitions: the target room, the target marker's `m_id`, and the facing direction on arrival.
4. Stretch it (see below).

`MARKER_LAND` is just the string `"land"` (`scripts/macro_markers/macro_markers.gml:4`) — markers are grouped by kind, and landing spots are one kind.

## Triggers

`o_trigger` runs your code when the player walks into it. It is the general-purpose "something happens here" object. Put the code in the instance's **Instance Creation Code**:

```gml
trigger_code = function() {
    cutscene_create();
    cutscene_dialogue("* (The floor creaks.)");
    cutscene_play();
}

trigger_exit_code = function() {
    triggered = false;      // re-arm when the player leaves
}
```

Three things about triggers cause almost all the confusion, and none of them are about the code.

### 1. Stretch the instance

`spr_trigger` is **20×20 pixels** with its origin at the top-left corner, and `o_trigger` is invisible at runtime. A default-sized trigger is a tiny invisible square the player walks straight past.

The engine's own triggers are all stretched. In `room_ex_church`:

| Instance | scaleX | scaleY | Actual size |
|---|---|---|---|
| `inst_64FAB75A` | 7.0 | 2.0 | 140 × 40 |
| `inst_2B13ACD5` | 7.0 | 2.0 | 140 × 40 |
| `inst_2838B310` | 5.0 | 2.0 | 100 × 40 |

Drag the instance handles in the room editor until it covers the whole passage.

### 2. `o_trigger` fires once

The entry event sets `triggered = true` and **nothing in the engine sets it back**. The exit event only touches `trigger_exit` (`objects/o_trigger/Other_11.gml`). If you want it to fire again, reset it yourself in `trigger_exit_code`, as in the snippet above — this is the engine's own idiom (`rooms/room_ex_church/InstanceCreationCode_inst_2B13ACD5.gml:13`).

One-shot is often what you want, though. A trigger that starts a boss fight should not restart it when the player walks back.

### 3. The player must be in control

With `controlled_activation = true` (the default), the trigger only fires when `get_leader()._checkmove()` is true (`objects/o_trigger/Step_0.gml:4`). That function requires `moveable_console`, `moveable_dialogue`, `moveable_battle` and several others to all be true (`objects/o_actor/Create_0.gml:197`).

In practice: **with the console open (++tab++), no trigger fires.** If you want a trigger that works regardless — room edges, for instance — set `controlled_activation = false` in the Creation Code.

!!! tip "30-second diagnosis"
    Put `show_debug_message(">>> TRIGGER FIRED")` as the first line of `trigger_code`. If it never prints in the Output window while you walk over it, the problem is collision (1) or control (3), not your code.

## Common problems

| Symptom | Cause |
|---|---|
| The room is black and nothing responds | no `o_dev_world` in the room |
| The screen is pitch black even with `o_dev_world` | you placed an `o_camera` in the room — delete it (`o_camera` is a global singleton) |
| The party never appears | no `o_dev_playermarker` |
| The player walks through a wall | the `o_block` is on a layer the player does not collide with, or `collide` was set to `false` |
| A trigger never fires | the instance is still 20×20 — stretch it |
| A trigger fires once and never again | expected; reset `triggered` in `trigger_exit_code` |
| No trigger fires while you are testing | the console is open |
| Foreground tiles draw behind the player | depth is positive; foreground needs a negative depth |
| Warping lands the party in the wrong spot | the destination has no `o_dev_marker_land` with the `m_id` you referenced |
