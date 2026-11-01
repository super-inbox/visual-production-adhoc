# -*- coding: utf-8 -*-
"""v3 任务报告生成器 —— 设计版（2026-10-28 v2 被判"裸html"后按印刷编辑体系重写）。

v2 → v3 的设计变化（版式体系重做，不是换皮）：
- 深色 masthead 封面：报告编号（№ 05 / 08）+ 大标题 + 判定印章 + Georgia 大数字统计条。
- 版面从"圆角卡片墙"改为印刷式 hairline 网格：区块用细线与留白分隔，不再到处描框圆角。
- 色彩纪律：暖纸底 + 墨色 + 单一强调色（氧化红）；verdict 色只出现在 chip/印章。
- 排印：kicker 小字距大写标签、标题 50px、评分/编号用 Georgia 衬线数字、Fig 编号图注。
- QA 规则表改为行式清单（细线分隔、无表格框）；rubric 为细条形 + 64px 大数字评分卡。
- 判定段为墨线框面板 + 双列偏差披露；index 为杂志目录式 TOC 行。
数据层原样 import 自 gen_reports_v2.py（CASES 结论一字未动）。
用法：python gen_reports_v3.py [key ...]   # 无参 = 全部 8 份 + index
"""
import os, sys, base64, io

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gen_reports_v2 as v2  # noqa: E402  (import 即完成 assets 复制与 CASES 数据装载)

CASES = v2.CASES
OUTDIR = v2.OUTDIR

# ---------- 图片内嵌（2026-10-29 用户令：HTML 单文件交付，图片重编码压小后 base64 内嵌） ----------
# 原始 assets/ 复制行为保留不动（assets/ 仍是全分辨率原图，整文件夹搬运那份不受影响）；
# HTML 里内嵌的是压缩副本：长边 ≤ EMBED_MAXEDGE，JPEG q85（带透明通道的图保留 PNG）。
from PIL import Image, ImageOps

EMBED = True
EMBED_MAXEDGE = 2000
EMBED_JPEG_Q = 85
_uris = {}


def data_uri(p):
    if p in _uris:
        return _uris[p]
    im = ImageOps.exif_transpose(Image.open(p))
    im.load()
    # ComfyUI RGBA 输出的 alpha 通道是解码噪声（<250 像素占比 ≤0.01%，肉眼不可见），
    # 按"alpha<250 像素占比 ≥1%"判真透明才保留 PNG，其余白底合成压 JPEG（实测能小 ~10 倍）。
    has_alpha = im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info)
    if has_alpha:
        a = im.convert("RGBA").getchannel("A")
        if a.getextrema()[0] >= 250:
            has_alpha = False
        else:
            hist = a.histogram()
            has_alpha = sum(hist[:250]) / a.size[0] / a.size[1] >= 0.01
    w, h = im.size
    scale = EMBED_MAXEDGE / float(max(w, h))
    if scale < 1:
        im = im.resize((max(1, round(w * scale)), max(1, round(h * scale))), Image.LANCZOS)
    buf = io.BytesIO()
    if has_alpha:
        im.save(buf, "PNG", optimize=True)
        mime = "image/png"
    else:
        rgba = im.convert("RGBA")
        flat = Image.new("RGB", rgba.size, (255, 255, 255))
        flat.paste(rgba, mask=rgba.getchannel("A"))
        kw = dict(quality=EMBED_JPEG_Q, optimize=True, progressive=True)
        icc = im.info.get("icc_profile")
        if icc:
            kw["icc_profile"] = icc
        flat.save(buf, "JPEG", **kw)
        mime = "image/jpeg"
    uri = "data:%s;base64,%s" % (mime, base64.b64encode(buf.getvalue()).decode("ascii"))
    _uris[p] = uri
    return uri

