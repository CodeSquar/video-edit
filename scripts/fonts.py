#!/usr/bin/env python3
"""Google Fonts -> assets/fonts/*.woff2 plus the @font-face CSS to paste.

  python fonts.py "Archivo:700" "Archivo:900" "Newsreader:italic:500" [--out assets/fonts]

Each spec is Family[:italic]:weight. Takes the latin subset (covers Spanish/Portuguese accents).
Skip this for the fonts HyperFrames bundles (references/format.md, Fonts).
"""
import argparse, os, re, subprocess, sys, urllib.parse

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"


def get(url):
    """curl, not urllib: Python's certificate store on some machines rejects valid hosts."""
    r = subprocess.run(["curl", "-sSfL", "-m", "30", "-A", UA, url], capture_output=True)
    if r.returncode:
        raise RuntimeError(r.stderr.decode("utf-8", "replace").strip())
    return r.stdout

ap = argparse.ArgumentParser()
ap.add_argument("specs", nargs="+")
ap.add_argument("--out", default="assets/fonts")
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)
css_out = []
for spec in a.specs:
    parts = spec.split(":")
    fam, italic, weight = parts[0], "italic" in parts, parts[-1]
    axis = f"ital,wght@1,{weight}" if italic else f"wght@{weight}"
    url = "https://fonts.googleapis.com/css2?family=" + urllib.parse.quote(fam) + ":" + axis + "&display=swap"
    try:
        css = get(url).decode()
    except Exception as e:
        print(f"{spec}: FAIL {e} (check the family name and that it ships this weight)")
        continue
    # blocks are "/* subset */ @font-face {...}"; keep latin, else the last one
    blocks = re.findall(r"/\*\s*([\w-]+)\s*\*/\s*@font-face\s*{([^}]*)}", css) or [("", css)]
    body = dict(blocks).get("latin", blocks[-1][1])
    src = re.search(r"url\((https://[^)]+\.woff2)\)", body)
    if not src:
        print(f"{spec}: FAIL no woff2 in the CSS")
        continue
    name = f"{fam.lower().replace(' ', '-')}-{'italic-' if italic else ''}{weight}.woff2"
    open(os.path.join(a.out, name), "wb").write(get(src.group(1)))
    css_out.append(f"@font-face {{ font-family: '{fam}'; src: url('{a.out}/{name}') format('woff2'); "
                   f"font-weight: {weight}; font-style: {'italic' if italic else 'normal'}; }}")
    print(f"{spec}: {a.out}/{name}")
print("\n" + "\n".join(css_out))
