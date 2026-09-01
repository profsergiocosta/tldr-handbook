# Reference: `shop()`

The base struct that defines a shopkeeper, catalog, dialogue responses, and conversation topics. Defined in `scripts/shops/shops.gml`.

You define a shop by inheriting from `shop()`:

```gml
function my_shop() : shop() constructor {
    flavor = "* Welcome to my shop!";
    // override only what you need
}
```

---

## Identity & Audio

| Field | Default | Meaning |
|---|---|---|
| `flavor` | `"* Shop flavor text."` | String or function returning the greeting text when opening the shop. |
| `flavor_prefix` | `""` | Markup prefix attached before flavor dialogue (e.g. voice blip or character link). |
| `bgm` | `noone` | Sound/Music asset to stream in the shop screen. |
| `bgm_pitch` | `1` | Pitch multiplier for the shop soundtrack. |
| `bgm_gain` | `1` | Volume gain (0.0 to 1.0) for the shop soundtrack. |
| `shopkeeper` | `undefined` | Shopkeeper object (`o_shop_shopkeep` child) containing animated talk and idle sprites. |
| `shopkeeper_x` | `160` | X position on the shop screen. |
| `shopkeeper_y` | `120` | Y position on the shop screen. |

---

## Navigation & Return

| Field | Default | Meaning |
|---|---|---|
| `return_room` | `noone` | Room to load upon selecting the EXIT option. |
| `return_marker_id` | `0` | ID of the `o_dev_marker_land` where Kris lands when leaving the shop. |
| `return_direction` | `undefined` | Facing direction (`DIR.DOWN`, `DIR.UP`, etc.) upon exiting. |

---

## Shop Options Array (`options`)

An array of 4 shop option constructors:

### 1. `new shop_option_buy(items_array, [dialogue_callback])`
- `items_array`: Array of item struct instances (e.g. `[new item_candy(), new item_sword()]`).
- `dialogue_callback`: Function receiving a `context` parameter from `SHOP_TALK_CONTEXT`:
  - `SHOP_TALK_CONTEXT.IDLE`
  - `SHOP_TALK_CONTEXT.BOUGHT`
  - `SHOP_TALK_CONTEXT.BOUGHT_STORAGE`
  - `SHOP_TALK_CONTEXT.NOT_ENOUGH`
  - `SHOP_TALK_CONTEXT.NO_SPACE`
  - `SHOP_TALK_CONTEXT.CANCELED`

### 2. `new shop_option_sell([dialogue_callback])`
- `dialogue_callback`: Function receiving `SHOP_TALK_CONTEXT`:
  - `SHOP_TALK_CONTEXT.IDLE`
  - `SHOP_TALK_CONTEXT.SOLD`
  - `SHOP_TALK_CONTEXT.NO_ITEMS`
  - `SHOP_TALK_CONTEXT.REFUSE`
  - `SHOP_TALK_CONTEXT.CANCELED`

### 3. `new shop_option_talk(topics_array, [dialogue_callback])`
- `topics_array`: Array of `new __shop_talk_option(title, dialogue)` instances.

### 4. `new shop_option_exit(leave_text)`
- `leave_text`: Closing farewell dialogue line before returning to the overworld.
