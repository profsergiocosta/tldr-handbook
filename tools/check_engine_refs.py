#!/usr/bin/env python3
"""Check the handbook against a tlDR Engine checkout.

Two checks:

1. Every `path:line` reference (e.g. `objects/o_enc/Step_0.gml:336`) must
   point to an existing file and a line inside it. The matching line is
   printed with --show so a human can confirm it still says what the text
   claims.
2. Every engine-looking identifier used in code (assets such as `spr_`,
   `snd_`, `o_`, and engine functions such as `party_`, `item_`, `cutscene_`)
   must exist in the engine, unless the handbook itself creates it (a
   `function name(` in a code block, or a name listed in
   tools/reader_names.txt for objects and sprites the reader is told to make).

Usage:
    python3 tools/check_engine_refs.py --engine ../tldr-engine [--show]

Exits with status 1 if anything is missing.
"""
import argparse
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(HERE, "..", "docs")

REF = re.compile(r"`?((?:objects|scripts|rooms|options|fonts|sprites)/[A-Za-z0-9_./-]+\.(?:gml|yy)):(\d+)(?:-(\d+))?`?")
SHORT_REF = re.compile(r"`(o_[A-Za-z0-9_]+/[A-Za-z0-9_]+\.gml):(\d+)`")
CODE_BLOCK = re.compile(r"```[a-z]*\n(.*?)```", re.S)
INLINE = re.compile(r"`([^`\n]+)`")
PREFIXES = ("spr_", "snd_", "mus_", "o_", "room_", "tile_", "party_", "item_",
            "shop_", "recruit_", "enc_", "cutscene_", "actor_", "camera_",
            "memory_", "lighting_", "dodge_", "climb_", "music_", "dialogue_")
IDENT = re.compile(r"\b(" + "|".join(PREFIXES) + r")[A-Za-z0-9_]+\b")


def engine_symbols(engine):
    names = set()
    for folder in ("objects", "sprites", "sounds", "rooms", "scripts",
                   "tilesets", "fonts", "paths", "shaders"):
        path = os.path.join(engine, folder)
        if os.path.isdir(path):
            names.update(os.listdir(path))
    words = set()
    for f in glob.glob(os.path.join(engine, "**", "*.gml"), recursive=True):
        if f.endswith(".bak"):
            continue
        with open(f, errors="ignore") as fh:
            words.update(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", fh.read()))
    return names | words


def reader_names():
    path = os.path.join(HERE, "reader_names.txt")
    if not os.path.exists(path):
        return set()
    with open(path) as fh:
        return {l.strip() for l in fh if l.strip() and not l.startswith("#")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine", required=True, help="path to a tldr-engine checkout")
    ap.add_argument("--show", action="store_true", help="print the engine line for every reference")
    args = ap.parse_args()

    symbols = engine_symbols(args.engine)
    allowed = reader_names()
    pages = sorted(glob.glob(os.path.join(DOCS, "**", "*.md"), recursive=True))

    defined = set(allowed)
    for page in pages:
        with open(page) as fh:
            for block in CODE_BLOCK.findall(fh.read()):
                defined.update(re.findall(r"function\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(", block))

    problems = 0
    for page in pages:
        rel = os.path.relpath(page, DOCS)
        with open(page) as fh:
            text = fh.read()
        lines = text.splitlines()

        for n, line in enumerate(lines, 1):
            refs = [(m.group(1), m.group(2)) for m in REF.finditer(line)]
            refs += [("objects/" + m.group(1), m.group(2)) for m in SHORT_REF.finditer(line)]
            for path, num in refs:
                target = os.path.join(args.engine, path)
                if not os.path.exists(target):
                    print(f"{rel}:{n}: missing file {path}")
                    problems += 1
                    continue
                with open(target, errors="ignore") as fh:
                    src = fh.read().splitlines()
                num = int(num)
                if num > len(src):
                    print(f"{rel}:{n}: {path}:{num} is past the end ({len(src)} lines)")
                    problems += 1
                elif args.show:
                    print(f"{rel}:{n}: {path}:{num}: {src[num - 1].strip()[:100]}")

        code = "\n".join(CODE_BLOCK.findall(text)) + "\n" + "\n".join(INLINE.findall(text))
        code = re.sub(r'"(?:[^"\\]|\\.)*"', "", code)
        for m in sorted({x.group(0) for x in IDENT.finditer(code)}):
            if m.endswith("_") or m in symbols or m in defined:
                continue
            print(f"{rel}: unknown engine name `{m}`")
            problems += 1

    print(f"\n{problems} problem(s)")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
