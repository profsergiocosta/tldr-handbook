# Reference: `item()`

The base struct that defines all consumables, key items, weapons, armors, and spells. Defined in `scripts/item/item.gml`.

You define an item by inheriting from `item()` (or `item_weapon()`):

```gml
function my_item() : item() constructor {
    name = ["MyItem", "My Item"];
    // override only what you need — everything else has a usable default
}
```

!!! danger "Misspelled fields never error"
    GML structs accept any assignment. Writing `buyprice` instead of `buy_price` creates a dead field that nothing reads, with no warning. When a value seems to be ignored, check the spelling first.

---

## Identity & Presentation

| Field | Default | Meaning |
|---|---|---|
| `name` | `["Item"]` | Name array: `[short_name, long_name]` or single string. Short name is used in menu grids. |
| `desc` | `["..."]` | Description array: `[overworld_desc, battle_desc, action_desc, shop_desc]`. |
| `type` | `ITEM_TYPE.CONSUMABLE` | Type enum: `CONSUMABLE`, `KEY`, `WEAPON`, `ARMOR`, `SPELL`, `STORAGE`, `LIGHT`. |
| `icon` | `spr_ui_menu_icon_exclamation` | Icon sprite rendered next to the item in menus. |
| `color` | `c_white` | Text color tint in inventory menus. |

---

## Usage & Execution

| Field | Default | Meaning |
|---|---|---|
| `use_type` | `ITEM_USE.INDIVIDUAL` | Target scope: `ITEM_USE.INDIVIDUAL`, `ITEM_USE.EVERYONE`, or `ITEM_USE.ENEMY`. |
| `can_use` | `true` | Boolean or callable returning whether the item can currently be selected. |
| `use` | `function(item_index, target_index, caller)` | Executed when used in Overworld or Battle. You must call `item_delete(item_index)` for consumables. |
| `tp_cost` | `0` | Tension Points (0–100) required to cast (for spells). |
| `reactions` | `{}` | Struct containing party comment quotes, e.g. `{ susie: "Yum!", ralsei: "Sweet!" }`. |

---

## Equippables & Weapons (`item_weapon`)

| Field | Default | Meaning |
|---|---|---|
| `stats` | `{ attack: 0, defense: 0, magic: 0 }` | Struct with stat modifiers added to the character's base stats. |
| `weapon_whitelist` | `[]` | Array of party character names permitted to equip this weapon (e.g. `["kris", "susie"]`). |
| `effect` | `undefined` | Struct with `{ text: "...", sprite: ... }` shown in the EQUIP status panel. |
| `apply` | `function(party_name)` | Custom hook called when equipped. |
| `deapply` | `function(party_name)` | Custom hook called when unequipped. |

---

## Dual-World Transformations

| Field | Default | Meaning |
|---|---|---|
| `lw_counterpart` | `undefined` | Script reference to the Light World item struct this item transforms into. |
| `dw_counterpart` | `undefined` | Script reference to the Dark World item struct this item transforms into. |

---

## Economy & Shops

| Field | Default | Meaning |
|---|---|---|
| `buy_price` | `0` | Cost in Dark Dollars ($) when purchased in shops. |
| `sell_price` | `undefined` | Sale price when sold to vendors (defaults to half of `buy_price` if undefined). |
| `shop_in_stock` | `infinity` | Number of copies available for purchase in shop inventories. |
| `can_sell` | `true` | Whether vendors will accept this item for purchase. |