# ---------- CSS / JS（普通字符串） ----------
CSS = """
:root{--paper:#f6f3ed;--ink:#171410;--mut:#6f675a;--line:rgba(23,20,16,.16);--line2:rgba(23,20,16,.55);
--wash:#ece7dc;--acc:#ac3a20;
--pass:#2e5e41;--dev:#8f6410;--fail:#9c2f1f;--todo:#4a4463}
*{box-sizing:border-box}
html{-webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility}
body{margin:0;background:var(--paper);color:var(--ink);font:15.5px/1.85 "Microsoft YaHei","PingFang SC","Segoe UI",system-ui,sans-serif}
a{color:inherit}
::selection{background:var(--acc);color:#fff}
.wrap{max-width:1200px;margin:0 auto;padding:0 44px}
/* ---------- masthead ---------- */
.mast{background:var(--ink);color:var(--paper)}
.mast .wrap{padding-top:48px;position:relative}
.kick{display:flex;justify-content:space-between;align-items:baseline;gap:20px;font-size:11px;letter-spacing:.22em;text-transform:uppercase;color:rgba(246,243,237,.6)}
.kick b{color:var(--paper);font-weight:400}
.mast h1{font-size:50px;line-height:1.2;letter-spacing:.01em;margin:24px 0 18px;font-weight:700;max-width:880px}
.stand{display:flex;flex-wrap:wrap;gap:8px 10px;align-items:center;font-size:13px;color:rgba(246,243,237,.72);margin-bottom:44px}
.stand .dir{margin-right:10px;font-family:Georgia,serif;letter-spacing:.02em}
.chip{font-size:12px;font-weight:600;padding:3px 11px;border:1px solid;border-radius:2px;letter-spacing:.05em;white-space:nowrap}
.chip.pass{background:rgba(46,94,65,.1);color:#24523a;border-color:rgba(46,94,65,.4)}
.chip.dev{background:rgba(143,100,16,.1);color:#7d5710;border-color:rgba(143,100,16,.4)}
.chip.fail{background:rgba(156,47,31,.08);color:#8a2c1e;border-color:rgba(156,47,31,.4)}
.chip.todo{background:rgba(74,68,99,.08);color:#443e63;border-color:rgba(74,68,99,.35)}
.mast .chip{background:transparent}
.mast .chip.pass{color:#9ecfad;border-color:rgba(158,207,173,.5)}
.mast .chip.dev{color:#e3c47a;border-color:rgba(227,196,122,.5)}
.mast .chip.fail{color:#e79a8a;border-color:rgba(231,154,138,.5)}
.mast .chip.todo{color:#b9b4dd;border-color:rgba(185,180,221,.5)}
.seal{position:absolute;right:44px;top:96px;transform:rotate(-2deg);border:2px solid rgba(246,243,237,.9);outline:1px solid rgba(246,243,237,.45);outline-offset:5px;padding:13px 24px 11px;text-align:center;color:var(--paper)}
.seal .w{font-family:Georgia,serif;font-size:25px;letter-spacing:.14em;white-space:nowrap}
.seal .z{font-size:10.5px;letter-spacing:.42em;margin-top:5px;color:rgba(246,243,237,.6);margin-right:-.42em}
.stats{display:grid;grid-template-columns:repeat(4,1fr);border-top:1px solid rgba(246,243,237,.28);margin-top:8px}
.stats .cell{padding:18px 22px 26px;border-left:1px solid rgba(246,243,237,.28)}
.stats .cell:first-child{border-left:none;padding-left:0}
.stats .k{font-size:10.5px;letter-spacing:.22em;text-transform:uppercase;color:rgba(246,243,237,.5)}
.stats .v{font-family:Georgia,serif;font-size:22px;margin-top:7px;line-height:1.4}
.stats .v small{font-size:13px;color:rgba(246,243,237,.62);font-family:"Microsoft YaHei",sans-serif;margin-left:6px}
.stats .v.txt{font-size:14px;font-family:"Microsoft YaHei",sans-serif}
/* ---------- nav ---------- */
.nav{position:sticky;top:0;z-index:40;background:rgba(246,243,237,.9);backdrop-filter:blur(10px);border-bottom:1px solid var(--line)}
.nav .wrap{display:flex;align-items:center;gap:28px;height:52px;padding-top:0;padding-bottom:0}
.brand{font-size:11.5px;letter-spacing:.2em;text-transform:uppercase;white-space:nowrap}
.brand b{color:var(--acc);font-weight:400}
.nav .lk{display:flex;gap:22px;font-size:13px;color:var(--mut)}
.nav .lk a{text-decoration:none}
.nav .lk a:hover{color:var(--ink)}
.nav .ix{margin-left:auto;font-size:12.5px;color:var(--mut);text-decoration:none;white-space:nowrap}
.nav .ix:hover{color:var(--ink)}
/* ---------- sections ---------- */
section{padding:56px 0 62px;border-bottom:1px solid var(--line)}
section:last-of-type{border-bottom:0}
.sh{display:flex;align-items:baseline;gap:18px;margin-bottom:30px}
.sh .no{font-family:Georgia,serif;font-size:16px;color:var(--acc);letter-spacing:.06em}
.sh h2{font-size:27px;margin:0;font-weight:700;letter-spacing:.01em}
.sh .en{margin-left:auto;font-size:10.5px;letter-spacing:.3em;text-transform:uppercase;color:var(--mut);white-space:nowrap}
.prose{max-width:900px}
.prose p{margin:0 0 15px}
.prose .bad{color:var(--fail);font-weight:600}.prose .warn{color:var(--dev);font-weight:600}.prose .ok{color:var(--pass);font-weight:600}
/* ---------- galleries ---------- */
.lab{display:flex;align-items:center;gap:14px;margin:38px 0 16px;font-size:11.5px;letter-spacing:.24em;text-transform:uppercase;color:var(--mut)}
.lab .r{flex:1;height:1px;background:var(--line)}
.gal{display:grid;gap:18px}
.g2{grid-template-columns:repeat(2,1fr)}.g3{grid-template-columns:repeat(3,1fr)}.g4{grid-template-columns:repeat(4,1fr)}
.shot{display:block;text-decoration:none;border:1px solid var(--line);background:#fff}
.shot:hover{border-color:var(--line2)}
.shot .ph{aspect-ratio:3/4;background:var(--wash);display:flex;align-items:center;justify-content:center;overflow:hidden}
.shot .ph img{max-width:100%;max-height:100%;width:auto;height:auto;object-fit:contain;display:block}
.shot .cap{display:block;padding:9px 13px 10px;font-size:12.5px;line-height:1.6;color:#4a443a;border-top:1px solid var(--line);background:#fff}
.shot .cap b.fn{font-family:Georgia,serif;color:var(--acc);font-weight:400;margin-right:9px;font-size:12px;letter-spacing:.04em}
/* ---------- rework log ---------- */
.rw{max-width:1120px}
.rrow{display:grid;grid-template-columns:250px 1fr 130px;gap:26px;padding:18px 0;border-top:1px solid var(--line);align-items:start}
.rrow:last-child{border-bottom:1px solid var(--line)}
.rstep .rn{font-size:14px;font-weight:700;line-height:1.7}
.rbody p{margin:0;font-size:13.5px;color:#514b40;line-height:1.9}
.rst{justify-self:end}
.rwhint{max-width:900px;font-size:12px;color:var(--mut);margin:12px 0 0}
/* ---------- QA 行式清单 ---------- */
.qanote{max-width:900px;font-size:13px;color:var(--mut);margin-bottom:20px}
.qa{border-top:1px solid var(--line);padding:20px 0;display:grid;grid-template-columns:290px 1fr 160px;gap:26px;max-width:1120px}
.qa:last-of-type{border-bottom:1px solid var(--line)}
.qa .rule{font-weight:700;font-size:14.5px;line-height:1.65}
.qa .basis{font-size:11.5px;color:var(--mut);margin-top:9px;line-height:1.6}
.qa .ev{font-size:13.5px;color:#514b40;line-height:1.9}
.qa .st{justify-self:end}
.vchip{font-size:11.5px;font-weight:700;padding:4px 11px;border:1px solid;border-radius:2px;white-space:nowrap;letter-spacing:.08em}
.vchip.pass{color:var(--pass);border-color:rgba(46,94,65,.55);background:rgba(46,94,65,.06)}
.vchip.dev{color:var(--dev);border-color:rgba(143,100,16,.55);background:rgba(143,100,16,.06)}
.vchip.fail{color:var(--fail);border-color:rgba(156,47,31,.55);background:rgba(156,47,31,.06)}
.vchip.todo{color:var(--todo);border-color:rgba(74,68,99,.5);background:rgba(74,68,99,.06)}
/* ---------- rubric ---------- */
.rubric{display:grid;grid-template-columns:1fr 350px;gap:52px;margin-top:46px;max-width:1120px;align-items:start}
.bars .row{display:grid;grid-template-columns:225px 1fr 36px;gap:16px;align-items:center;padding:9px 0;border-top:1px solid var(--line);font-size:13.5px}
.bars .nm b{font-weight:600}
.bars .nm .wt{color:var(--mut);font-size:11px;margin-left:7px;font-family:Georgia,serif}
.bars .track{display:block;background:var(--wash);height:7px;position:relative}
.bars .fill{display:block;height:100%;background:var(--ink)}
.bars .val{font-family:Georgia,serif;text-align:right;font-size:15px}
.dimwhy{margin-top:16px;font-size:12.5px;color:var(--mut)}
.dimwhy summary{cursor:pointer;letter-spacing:.06em}
.dimwhy div{margin-top:10px;line-height:1.9}
.dimwhy b{color:#514b40;font-weight:600}
.scorecard{border:1.5px solid var(--ink);padding:24px 28px 22px;background:rgba(255,255,255,.35)}
.scorecard .k{font-size:10.5px;letter-spacing:.24em;text-transform:uppercase;color:var(--mut)}
.scorecard .v{font-family:Georgia,serif;font-size:62px;line-height:1.05;margin:10px 0 6px}
.scorecard .v.zh{font-size:15px;font-family:"Microsoft YaHei",sans-serif;line-height:1.75;font-weight:600}
.scorecard .g{font-size:12px;color:var(--mut);line-height:1.75}
.scorecard+.scorecard{margin-top:16px}
/* ---------- verdict ---------- */
.verdict{border:1.5px solid var(--ink);padding:32px 36px 28px;max-width:1120px;position:relative;background:rgba(255,255,255,.35)}
.verdict .vtag{position:absolute;top:-10px;left:28px;background:var(--paper);padding:0 14px;font-size:10.5px;letter-spacing:.3em;text-transform:uppercase;color:var(--acc)}
.verdict .vtitle{font-size:21px;font-weight:700;margin-bottom:14px;line-height:1.5}
.verdict p{margin:0 0 13px;font-size:14.5px;line-height:1.9}
.verdict p:last-child{margin-bottom:0}
.devlist{margin:10px 0 0;padding-left:0;list-style:none;columns:2;column-gap:44px}
.devlist li{margin-bottom:8px;break-inside:avoid;padding-left:18px;position:relative;font-size:13.5px;color:#514b40}
.devlist li:before{content:"—";position:absolute;left:0;color:var(--acc)}
/* ---------- footer ---------- */
footer{margin-top:72px;border-top:1px solid var(--line2);padding:20px 0 64px;font-size:12px;color:var(--mut);line-height:2.05}
footer .fm{font-family:Georgia,serif;letter-spacing:.16em;text-transform:uppercase;font-size:10.5px;color:var(--ink);display:block;margin-bottom:6px}
/* ---------- index TOC ---------- */
.toc{border-top:1px solid var(--line2);margin-top:52px}
.trow{display:grid;grid-template-columns:56px 78px 1fr 320px 96px;gap:22px;align-items:center;padding:17px 0;border-bottom:1px solid var(--line);text-decoration:none}
.trow:hover{background:rgba(23,20,16,.035)}
.trow .no{font-family:Georgia,serif;font-size:21px;color:var(--acc)}
.trow .th{width:78px;height:98px;background:var(--wash);border:1px solid var(--line);display:flex;align-items:center;justify-content:center;overflow:hidden}
.trow .th img{max-width:100%;max-height:100%;width:auto;height:auto;object-fit:contain;display:block}
.trow .tt b{font-size:16.5px;display:block;line-height:1.5}
.trow .tt b .k2{color:var(--acc);font-family:Georgia,serif;font-weight:400;margin-right:10px}
.trow .tt span{font-size:12.5px;color:var(--mut);font-family:Georgia,serif}
.trow .tc{display:flex;flex-wrap:wrap;gap:6px;justify-content:flex-end}
.trow .sc{font-family:Georgia,serif;font-size:30px;text-align:right;line-height:1}
.trow .sc small{display:block;font-family:"Microsoft YaHei",sans-serif;font-size:9.5px;color:var(--mut);letter-spacing:.22em;text-transform:uppercase;margin-top:7px}
/* ---------- lightbox ---------- */
#lb{position:fixed;inset:0;background:rgba(13,11,9,.95);display:none;z-index:100;flex-direction:column;align-items:center;justify-content:center}
#lb.on{display:flex}
#lb img{max-width:92vw;max-height:84vh;box-shadow:0 24px 90px rgba(0,0,0,.55)}
#lb-cap{color:#d6d3d1;font-size:13.5px;margin-top:16px;max-width:78vw;text-align:center;line-height:1.6}
#lb-x{position:absolute;top:14px;right:28px;color:#a8a29e;font-size:30px;cursor:pointer}
#lb-prev,#lb-next{position:absolute;top:50%;transform:translateY(-50%);color:#a8a29e;font-size:44px;cursor:pointer;user-select:none;padding:24px}
#lb-prev{left:16px}#lb-next{right:16px}
#lb-prev:hover,#lb-next:hover,#lb-x:hover{color:#fff}
@media (max-width:1000px){.gal.g3,.gal.g4{grid-template-columns:repeat(2,1fr)}.rubric{grid-template-columns:1fr}.wrap{padding:0 20px}.seal{display:none}.trow{grid-template-columns:40px 1fr 80px}}
"""

