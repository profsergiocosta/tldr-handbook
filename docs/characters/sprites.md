# Character sprites

Before a new party member can exist, it needs a body. This chapter is about the
**overworld sprites** of a character of your own: how big they may be, where the
origin goes, how the collision mask works, and what the engine expects them to be
called. It ends with your character standing in a room, with its origin and
collision box drawn on top of it so you can check both by eye.

It does not make the character a *party member* yet. That is
the next chapter (*Your first party member*).

We will build a character called **Berto**. Use any name you like, but keep it
lowercase and without spaces, because it becomes part of every asset name.

---

## What you need to draw

The short answer: **4 sprites, each with 4 frames — 16 small drawings.**

| Sprite | Frames | What it is |
|---|---|---|
| `spr_berto_down` | 4 | walking animation, facing the camera |
| `spr_berto_up` | 4 | walking animation, facing away |
| `spr_berto_left` | 4 | walking animation, facing left |
| `spr_berto_right` | 4 | walking animation, facing right |

There is no separate "standing" sprite and no separate "walking" sprite at this
point: one walking animation per direction does both. When Berto is not moving the
engine stops the animation on frame 0, so **frame 0 should be the standing pose**.
(The base-game sprites all have 4 frames and the engine counts frames from the
sprite itself instead of fixing the number. It also stops the animation on even
frames, so I recommend keeping to an even number such as 4. I have not tested
other counts.)

That is the complete minimum for a character who can walk around. Everything in
Step 2 beyond these four sprites is an **optional extra**, and you can add it later
without touching what you already drew.

---

## Do all characters need the same size?

No. The engine's own party members are different sizes, on purpose:

| Sprite | Size | Origin (x, y) |
|---|---|---|
| `spr_kris_down` | 19 × 38 | 10, 37 |
| `spr_susie_down` | 26 × 43 | 13, 43 |
| `spr_ralsei_down` | 21 × 41 | 10, 40 |
| `spr_noelle_down` | 23 × 48 | 11, 46 |

Draw Berto as tall and as wide as the design needs. What has to be consistent is
not the size of the picture but two things the engine reads from it:

1. **The origin** — the point that is Berto's position. It goes at the **feet**.
2. **The collision mask** — the box used to bump into walls. It is a small box
   around the feet, *not* the whole body.

Both are explained below. Get these two right and any size works.

---

## Step 1 — The `down` sprite: size, origin and collision mask

`down` is the most important sprite, because the engine uses it as the character's
collision shape (more on that in a moment).

1. In the Asset Browser, **Create → Sprite**, name it **`spr_berto_down`**.
2. Import or draw four frames. The engine's walk sprites have **4 frames**; the
   first frame is the standing pose, which the engine shows when the character is
   not moving (`objects/o_actor/Step_0.gml:327`).
3. Set the **origin** to the feet: horizontally centred, vertically on the bottom
   row of the sprite. In the sprite editor's **Properties** panel, open the *Origin*
   drop-down (it starts at *Top Left*) and choose **Bottom Centre**; you can then
   adjust X and Y by hand. Kris, for instance, is `10, 37` on a 19 × 38 sprite.

    !!! warning "Never leave the origin at the GameMaker default"
        The default is the top-left corner. A character whose origin is at the head
        floats above the ground, and the party lines up by their heads instead of
        their feet.

4. In the same Properties panel, set **Fps** to **4**. The editor starts at 30
   frames per second, which makes a walking animation run far too fast; the
   base-game character sprites use 4 (*Time Units*: *Frames per second*).
5. Set the **collision mask** to *Manual*, type *Rectangle*, and make it a small
   box at the feet. Look at what the base-game characters use:

    | Sprite | Mask (left, top → right, bottom) | Size |
    |---|---|---|
    | `spr_kris_down` | 2, 29 → 16, 36 | 15 × 8 |
    | `spr_susie_down` | 5, 35 → 19, 42 | 15 × 8 |
    | `spr_ralsei_down` | 3, 32 → 17, 39 | 15 × 8 |
    | `spr_noelle_down` | 4, 38 → 18, 45 | 15 × 8 |

    Every one of them is **15 × 8 pixels**, roughly centred horizontally on the
    origin (within a pixel or two), with the bottom edge one row above the origin
    row. Copy that recipe: for a sprite whose origin is `(ox, oy)`, make a box
    about 15 pixels wide centred on `ox`, 8 pixels tall, with
    bottom = `oy - 1` and top = `oy - 8`.

!!! info "Why a small box at the feet?"
    DELTARUNE is drawn with the characters' heads overlapping what is "behind"
    them. If the collision box covered the whole body, a character could not walk
    close to a wall without their head stopping them. A box at the feet lets the
    head pass in front of a wall while the feet stay on the floor.

### Where the mask really comes from

The mask belongs to the **object**, not to each sprite. In the engine, each party
actor object (`o_actor_kris`, `o_actor_susie`, …) has its *Collision Mask* set to
that character's `_down` sprite, and the same box is used no matter which direction
the character faces. The `up`, `left` and `right` sprites of Kris have an automatic
mask (the whole picture), which is simply never used for walls.

So you only need the careful manual mask on **one** sprite, `spr_berto_down`, and
the object you make in the next chapter will point at it.

---

## Step 2 — The other directions, and the naming scheme

The engine finds a character's sprites **by name**, not by a list you fill in.
For a character named `berto`, with no prefix, it builds names with this scheme
(`scripts/party_scripts/party_scripts.gml:202`, `party_get_sprite_from_scheme`):

```text
spr_{prefix}_{name}_{identifier}      →      spr_berto_down
```

The minimum a walking character needs is four sprites, one per direction:

