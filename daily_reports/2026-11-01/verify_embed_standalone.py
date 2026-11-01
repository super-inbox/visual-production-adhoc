# -*- coding: utf-8 -*-
"""独立验证脚本：禁止 import gen_reports_v2/v3（它们被 import 会重写报告）。
原理：备份 HTML（外链版）与新 HTML（内嵌版）由同一 CASES 顺序生成，
第 i 个 a.shot 的 assets/aNNN ↔ 第 i 个 data URI 一一对应。
assets/aNNN 本身就是原图的逐字节副本，可直接当原图基准。
"""
import os, re, io, base64
from PIL import Image, ImageOps
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
B = "backup-html-py-before-embed-20261029"
SHOT_RE = re.compile(r'<a class="shot" href="([^"]*)" data-cap="[^"]*"><span class="ph"><img loading="lazy" src="([^"]*)"')

def shots_old(html):
    return [(m.group(1), m.group(2)) for m in SHOT_RE.finditer(html)]

def uris_new(html):
    return re.findall(r'<img loading="lazy" src="(data:image/\w+;base64,[A-Za-z0-9+/=]+)"', html)

def flatten(im):
    o = ImageOps.exif_transpose(im)
    o.load()
    rgba = o.convert("RGBA")
    bg = Image.new("RGB", rgba.size, (255, 255, 255))
    bg.paste(rgba, mask=rgba.getchannel("A"))
    return bg

def ref_for(p, size):
    ref = flatten(Image.open(p)).resize(size, Image.LANCZOS)
    return np.asarray(ref, dtype=np.float64)

results = []
worst = []
os.makedirs("verify_out", exist_ok=True)
for f in sorted(os.listdir(".")):
    if not (f.startswith("report-") and f.endswith(".html")):
        continue
    old = shots_old(open(os.path.join(B, f), encoding="utf-8").read())
    new = uris_new(open(f, encoding="utf-8").read())
    assert len(old) == len(new), (f, len(old), len(new))
    psnrs = []
    for (href, src), uri in zip(old, new):
        assert src == href and src.startswith("assets/"), (f, src, href)
        ap = os.path.join(HERE, src.replace("/", os.sep))
        m, b = re.match(r"data:(image/\w+);base64,([A-Za-z0-9+/=]+)", uri).groups()
        emb = Image.open(io.BytesIO(base64.b64decode(b)))
        emb.load()
        arr_new = np.asarray(emb.convert("RGB"), dtype=np.float64)
        arr_ref = ref_for(ap, emb.size)
        mse = ((arr_ref - arr_new) ** 2).mean()
        psnr = 10 * np.log10(255.0 ** 2 / mse)
        psnrs.append(psnr)
        results.append((f, src, emb.size, psnr))
        worst.append((psnr, f, src, emb.size))
    print("%s: %d imgs, PSNR min=%.1f mean=%.1f max=%.1f" %
          (f, len(psnrs), min(psnrs), sum(psnrs)/len(psnrs), max(psnrs)))

worst.sort()
print("--- 全部 77 张里 PSNR 最低的 5 张（压缩损伤最大，重点亲眼看） ---")
for psnr, f, src, size in worst[:5]:
    print("  %.1fdB  %s %s %s" % (psnr, f, src, size))
    # 把内嵌图和 1:1 中心裁切导出，供亲眼验收
    m, b = None, None
    new = uris_new(open(f, encoding="utf-8").read())
    old = shots_old(open(os.path.join(B, f), encoding="utf-8").read())
    idx = [s for _, s in old].index(src)
    m, b = re.match(r"data:(image/\w+);base64,([A-Za-z0-9+/=]+)", new[idx]).groups()
    emb = Image.open(io.BytesIO(base64.b64decode(b))).convert("RGB")
    stem = os.path.splitext(src)[1 and 0] or src  # aNNN
    name = src.replace("assets/", "").replace(".", "_")
    emb.save(os.path.join("verify_out", "%s_full.png" % name))
    w, h = emb.size
    cw, ch = min(600, w), min(600, h)
    emb.crop(((w-cw)//2, (h-ch)//2, (w+cw)//2, (h+ch)//2)).save(
        os.path.join("verify_out", "%s_center600.png" % name))
    print("    导出: verify_out/%s_full.png + _center600.png(1:1)" % name)