JS = """
(function(){
var lb=document.getElementById('lb'),img=document.getElementById('lb-img'),cap=document.getElementById('lb-cap');
var list=[],idx=0;
function render(){var a=list[idx];if(!a)return;img.src=a.querySelector('.ph img').src;cap.innerHTML=a.getAttribute('data-cap')||'';lb.classList.add('on');}
function openLb(a){list=[].slice.call(a.closest('.gal').querySelectorAll('a.shot'));idx=list.indexOf(a);render();}
function step(d){if(!list.length)return;idx=(idx+d+list.length)%list.length;render();}
document.addEventListener('click',function(e){
  var t=e.target;
  var a=t.closest?t.closest('a.shot'):null;
  if(a){e.preventDefault();openLb(a);return;}
  if(t.closest&&t.closest('#lb-next')){step(1);return;}
  if(t.closest&&t.closest('#lb-prev')){step(-1);return;}
  if(t.id==='lb-x'||t.id==='lb'){lb.classList.remove('on');}
});
document.addEventListener('keydown',function(e){
  if(!lb.classList.contains('on'))return;
  if(e.key==='Escape')lb.classList.remove('on');
  else if(e.key==='ArrowRight')step(1);
  else if(e.key==='ArrowLeft')step(-1);
});
})();
"""