| Sprite | Used for |
|---|---|
| `spr_berto_down` | facing / walking down |
| `spr_berto_up` | facing / walking up |
| `spr_berto_left` | facing / walking left |
| `spr_berto_right` | facing / walking right |

Create the other three in the same way as `spr_berto_down`: same origin rule,
4 frames each. (The mask does not matter for them, as explained above.)

Everything else is optional, and each optional sprite has a name the engine
searches for (`scripts/party_scripts/party_scripts.gml:225`, `party_get_cardinal`):

| Name pattern | What it adds |
|---|---|
| `spr_berto_walk_down` (and `_up`, `_left`, `_right`) | A separate walking sprite. If it exists it is used for walking instead of `spr_berto_down`. |
| `spr_berto_idle_down` (and the others) | A separate standing animation. Without it, the engine shows frame 0 of the walking sprite and freezes it. |
| `spr_berto_down_light` | The Light World version. In the Light World the engine appends `_light` to the name it looks for (`party_m_get_cardinal`). |
| `spr_berto_ball`, `spr_berto_landed`, `spr_berto_slide` | The ball, landing and sliding poses (`objects/o_actor/Other_12.gml`). |

A **state** is a suffix at the very end of the name (`spr_berto_down_happy`), chosen
by the character's `s_state` field, which the next chapter introduces. You can
ignore it for now.

!!! tip "Using a project prefix"
    The scheme begins with `{prefix}`, which is empty by default. If you give the
    character a prefix (the engine's own examples use `ex`), every name gains it:
    `spr_ex_berto_down`. Double underscores are collapsed, which is why an empty
    prefix does not leave a gap in the name.

!!! warning "A wrong name gives you a grey square, not an error"
    When the engine cannot find a sprite by name it silently uses `spr_default`, a
    20 × 20 placeholder. So `spr_berto_dowm` (typo) will not crash anything. Berto
    will just turn into a square. If a direction shows the placeholder, check the
    spelling of that sprite first.

!!! note "Climbing sprites"
    The `o_actor` object falls back to **Kris's** climbing sprites
    (`spr_kris_climb`, …, `objects/o_actor/Create_0.gml:77`). A new character
    works in a climbing room, but climbs as Kris looks. This book does not cover
    custom climbing sprites yet.

---

## Step 3 — See it: a test object

A sprite is easier to trust once you can see its origin and mask. We will make a
throwaway object that draws both on top of the sprite. (It is a plain object, not
the character; the character comes in the next chapter.)

1. **Create → Object**, name it **`o_test_berto`**.
2. Set its **Sprite** to `spr_berto_down`, and its **Collision Mask** to
   `spr_berto_down` too.
3. In the **Create** event:

    ```gml
    // objects/o_test_berto/Create_0.gml
    image_speed = 1;    // play the 4 walking frames, so you can see all of them
    ```

4. In the **Draw** event:

    ```gml
    // objects/o_test_berto/Draw_0.gml
    draw_self();

    // the collision mask, in red
    draw_rectangle_color(bbox_left, bbox_top, bbox_right, bbox_bottom,
                         c_red, c_red, c_red, c_red, true);

    // the origin, as a green dot
    draw_circle_color(x, y, 1, c_lime, c_lime, false);
    ```

The object is done. To see it you need a room, which is the next step.

## Step 4 — A minimal test room

You do not need a finished area, only somewhere to put the object. If you have
never made a room, this is the shortest recipe. (A complete, decorated room is
built in [Your first room](../overworld/your-first-room.md).)

1. In the **Asset Browser**, right-click your rooms folder → **Create → Room**.
   Name it **`room_test_characters`**.
2. In the room's settings, set the size to **640 × 480** and the grid to
   **20 × 20**, as in that chapter.
3. On the room's default **Instances** layer, place two objects:
    - **`o_dev_world`**, anywhere (for example at `20, 20`);
    - **`o_dev_playermarker`**, at `320, 380`: this is where the party appears.
4. Place **`o_test_berto`** a little to the right of the marker, for example at
   `400, 380`.
5. Run the game (++f5++), hold ++tab++ + ++r++ and pick `room_test_characters`.

!!! danger "Do not place `o_camera`"
    The engine creates the camera by itself. A second one makes the screen go
    completely black ([Rooms and collision](../overworld/rooms-and-collision.md)).

This room has no tiles, so you will see a plain background. That is enough for
this chapter; the book's own first room was also blank at this point
(see [Your first room](../overworld/your-first-room.md)). I have not tested a room
with no layers other than Instances, so if anything misbehaves, compare with
that chapter's layer setup.

You should see Berto next to Kris and company, with:

- a **green dot at the feet**, in the middle of the character;
- a **small red box around the feet**, not around the whole body.

If the dot is at the head, the origin is wrong (Step 1, item 3). If the red box
covers the whole sprite, the mask is still set to automatic (Step 1, item 5). If
Berto is a grey square, the sprite name is wrong (Step 2).

!!! danger "Do not place `o_actor_<your name>` in a room yet"
    A party actor looks its data up in the party registry when it is created
    (`objects/o_actor/Other_12.gml`). Until Berto is registered as a party member,
    which is what the next chapter does, an `o_actor_berto` would not find its
    data. That is why this chapter uses a plain test object.

---

## Common problems

| Symptom | Likely cause |
|---|---|
| The character floats above the ground | The origin is not at the feet |
| The character walks "into" walls up to the chest | The collision mask covers the body instead of the feet |
| One direction is a grey 20 × 20 square | That sprite's name is misspelled, or the sprite does not exist |
| The red box is bigger than the feet | The mask is still *Automatic*; set it to *Manual* |

## Next

*Your first party member*: turn these sprites into a
character the engine knows about, and make it follow Kris.
