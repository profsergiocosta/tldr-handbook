# The tlDR Engine Handbook

A practical guide to building a DELTARUNE-style game with the
[tlDR Engine](https://github.com/profsergiocosta/tldr-engine).

Part of the **[LambdaGeo](https://lambdageo.github.io/ebooks/)** collection of
open textbooks.

Not a feature list — a set of walkthroughs that each end with something running
on screen, plus a reference for when you forget a field name.

## Reading it locally

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

mkdocs serve      # http://127.0.0.1:8000
mkdocs build      # static site in ./site
```

Pushing to `main` publishes to GitHub Pages automatically
(`.github/workflows/deploy.yml` runs `mkdocs gh-deploy`).

## Contents

| Part | |
|---|---|
| **Getting Started** | installing the project; getting accented characters to render |
| **The Overworld** | rooms, collision, NPCs, dialogue, tiles |
| **The Battle System** | how a fight works; a complete worked enemy; the arena; advanced patterns |
| **Reference** | `enemy()`, `enc_set()`, the turn object |

## About the engine references

Everything here was checked against the engine source rather than remembered.
References look like `objects/o_enc/Step_0.gml:321` — path, then line.

**Verified against tlDR Engine commit `7308e305`.** Line numbers drift as the
engine changes; file paths and behaviour are far more stable than the numbers.
If a reference does not line up, search for the surrounding code instead, and
please open an issue.

## Contributing

Corrections are very welcome, particularly:

- engine references that have gone stale
- behaviour that differs from what is described
- steps that were unclear when you followed them

## Licence

The handbook text is CC BY 4.0. The tlDR Engine itself is MIT, © tweenko.
