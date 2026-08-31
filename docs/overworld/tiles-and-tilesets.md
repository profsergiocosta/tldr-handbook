# Tiles and tilesets

Tiles are plain GameMaker tiles — the engine adds no custom tile system. What it does add is a set of conventions about how many layers you use and what depth each one sits at, and those conventions are worth following because collision, depth sorting and the foreground effect all assume them.

## The grid

Every tileset in the project uses **20 × 20 pixel** tiles:

| Tileset | Used by |
|---|---|
| `tile_ex_ow_city`, `_edges`, `_path`, `_road`, `_street` | the city example |
| `tile_ex_church`, `_library`, `_secondary` | the church example |
| `tile_ex_dforest`, `_battle` | the dark forest example |
| `tile_ow_battle` | battle backdrops |
| `tile_dev_climb` | the climbing sections |

20×20 is not arbitrary: the game view is 320 × 240, so a screen is exactly 16 × 12 tiles. Designing rooms in multiples of a screen keeps camera transitions clean.

!!! note "Art is drawn at 2×"
    The engine's source art is twice the display size and drawn at `0.5` scale. You will see `draw_sprite_ext(..., .5, .5, ...)` throughout the codebase for this reason. When you author a new tileset, match the existing ones rather than the on-screen pixel size.

## Layer conventions

`room_ex_city` is the reference layout. Tile layers are interleaved with instance layers by depth:

```text
-4000   t_foreground     tiles ── drawn OVER the player
    0   collisions       instances (o_block, o_block_diag)
  200   decor            instances
  300   Instances        instances (NPCs, triggers, markers, o_dev_world)
  400   area             folder
  500   t_buildingstop   tiles
  600   t_buildings      tiles
  700   t_grounddecor    tiles
  800   t_roaddecor      tiles
 1000   t_road           tiles
 1200   Background       background colour
```

The naming is a convention too: tile layers are prefixed `t_`, which makes them easy to pick out in the layer panel once a room has fifteen of them.

### Reading that table

**Larger depth is further back.** The background is at `1200`, the road at `1000`, buildings in front of that, and the foreground at `-4000` so it covers everything including the party.

**Collisions sit at depth 0**, between the foreground and the props. The depth of that layer does not affect collision — `o_block` is found by object, not by layer — but keeping it at 0 in every room means you can copy instances between rooms without them jumping in front of your buildings.

**Instances at 300** put NPCs and triggers behind the building tops but in front of the ground, which is what you want for a top-down scene.

## Building a room

A practical order that avoids rework:

1. **Background layer** — a flat colour close to your final palette. It shows through every gap you have not filled yet, so a sensible colour makes the room readable while you work.
2. **Ground tiles** (`t_road`, `t_grounddecor`) — the walkable surface.
3. **Structures** (`t_buildings`, `t_buildingstop`) — split into two layers so the tops of buildings can overlap the bottoms of the ones behind.
4. **Collisions** — only now. Stretch `o_block` over everything solid. Do this after the art so you can see what you are blocking.
5. **Instances** — NPCs, signs, triggers, `o_dev_world`, `o_dev_playermarker`, `o_camera`.
6. **Foreground** (`t_foreground`) — awnings, treetops, anything the player should walk behind.

!!! tip "Collision does not follow tiles"
    Painting a wall tile does not create a wall. Every solid surface needs an `o_block` instance over it. This feels redundant at first and pays off immediately: you can make a wall passable at runtime by flipping `collide` on one instance, without touching the art.

## Depth-sorted props

For an object that the player should walk both in front of and behind — a lamp post, a pillar, a bush — do not use a tile. Use an object parented to **`o_ow_depthobj`**, which the engine sorts by its `y` position. `o_ow_interactable` already inherits from it, so any sign or NPC is depth-sorted for free.

`o_ow_depthobj` also carries a couple of extras you may want:

```gml
shake = 0                 // offset for shake effects
can_reflect = false       // whether the object draws a mirrored reflection
reflection_code = ...     // how it draws that reflection
s_lightalpha = 0          // lighting integration
```

## Parallax

`o_ow_parallax` moves a layer against the camera to fake distance. Useful for skylines and far backgrounds. `o_ex_infinity_parallaxer` in the examples shows a looping variant.

Parallax is a background layer job, not a tile layer job — put it behind everything, at a depth greater than your furthest tile layer.

## Common problems

| Symptom | Cause |
|---|---|
| The player walks over a building | the tile layer's depth is greater than the player's; buildings belong above `400` in the table, foreground below `0` |
| Foreground tiles draw behind the player | the layer has a positive depth — foreground needs a negative one |
| The player walks through a painted wall | tiles are not solid; add `o_block` |
| Tiles have hairline gaps when the camera moves | the camera is at a fractional position, or the room size is not a multiple of the tile size |
| A prop always draws in front of the player | it is not parented to `o_ow_depthobj` |
| A new tileset looks blurry or doubled | authored at 1× instead of 2× — match the existing tilesets |
