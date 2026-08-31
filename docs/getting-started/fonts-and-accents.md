# Fonts and accents

If your game is in English, you can skip this chapter. If it is in Portuguese, Spanish, French, German, Turkish or anything else with diacritics, read it before you write dialogue — the fix is easy, but the failure mode is silent and the wrong fix wastes an afternoon.

## The symptom

Write a line with an accent and run it:

```gml
text = "{col(y)}* Bem-vindo Sérgio, Bonitão.{col(w)}{p}{e}"
```

On screen you get:

```text
* Bem-vindo Srgio, Bonito.
```

The accented characters vanish, and the letters carrying them go with them. No error, no warning, nothing in the Output window.

## The cause

The engine's fonts are **bitmap fonts**: every glyph is a slice of a prepared image (`fonts/font_main/font_main.png`), and the `.yy` file holds a table of which characters were drawn. That table covers ASCII only:

```json
"ranges":[
    {"lower":32,"upper":127,},
    {"lower":9647,"upper":9647,},
]
```

`á` is 225. `ç` is 231. `ã` is 227. All above 127, so they are simply **not in the atlas**. GameMaker has nothing to draw and draws nothing.

!!! info "This is not a UTF-8 problem"
    Your `.gml` is fine, the encoding is fine, GameMaker read the right string. The gap is at draw time only. Changing file encodings will not help.

Fixing it means **regenerating each font with the accented characters included** — and for that, GameMaker needs the original typeface installed on your system, because the project ships no `.ttf` files at all.

## What you need

One font: **`8bitoperator JVE`** by Jayvee Enaguas (GrafxKid). It is a free pixel font and it covers the full Latin-1 accent set. Search for it by name and prefer the author's own page over font aggregator sites, which are re-uploads.

!!! warning "About the engine's other source fonts"
    The project references six source typefaces, and not all of them are obtainable. In particular, the one named `Monospaced JVE` in the `.yy` — the font behind **all dialogue** — is not distributed anywhere. **You do not need it.** Step 4 shows how to use `8bitoperator` in its place and step 5 restores the spacing. Do not spend time hunting for it.

---

## Step 1 — Branch

You are about to modify binary assets. One mistake dirties several files at once, and Git is the civilised way back.

```bash
git switch -c fonts
```

**Check:** `git status` is clean and `git branch --show-current` says `fonts`.

---

## Step 2 — Build a test room

Do not test in the middle of your game. A minimal room opens in two seconds and isolates the variable.

1. **Create → Room**, name it `RoomTest`.
2. Drag in three objects:
    - **`o_dev_world`** — the game controller. Nothing works without it.
    - **`o_dev_playermarker`** — where the player spawns.
    - **`o_ow_sign`** — the sign you will read.
3. Select the sign and put this in its **Instance Creation Code**:

    ```gml
    text = "{col(y)}* Bem-vindo Sérgio, Bonitão.{col(w)}{p}{e}"
    ```

    That sentence carries two different accent families: `é` (acute, 233) and `ã` (tilde, 227). If both survive, the rest will too.

4. Run. If `RoomTest` is not the first room, open the console with ++tab++, type `room_select`, and pick it.
5. Read the sign, and **write down what you saw**. That is your "before".

---

## Step 3 — Install the typeface

=== "Linux (Mint, Ubuntu…)"

    ```bash
    mkdir -p ~/.local/share/fonts
    cp ~/Downloads/8bitoperator_jve.ttf ~/.local/share/fonts/
    fc-cache -f
    ```

    Or double-click the `.ttf` in the file manager and press **Install**.

=== "Windows"

    Double-click the `.ttf` and press **Install**.

=== "macOS"

    Double-click the `.ttf` and press **Install Font**.

### Confirm the system sees it

```bash
fc-list : family | grep -i "8bitoperator"
```

It must print `8bitoperator JVE`. **That exact name matters** — it is what you will select inside GameMaker.

### Confirm it actually has the accents

```bash
fc-list ":lang=pt" family | grep -i "8bitoperator"
```

