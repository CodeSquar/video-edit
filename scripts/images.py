#!/usr/bin/env python3
"""Find, fetch and cut real images without writing search/download code.

  python images.py search "query one" "query two" [--n 10] [--min 700]
      one compact line per hit: W×H  image-url  | title | page   (hits under --min px on the long side dropped)
  python images.py get DIR URL NAME [URL NAME ...]
      parallel download with a browser UA; checks it really is an image (an HTML page is searched for its
      og:image and that is fetched instead); prints NAME W×H or why it failed
  python images.py cut SRC OUT.webp [--box x0,y0,x1,y1] [--w 1600] [--q 88]
      crop (source px) / resize / save as webp for assets/img/
  python images.py sheet DIR [--out DIR]
      a local folder as labelled contact sheets (up to 64 per jpg, bigger cells when there are few) + one line per file: index name W×H

Needs `pip install ddgs pillow`. Look at a downloaded file before using it; this only filters.
"""
import argparse, concurrent.futures as cf, io, os, re, subprocess, sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"


def fetch(url):
    """curl, not urllib: Python's certificate store on some machines rejects valid hosts."""
    r = subprocess.run(["curl", "-sSfL", "-m", "30", "-A", UA, "-H", "Accept: image/*,*/*;q=0.8", url],
                       capture_output=True)
    if r.returncode:
        raise RuntimeError(r.stderr.decode("utf-8", "replace").strip())
    return r.stdout, ""


def search(a):
    from ddgs import DDGS
    with DDGS() as d:
        for q in a.queries:
            print("##", q)
            try:
                hits = d.images(q, max_results=a.n, size="Large")
            except Exception as e:
                print("  search failed:", e)
                continue
            for h in hits:
                w, ht = int(h.get("width") or 0), int(h.get("height") or 0)
                if max(w, ht) and max(w, ht) < a.min:
                    continue
                print(f"  {w}×{ht}  {h['image']}  | {(h.get('title') or '')[:60]} | {h.get('url', '')[:80]}")


def get_one(dir_, url, name):
    from PIL import Image
    try:
        data, _ = fetch(url)
        if b"<html" in data[:2000].lower() or b"<!doctype" in data[:200].lower():
            m = re.search(rb'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)', data) or \
                re.search(rb'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image', data)
            if not m:
                return f"{name}: FAIL got an HTML page with no og:image"
            data, _ = fetch(m.group(1).decode())
        im = Image.open(io.BytesIO(data))
        im.load()
        path = os.path.join(dir_, name)
        open(path, "wb").write(data)
        return f"{name}: {im.width}×{im.height} {im.format}"
    except Exception as e:
        return f"{name}: FAIL {str(e)[:120]}"


def get(a):
    os.makedirs(a.dir, exist_ok=True)
    pairs = list(zip(a.items[::2], a.items[1::2]))
    with cf.ThreadPoolExecutor(8) as ex:
        for line in ex.map(lambda p: get_one(a.dir, *p), pairs):
            print(line)


def cut(a):
    from PIL import Image
    im = Image.open(a.src).convert("RGB")
    if a.box:
        im = im.crop(tuple(int(v) for v in a.box.split(",")))
    if a.w and im.width > a.w:
        im = im.resize((a.w, round(im.height * a.w / im.width)), Image.LANCZOS)
    im.save(a.out, "WEBP", quality=a.q)
    print(f"{a.out}: {im.width}×{im.height}")


def sheet(a):
    """Contact sheets of a local folder: one Read shows every image, each labelled with its index."""
    import math, tempfile, warnings
    from PIL import Image, ImageDraw
    warnings.filterwarnings("ignore")
    exts = (".jpg", ".jpeg", ".png", ".webp", ".gif", ".jfif", ".avif", ".bmp")
    files = sorted(f for f in os.listdir(a.dir) if f.lower().endswith(exts))
    per = 64
    out_dir = a.out or tempfile.gettempdir()
    rows_txt, paths = [], []
    for k in range(0, len(files), per):
        chunk = files[k:k + per]
        # near-square grid ~1920 px wide: few images get big cells (4 -> 2x2 of 960), 64 -> 8x8 of 240
        cols = min(8, math.ceil(math.sqrt(len(chunk))))
        cw = 1920 // cols; ch = cw + 20
        im_sheet = Image.new("RGB", (cols * cw, -(-len(chunk) // cols) * ch), "white")
        d = ImageDraw.Draw(im_sheet)
        for j, f in enumerate(chunk):
            i, x, y = k + j, (j % cols) * cw, (j // cols) * ch
            try:
                im = Image.open(os.path.join(a.dir, f))
                size = f"{im.width}x{im.height}"
                im = im.convert("RGB"); im.thumbnail((cw - 10, ch - 30))
                im_sheet.paste(im, (x + 5, y + 5))
            except Exception:
                size = "unreadable"
            d.rectangle((x, y + ch - 24, x + cw, y + ch), fill="white")
            d.text((x + 5, y + ch - 22), f"{i} {f[:26]}", fill="black")
            rows_txt.append(f"{i} {f} {size}")
        p = os.path.join(out_dir, f"sheet-{k // per + 1}.jpg")
        im_sheet.save(p, quality=80); paths.append(p)
    print("\n".join(rows_txt))
    print("sheets (Read all in one message): " + ", ".join(paths))


ap = argparse.ArgumentParser()
sub = ap.add_subparsers(dest="cmd", required=True)
s = sub.add_parser("search"); s.add_argument("queries", nargs="+"); s.add_argument("--n", type=int, default=10)
s.add_argument("--min", type=int, default=700); s.set_defaults(f=search)
g = sub.add_parser("get"); g.add_argument("dir"); g.add_argument("items", nargs="+"); g.set_defaults(f=get)
c = sub.add_parser("cut"); c.add_argument("src"); c.add_argument("out"); c.add_argument("--box")
c.add_argument("--w", type=int, default=1600); c.add_argument("--q", type=int, default=88); c.set_defaults(f=cut)
h = sub.add_parser("sheet"); h.add_argument("dir"); h.add_argument("--out"); h.set_defaults(f=sheet)
a = ap.parse_args()
a.f(a)