LIGHTBOX = ('<div id="lb"><span id="lb-x">&times;</span><span id="lb-prev">&#8249;</span>'
            '<span id="lb-next">&#8250;</span><img id="lb-img" alt=""><div id="lb-cap"></div></div>')

SEAL_WORD = {"pass": ("PASS", "合格"), "dev": ("PASS·DEV", "合格·偏差"),
             "fail": ("FAIL", "不合格"), "todo": ("REVIEW", "待复核")}


def shot(src, cap, fig):
    p = v2.asset_path(src)
    if not os.path.exists(p):
        raise SystemExit("MISSING ASSET: " + p)
    v2.asset(src)  # 保留原行为：原图随包复制进 assets/
    uri = data_uri(p) if EMBED else v2.asset(src)
    return ('<a class="shot" href="#" data-cap="%s"><span class="ph"><img loading="lazy" src="%s" alt=""></span>'
            '<span class="cap"><b class="fn">%s</b>%s</span></a>'
            % (cap.replace('"', '&quot;'), uri, fig, cap))


def gal(items, cols, figstart):
    cls = {2: "g2", 3: "g3", 4: "g4"}[cols]
    out = []
    for i, (s, c) in enumerate(items):
        out.append(shot(s, c, "Fig.%02d" % (figstart + i)))
    return '<div class="gal %s">%s</div>' % (cls, "".join(out)), figstart + len(items)


