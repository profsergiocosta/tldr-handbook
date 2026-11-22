# Joining and leaving the party

Until now you have added Berto with the debug console. A game needs the story to do it:
a scene where he asks to join, and one where he leaves. This chapter builds both with
**triggers** and **cutscenes**.

It uses the face and voice from [Light World and dialogue](light-world-and-dialogue.md), so
do that chapter's Part 2 first. If you skip it, remove the `{char(berto, 0)}` tags from the
text below and the scenes still work.

---

## The three functions

| Function | What it does |
|---|---|
| `party_member_add(name)` | Appends `name` to `global.party_names`, creates his actor at the leader's position, and repositions the party (`scripts/party_scripts/party_scripts.gml`). |
| `party_member_kick(name)` | Removes `name` from the list, destroys his actor and repositions the party. |
| `party_contains(name, true)` | Whether `name` is in the party. |

`name` is always the **registration name** (`"berto"`). Both functions are plain
functions, not cutscene events: inside a cutscene you call them with
`cutscene_func`, so that they run at the right moment in the queue.

---

## Step 1 — A scene where he joins

In `room_test_characters`, place an **`o_trigger`** and **stretch it** so the party must
walk over it (see [Rooms and collision](../overworld/rooms-and-collision.md) for why).
In its Instance Creation Code:

```gml
trigger_code = function() {
    if party_contains("berto", true)
        exit

    cutscene_create()
    cutscene_player_canmove(false)
    cutscene_dialogue([
        "{char(berto, 0)}* Hi! I'm Berto.",
        "{char(berto, 1)}* Mind if I tag along?"
    ])
    cutscene_func(party_member_add, ["berto"])
    cutscene_sleep(15)
    cutscene_dialogue("{char(berto, 1)}* Thanks!")
    cutscene_player_canmove(true)
    cutscene_play()
}

trigger_exit_code = function() {
    triggered = false      // re-arm when the player leaves
}
```

Read it as a script:

1. If Berto is already in the party, do nothing.
2. Freeze the player, show two lines of dialogue.
3. `cutscene_func(party_member_add, ["berto"])` calls `party_member_add("berto")`
   at that point in the queue: the argument list is the array.
4. Wait half a second, one more line, and return control.

`cutscene_create` ... `cutscene_play` and the other functions are explained in
[Cutscenes](../overworld/cutscenes.md).

**Test:** wipe the save if needed, run, go to the room and walk over the trigger. After
the scene, Berto stands behind Kris and follows.

!!! tip "If he appears to jump"
    The engine documents `cutscene_party_interpolate()` as the way to attach party members
    back to the "caterpillar" after a scene (`scripts/cutscene_events/cutscene_events.gml`).
    If Berto teleports or lags when you regain control, add it before
    `cutscene_player_canmove(true)`. I have not seen this case in a test.

---

## Step 2 — A scene where he leaves

Place a second stretched `o_trigger` elsewhere in the room:

```gml
trigger_code = function() {
    if !party_contains("berto", true) || global.party_names[0] == "berto"
        exit

    cutscene_create()
    cutscene_player_canmove(false)
    cutscene_dialogue("{char(berto, 1)}* I have to go. See you!")
    cutscene_func(party_member_kick, ["berto"])
    cutscene_sleep(15)
    cutscene_player_canmove(true)
    cutscene_play()
}

trigger_exit_code = function() {
    triggered = false
}
```

The guard in the first line also checks that Berto is **not the leader** (the first entry of
`global.party_names`). I did not look at what kicking the leader does, so the scene refuses
to.

**Test:** walk over the join trigger, then the leave trigger: he joins, follows, then
disappears from the party.

!!! warning "The party can be full"
    `party_member_add` does not check the size of the party. How many members are drawn in
    battle is limited by `global.party_limit` (`party_length` in
    `scripts/party_scripts/party_scripts.gml`), and the original game's party is three.
    I have not tested adding a fourth.

---

## Starting the game with Berto in the party

The default party is set in `o_world`'s Game Start event
(`objects/o_world/Other_2.gml`):

```gml
global.party_names = [   // <-- if you wish to change the default team members, change them here
    "kris", "susie", "ralsei"
]
```

Add `"berto"` there to start with him already in the party. A saved game, again, has its
own copy of `global.party_names` and overrides this.

!!! danger "Berto as the leader"
    The **first** name in that list is the leader, the character you control. Putting
    `"berto"` first should make him the playable character, because the room's player
    marker creates the leader from `global.party_names[0]`
    (`objects/o_dev_playermarker/Other_4.gml`). This is the part of Part 5 I trust least:
    his collision mask, his Light World sprites and his climbing sprites (which fall back
    to Kris's) all matter much more when he is the one walking into walls. Try it, and
    expect to fix things.

## Checklist: a complete party member

Everything Berto needed, in order:

| | Chapter | What |
|---|---|---|
| ☐ | [Character sprites](sprites.md) | 4 directions × 4 frames, origin at the feet, a manual feet mask |
| ☐ | [Your first party member](first-party-member.md) | `o_actor_berto`, `party_m_berto`, two registrations in `o_world` |
| ☐ | [Battle sprites and icons](battle-sprites.md) | `battle_sprites`, three icons |
| ☐ | [Stats, equipment and spells](stats-and-equipment.md) | stats, weapon, armour, a spell |
| ☐ | [Light World and dialogue](light-world-and-dialogue.md) | `_light` sprites, face and voice |
| ☐ | This chapter | joining and leaving |