If the name appears, the font covers the language. A more thorough checker is at the [end of this page](#tool-does-this-font-have-the-glyphs-i-need).

### Restart GameMaker

!!! danger "This step is not optional"
    The IDE builds its list of system fonts **at startup**. If it was already open when you installed, it still cannot see the font — and it will not tell you. It quietly generates the bitmap from a substitute typeface, and your pixel art becomes a smooth, larger font.

---

## Step 4 — Find out which font your text uses, then fix it

### There are three text fonts, not one

This is the step that costs the most time. The engine does not draw all text with the same font — it picks by context, and **fixing the wrong asset changes nothing on screen**:

| The text | Font used | Asset |
|---|---|---|
| Signs, overworld dialogue, cutscenes, ACT text | `loc_font("text")` | **`font_main_mono`** |
| **Enemy speech bubble, during battle** | `loc_font("enc")` | **`font_dotumche`** |
| Menus, console, enemy names, HP/TP, game over | `loc_font("main")` | **`font_main`** |

Which key maps to which asset lives in `datafiles/loc/fonts.json`.

**Your test sign** takes this path:

```text
o_ow_sign → dialogue_start()            objects/o_ow_sign/Other_10.gml:1
          → o_ui_dialogue
          → text_typer_create()         objects/o_ui_dialogue/Other_10.gml:15
          → o_text_typer
                font = loc_font("text")     objects/o_text_typer/Create_0.gml:5
          → fonts.json:  "font_text" → "font_main_mono"
```

**The enemy bubble branches off midway.** It goes through the same `o_text_typer`, but a *preset* swaps the font:

```text
enemy.dialogue → actor_dialogue_create()          scripts/misc/misc.gml:313
               → o_ui_actordialogue
                     preset = "{preset(enemy_text)}"    Create_0.gml:7
               → o_text_typer, handling that preset:
                     font = loc_font("enc")             Other_10.gml:98
               → fonts.json:  "font_enc" → "font_dotumche"
```

So it is entirely possible to fix the sign, walk into a battle, and watch the enemy still speak without accents. **Different assets.**

!!! info "There are other presets"
    The same mechanism applies to `{preset(god_text)}` and `{preset(light_world)}`, defined in `objects/o_text_typer/Other_10.gml:96`. If some text is still broken after everything else works, look for a `{preset(...)}` at the start of it.

### Fix it

1. Open **`font_main_mono`** in the Asset Browser.
2. In the **Font** field, replace `Monospaced JVE` with **`8bitoperator JVE`**.
3. Under **Character Range**, click **Add** and enter *lower* = **192**, *upper* = **255**. That covers `À`–`ÿ`, every accented character in Portuguese, Spanish, French and German. Use 160 instead of 192 if you also want `º ª « » ¿`.
4. **Force regeneration.** GameMaker only redraws the bitmap when something changes — nudge **Size** from `12` to `13` and back to `12`.
5. **Ctrl+S.**

**Check** the font preview right there in the editor:

| Preview shows | Meaning |
|---|---|
| Pixel art, with `À Á Â Ã Ç É` among the glyphs | ✅ done, go to step 5 |
| Pixel art, but the accents are blank gaps | the selected typeface lacks those glyphs — revisit step 3 |
| Smooth, larger letters with no pixels | the IDE did not find the font — close it, reopen, redo this step |

Run `RoomTest`. The sign should now read **`Bem-vindo Sérgio, Bonitão.`** — but with letter spacing that looks different from the rest of the game. Step 5 fixes that.

---

## Step 5 — Restore the original spacing

tlDR dialogue is **monospaced**: every character advances exactly 8 pixels. That is what gives the text its typewriter rhythm.

`8bitoperator` is proportional — `.` advances 3px, `i` advances 7, `W` advances 8. Regenerating from it in step 4 gave the dialogue that variable spacing. This step puts the fixed advance back.

It is safe because no glyph in the font is drawn wider than 8px, so nothing can bleed into the next character.

1. **Close the project** in GameMaker. The IDE rewrites the `.yy` when it saves, so it must not have the file open.
2. From the project root:

    ```bash
    python3 - <<'EOF'
    import re
    p = 'fonts/font_main_mono/font_main_mono.yy'
    s = open(p).read()
    def fix(m):
        return f'{m.group(1)}"shift":{16 if int(m.group(2)) > 9000 else 8},'
    s2, n = re.subn(r'("(\d+)":\{"character":\d+,"h":\d+,"offset":\d+,)"shift":\d+,', fix, s)
    open(p, 'w').write(s2)
    print("glyphs set to a fixed advance of 8:", n)
    EOF
    ```

3. Reopen the project.

!!! warning "This is always the last step"
    If you go back into the font editor and touch Size, Range or Font again, the IDE regenerates the `.yy` from scratch and the spacing reverts. That is not a bug — just run the script again. Get the font right in the IDE first, run the script last.

---

## Step 6 — Test

### On screen

| Stage | Expected result |
|---|---|
| Before anything | `* Bem-vindo Srgio, Bonito.` |
| After step 4 | `* Bem-vindo Sérgio, Bonitão.` with tight, uneven spacing |
| After step 5 | `* Bem-vindo Sérgio, Bonitão.` with the engine's regular rhythm |

Compare the last one against any other text in the game — a menu, a sign in `room_ex_church` — to confirm the letter rhythm matches.

### Test the enemy bubble too

Signs and battle bubbles use **different fonts**, so one can be right while the other is broken:

1. Open the console (++tab++) and type `encounter_select`.
2. Pick any encounter whose enemy speaks with accented text.
3. Read the bubble above the enemy at the start of the round.

| What happens | Meaning |
|---|---|
| Sign **and** bubble correct | ✅ `font_main_mono` and `font_dotumche` are both fine |
| Sign correct, bubble broken | `font_dotumche` still needs fixing — see step 7 |
| Bubble correct, sign broken | `font_main_mono` still needs fixing — see step 4 |
| Enemy name in the list broken | `font_main` still needs fixing — see step 7 |

### In the files

You can check without launching the game. From the project root:

```bash
python3 - <<'EOF'
import re, glob, os
for f in sorted(glob.glob('fonts/*/*.yy')):
    if f.endswith('.old.yy'): continue                       # skip IDE backups
    if os.path.basename(f)[:-3] != os.path.basename(os.path.dirname(f)): continue
    s = open(f).read()
    name = re.search(r'"%Name":"([^"]*)"', s).group(1)
    ttf  = re.search(r'"fontName":"([^"]*)"', s).group(1)
    lh   = re.search(r'"lineHeight":(\d+)', s).group(1)
    rng  = re.findall(r'\{"lower":(\d+),"upper":(\d+),\}', s)
    ac   = re.search(r'"225":\{"character":225,"h":\d+,"offset":\d+,"shift":\d+,"w":(\d+)', s)
    st   = "no a-acute" if not ac else ("a-acute EMPTY" if ac.group(1) == '0' else "a-acute OK")
    print(f'{name:22} {ttf:26} lineHeight={lh:<3} {st:14} ranges={rng}')
EOF
```

How to read the row for the font you fixed:

| Column | Value | Meaning |
|---|---|---|
| state | `a-acute OK` | ✅ the glyph made it into the atlas |
| state | `no a-acute` | the range was never widened, or you did not save |
| state | `a-acute EMPTY` | range is right, but the typeface has no such glyph |
| `lineHeight` | `16` | ✅ came from the pixel font |
| `lineHeight` | much larger (e.g. `22`) | the IDE used a substitute — restart it and redo step 4 |
| `fontName` | anything | **proves nothing.** The `.yy` always stores the name you asked for, even when the IDE could not find it |

!!! tip "Independent proof that the range was the whole problem"
    In that same output, look at the fonts ending in **`_ja`** (the Japanese ones). They ship with range `32–65439` and report `a-acute OK` in a freshly cloned project, with no work from you. Same engine, same system — accents always worked in those.

---

## Step 7 — The other two text fonts

Steps 4 and 5 fixed signs and cutscenes. Two assets remain, and you will notice their absence in specific places:

| Asset | You notice when… | Source typeface | What to do |
|---|---|---|---|
| `font_main_mono` | a sign or cutscene eats accents | unobtainable | ✅ done in steps 4–5 |
| **`font_dotumche`** | **an enemy speaks without accents in battle** | DotumChe Pixel | not obtainable — see below |
| `font_main` | an enemy name or a menu eats accents | 8bitoperator JVE | you already have the typeface |

### `font_main` — the easy one

Its source typeface is the one you installed. Repeat step 4 **without changing the Font field** (it already says `8bitoperator JVE`) and **without doing step 5** — this font is proportional on purpose.

### `font_dotumche` — the enemy bubble

`DotumChe Pixel` is not obtainable either. Two ways out:

**A. Point the key at a font you already fixed.** One line in `datafiles/loc/fonts.json`:

```json
"font_enc": {
    "en": "font_main",
    "ja": "font_dotumche_ja"
}
```

Ten seconds, and the bubble uses the same font as the menus.

**B. Regenerate the asset from `8bitoperator JVE`.** Open `font_dotumche`, change the **Font** field, add range 192–255, force regeneration. More work, but it keeps the assets separate — useful if you later want a distinct look per context.

### The rest

`font_lwmenu` (Light World menu), `font_prophecy` (overworld prophecy) and `font_8bit` only matter if your game uses those screens. The procedure never changes: install the source typeface → widen the range → force regeneration.

!!! tip "Fix on demand"
    Do not try to fix all six at once. Play, find text that is broken, work out which asset draws it (step 4), fix that one, keep playing.

---

## When things go wrong

| Symptom | Cause |
|---|---|
| Accents vanish, no error | the font's range is 32–127 — step 4 |
| Fixed a font and the sign did not change | wrong asset; dialogue is `font_main_mono` — step 4 |
| The font lost its pixels and got bigger | the IDE could not find the typeface and substituted one — restart it (step 3) |
| Installed the font, the IDE does not list it | it reads the list only at startup — restart |
| Changed the range and nothing happened | the bitmap was not regenerated — nudge Size, then save |
| Accents render as blank space | the typeface has no such glyph — step 7 |
| Dialogue spacing became uneven | step 5 is missing |
| Ran the script, then the spacing reverted | the IDE regenerated afterwards; run the script again, last |
| Menus and dialogue use different fonts | they are different assets — step 7 |
| Everything is broken | see below |

### Undoing everything

```bash
git checkout -- fonts/
rm -f fonts/*/*.old.png fonts/*/*.old.yy
```

The `rm` clears the backups GameMaker makes when it regenerates. Then **close and reopen the project** so the IDE rereads the bitmaps from disk.

---

## Tool: does this font have the glyphs I need?

Worth checking before adopting any new typeface. This reads the installed `.ttf`'s `cmap` and tests the accented characters one by one:

```bash
python3 - <<'EOF' "8bitoperator"
import struct, sys, subprocess
target = "áàâãçéêíóôõúüÁÀÂÃÇÉÊÍÓÔÕÚÜºª"
name = sys.argv[1] if len(sys.argv) > 1 else "8bitoperator"
out = subprocess.run(['fc-list'], capture_output=True, text=True).stdout
path = next((l.split(':')[0] for l in out.splitlines() if name.lower() in l.lower()), None)
if not path:
    print("font not installed:", name); raise SystemExit

d = open(path, 'rb').read()
tabs = {}
for i in range(struct.unpack('>H', d[4:6])[0]):
    o = 12 + 16*i
    tabs[d[o:o+4].decode('latin1')] = struct.unpack('>II', d[o+8:o+16])
off = tabs['cmap'][0]
chars = set()
for i in range(struct.unpack('>H', d[off+2:off+4])[0]):
    _, _, so = struct.unpack('>HHI', d[off+4+8*i:off+12+8*i])
    t = off + so
    fmt = struct.unpack('>H', d[t:t+2])[0]
    if fmt == 4:
        segX2 = struct.unpack('>H', d[t+6:t+8])[0]; seg = segX2//2
        ends   = struct.unpack('>%dH' % seg, d[t+14:t+14+segX2])
        starts = struct.unpack('>%dH' % seg, d[t+16+segX2:t+16+2*segX2])
        for s, e in zip(starts, ends):
            if e != 0xFFFF: chars.update(range(s, e+1))
    elif fmt == 6:
        first, cnt = struct.unpack('>HH', d[t+6:t+10]); chars.update(range(first, first+cnt))
    elif fmt == 0:
        chars.update(c for c in range(256) if d[t+6+c])

missing = [c for c in target if ord(c) not in chars]
print(path)
print("glyphs in font:", len(chars))
print("MISSING:", ''.join(missing) if missing else "(none) — safe to use")
EOF
```

Pass a different name to test another: `... EOF "crypt of tomorrow"`.

---

## Quick reference

```text
Accent range:        192–255       (or 160–255 to include º ª « » ¿)
á=225  ã=227  ç=231  é=233  í=237  ó=243  õ=245  ú=250

The THREE text fonts:
  signs / cutscenes / ACT text   loc_font("text")  -> font_main_mono
  enemy bubble (in battle)       loc_font("enc")   -> font_dotumche
  menus / names / HP / TP        loc_font("main")  -> font_main
Font map:            datafiles/loc/fonts.json

Order that works:
  install ttf -> restart IDE -> change Font -> widen range
  -> force regen (Size 12->13->12) -> save -> close project -> advance script

Undo:                git checkout -- fonts/
```