def qa_rows(rows):
    out = []
    for (rule, ev, res, basis) in rows:
        label, kind = res
        out.append(
            '<div class="qa"><div><div class="rule">%s</div><div class="basis">%s</div></div>'
            '<div class="ev">%s</div><div class="st"><span class="vchip %s">%s</span></div></div>'
            % (rule, basis, ev, kind, label))
    return "".join(out)


def rework_log(rows):
    badge = {"fail": ("缺陷", "fail"), "dev": ("部分修复", "dev"), "pass": ("闭环", "pass")}
    out = []
    for (step, body, kind) in rows:
        label, cls = badge[kind]
        out.append('<div class="rrow"><div class="rstep"><span class="rn">%s</span></div>'
                   '<div class="rbody"><p>%s</p></div>'
                   '<div class="rst"><span class="vchip %s">%s</span></div></div>'
                   % (step, body, cls, label))
    return ('<div class="lab"><span>返工与优化记录 · Rework Log</span><span class="r"></span></div>'
            '<div class="rw">%s</div>'
            '<p class="rwhint">口径：每轮 = 识别缺陷 &#8594; 改 prompt/条款/seed &#8594; 重跑 &#8594; 特写复验；一次通过的 take 不列。seed/哈希全量见 spec.json / meta.json。</p>'
            % "".join(out))


def rubric(dims, total, gated):
    rows = []
    for name, weight, sc, why in dims:
        pct = int(sc / 5 * 100)
        rows.append('<div class="row"><span class="nm"><b>%s</b><span class="wt">%d%%</span></span>'
                    '<span class="track"><span class="fill" style="width:%d%%"></span></span>'
                    '<span class="val">%d</span></div>' % (name, weight, pct, sc))
    whys = "".join('<div><b>%s</b> — %s</div>' % (n, w) for n, _, _, w in dims)
    return ('<div class="rubric"><div class="bars">%s'
            '<details class="dimwhy"><summary>各维度评分依据（逐条）</summary><div>%s</div></details></div>'
            '<div><div class="scorecard"><div class="k">Quality Score</div><div class="v">%s</div>'
            '<div class="g">统一 rubric 八维度加权归一 · design-agent-v0/eval/rubrics/unified-design-agent-rubric-v0.1.md（agentic-adhoc 仓库）</div></div>'
            '<div class="scorecard"><div class="k">Gated Score</div><div class="v zh">%s</div></div></div></div>'
            % ("".join(rows), whys, total, gated))


def mast(c, no, total):
    sw, sz = SEAL_WORD.get(c["vkind"], ("REVIEW", "待复核"))
    key, _, zh = c["title"].partition(" · ")
    chips = "".join('<span class="chip %s">%s</span>' % (k, t) for t, k in c["chips"])
    return f"""<header class="mast"><div class="wrap">
<div class="kick"><span>Fashion Try-on Benchmark · Task Report</span><span>Report <b>&#8470; {no:02d} / {total:02d}</b></span></div>
<h1>{zh}</h1>
<div class="stand"><span class="dir">{key}</span><span class="dir">{c['dir']}</span>{chips}</div>
<div class="seal"><div class="w">{sw}</div><div class="z">{sz}</div></div>
<div class="stats">
<div class="cell"><div class="k">Outputs</div><div class="v">{len(c['outputs'])}<small>张成品</small></div></div>
<div class="cell"><div class="k">Close-ups</div><div class="v">{len(c['crops'])}<small>张验收特写</small></div></div>
<div class="cell"><div class="k">Quality Score</div><div class="v">{c['score']}<small>/ 1.00</small></div></div>
<div class="cell"><div class="k">Case Directory</div><div class="v txt">{c['dir']}</div></div>
</div>
</div></header>"""


def report(c, no, total):
    _fig = [1]

    def g(items, cols):
        out, nxt = gal(items, cols, _fig[0])
        _fig[0] = nxt
        return out

    navlinks = "".join('<a href="#p%d">%s</a>' % (i + 1, t) for i, t in
                       enumerate(["任务与需求", "做法", "输入与产出", "QA 质检", "合格判定"]))
    inp_html = g(c['inputs'], 4)
    out_html = g(c['outputs'], 3)
    crops_html = ('<div class="lab"><span>验收特写 · 关键区 2-3&#215; 放大</span><span class="r"></span></div>'
                  + g(c['crops'], 4)) if c['crops'] else ''
    rw_html = rework_log(c['rework']) if c.get('rework') else ''
    return f"""<!DOCTYPE html><html lang="zh"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{c['title']} · 任务报告</title><style>{CSS}</style></head><body>
<nav class="nav"><div class="wrap"><span class="brand">FT<b>/</b>B · 任务报告</span><span class="lk">{navlinks}</span></div></nav>
{mast(c, no, total)}
<div class="wrap">
<section id="p1"><div class="sh"><span class="no">01</span><h2>任务是什么 · 客户需求 · 做到什么程度</h2><span class="en">Task &amp; Brief</span></div><div class="prose">{c['s1']}</div></section>
<section id="p2"><div class="sh"><span class="no">02</span><h2>怎么做的</h2><span class="en">Method</span></div><div class="prose">{c['s2']}</div>{rw_html}</section>
<section id="p3"><div class="sh"><span class="no">03</span><h2>输入与产出可视化</h2><span class="en">Visual Record</span></div>
<div class="lab"><span>输入 · 客户 brief 引用图</span><span class="r"></span></div>
{inp_html}
<div class="lab"><span>产出 · 成品图（点开看原图，左右方向键翻张）</span><span class="r"></span></div>
{out_html}
{crops_html}
</section>
<section id="p4"><div class="sh"><span class="no">04</span><h2>按本任务 QA 规则质检</h2><span class="en">QA &amp; Scoring</span></div>
<div class="qanote">任务级明文规则逐条核验 + 统一 rubric 八维度评分。及格线：hard gates 全过且 quality_score &#8805; 0.70。结论全部来自直接读图实测（find-defects-first + 关键区 2-3&#215; 特写），推断均已标注。</div>
{qa_rows(c['qa'])}
{rubric(c['dims'], c['score'], c['gated'])}
</section>
<section id="p5"><div class="sh"><span class="no">05</span><h2>合格判定</h2><span class="en">Verdict</span></div>
<div class="verdict"><span class="vtag">Final Verdict</span><div class="vtitle">{c['vtitle']}</div>{c['vbody']}</div>
</section>
<footer><span class="fm">Fashion Try-on Benchmark — Task Report &#8470;{no:02d}</span>
数据来源：本目录 gen_reports_v3.py（版式 v3，判定/QA/评分数据原样取自 v1/v2，未改动结论）· 各 case spec/meta.json（模型/prompt/seed/输入输出哈希）· 工作文档 2026-10-27_各图生成过程与代码清单_工作文档.md。<br>
benchmark 红线：client-brief/ 字节不动 · 不虚构缺失数据 · 历史生成结果不作输入参考 · 参考对标图（不可直接用）从未喂给任何模型。</footer>
</div>
{LIGHTBOX}
<script>{JS}</script>
</body></html>"""


# ---------- 生成（2026-10-28 用户令：一个 HTML=一份子报告，不搞总览页，index_page 已删） ----------
if __name__ == "__main__":
    keys = sys.argv[1:]
    targets = [c for c in CASES if not keys or c["key"] in keys]
    for c in targets:
        no = CASES.index(c) + 1
        p = os.path.join(OUTDIR, "report-%s.html" % c["key"])
        open(p, "w", encoding="utf-8").write(report(c, no, len(CASES)))
        print("written:", p)
