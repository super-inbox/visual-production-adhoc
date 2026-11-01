# -*- coding: utf-8 -*-
"""v2 任务报告生成器 —— 编辑风版式重做（2026-10-28 用户否决 v1 后重写）。

与 v1 的差别：
- 图片全部复制进 assets/、路径全相对：整个 reports 文件夹拷到任何位置都能打开（v1 混用 file:/// 绝对路径 + ../../ 相对路径，挪位即裂图）。
- 大图可点开（lightbox 逐张翻看原图），缩略图 contain 不裁切（v1 用 340px cover 把 3:4 图头脚裁掉）。
- QA 从表格墙改成卡片；rubric 评分改成条形图。
- 五段结构不变（用户定的）：①任务与需求 ②做法 ③输入产出可视化 ④QA ⑤判定。
判定/QA/评分数据原样取自 v1 gen_reports.py，未改动任何结论。
"""
import os, shutil

ROOT = "E:/projects/fashion-tryon-benchmark-main/fashion-tryon-benchmark-lfs"
OUTDIR = os.path.join(ROOT, "outputs/task-reports-2026-10-28")
ASSETS = os.path.join(OUTDIR, "assets")
COMFY = "E:/projects/ComfyUI/output"

# ---------- assets：注册即复制，返回相对路径 ----------
_assets = {}

def asset(src):
    if src.startswith("file:///"):
        src = src[len("file:///"):]
    if src.startswith("E:/projects/ComfyUI/output/"):
        p = src
    else:
        p = src if os.path.isabs(src) else os.path.join(ROOT, src)
    p = os.path.normpath(p)
    if p in _assets:
        return _assets[p]
    if not os.path.exists(p):
        raise SystemExit("MISSING ASSET: " + p)
    os.makedirs(ASSETS, exist_ok=True)
    ext = os.path.splitext(p)[1].lower() or ".png"
    name = "a%03d%s" % (len(_assets) + 1, ext)
    shutil.copy2(p, os.path.join(ASSETS, name))
    rel = "assets/" + name
    _assets[p] = rel
    return rel

# ---------- CSS / JS（普通字符串，避免 f-string 花括号转义） ----------
CSS = """
:root{--ink:#1c1917;--mut:#78716c;--line:#e7e5e4;--bg:#faf9f7;--card:#fff;
--pass:#166534;--passbg:#ecfdf5;--dev:#92400e;--devbg:#fffbeb;--fail:#991b1b;--failbg:#fef2f2;--todo:#3730a3;--todobg:#eef2ff}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.8 "Segoe UI","Microsoft YaHei",system-ui,sans-serif;-webkit-font-smoothing:antialiased}
a{color:inherit}
.wrap{max-width:1160px;margin:0 auto;padding:0 40px}
.nav{position:sticky;top:0;z-index:50;background:rgba(250,249,247,.92);backdrop-filter:blur(8px);border-bottom:1px solid var(--line)}
.nav .wrap{display:flex;align-items:center;gap:24px;height:54px;padding-top:0;padding-bottom:0}
.nav .brand{font-weight:700;font-size:14px;letter-spacing:.02em;white-space:nowrap}
.nav .links{display:flex;gap:20px;font-size:13.5px;color:var(--mut);flex-wrap:wrap}
.nav .links a{text-decoration:none;padding:2px 0;border-bottom:2px solid transparent}
.nav .links a:hover{color:var(--ink);border-color:var(--ink)}
.nav .home{margin-left:auto;font-size:13px;color:var(--mut);text-decoration:none;white-space:nowrap}
.nav .home:hover{color:var(--ink)}
.hero{padding:60px 0 34px;border-bottom:1px solid var(--line)}
.eyebrow{font-size:12px;letter-spacing:.16em;text-transform:uppercase;color:var(--mut);font-weight:700}
h1{font-size:36px;line-height:1.25;margin:12px 0 20px;font-weight:700;letter-spacing:-.01em}
.chips{display:flex;flex-wrap:wrap;gap:10px}
.chip{font-size:13px;font-weight:600;padding:6px 14px;border-radius:999px}
.chip.sm{font-size:12px;font-weight:600;padding:2px 10px;border-radius:999px;display:inline-block}
.chip.pass{background:var(--passbg);color:var(--pass)}.chip.dev{background:var(--devbg);color:var(--dev)}
.chip.fail{background:var(--failbg);color:var(--fail)}.chip.todo{background:var(--todobg);color:var(--todo)}
.facts{display:flex;flex-wrap:wrap;gap:10px 34px;margin-top:24px;font-size:13.5px;color:var(--mut)}
.facts b{color:var(--ink);font-weight:600}
section{padding:46px 0;border-bottom:1px solid var(--line)}
section:last-of-type{border-bottom:none}
.sh{display:flex;align-items:baseline;gap:14px;margin-bottom:24px}
.sh .no{font-size:13px;font-weight:700;color:#a8a29e;letter-spacing:.06em}
.sh h2{font-size:22px;margin:0;font-weight:700;letter-spacing:-.01em}
.prose{max-width:880px}
.prose p{margin:0 0 14px}
.prose .bad{color:var(--fail);font-weight:600}.prose .warn{color:var(--dev);font-weight:600}.prose .ok{color:var(--pass);font-weight:600}
h3.lab{font-size:12.5px;letter-spacing:.14em;text-transform:uppercase;color:var(--mut);font-weight:700;margin:30px 0 14px}
.gal{display:grid;gap:16px}
.gal.g2{grid-template-columns:repeat(2,1fr)}.gal.g3{grid-template-columns:repeat(3,1fr)}.gal.g4{grid-template-columns:repeat(4,1fr)}
.shot{background:var(--card);border:1px solid var(--line);border-radius:12px;overflow:hidden;text-decoration:none;display:block;transition:box-shadow .16s,transform .16s}
.shot:hover{box-shadow:0 12px 32px rgba(28,25,23,.12);transform:translateY(-2px)}
.shot .ph{aspect-ratio:3/4;background:#f1efec;display:flex;align-items:center;justify-content:center;overflow:hidden}
.shot .ph img{max-width:100%;max-height:100%;width:auto;height:auto;object-fit:contain;display:block}
.shot .cap{display:block;padding:10px 14px;font-size:13px;color:#44403c;border-top:1px solid var(--line);line-height:1.55}
.qa{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px 20px;margin-bottom:12px;max-width:1020px}
.qa .top{display:flex;align-items:center;gap:12px;flex-wrap:wrap}
.qa .rule{font-weight:650;font-size:15px}
.qa .basis{margin-left:auto;font-size:12px;color:var(--mut)}
.qa .ev{font-size:13.5px;color:#57534e;margin-top:8px;line-height:1.75}
.scorebox{display:grid;grid-template-columns:1fr 300px;gap:36px;max-width:1020px;align-items:start;margin-top:26px}
.bars .row{display:grid;grid-template-columns:200px 1fr 40px;gap:12px;align-items:center;margin-bottom:11px;font-size:13.5px}
.bars .track{display:block;background:#f0eeea;border-radius:999px;height:10px;overflow:hidden}
.bars .fill{display:block;height:100%;border-radius:999px;background:#292524}
.bars .val{font-weight:650;text-align:right;font-variant-numeric:tabular-nums}
.big{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:20px 22px}
.big .k{font-size:11.5px;letter-spacing:.12em;text-transform:uppercase;color:var(--mut);font-weight:700}
.big .v{font-size:36px;font-weight:700;margin-top:6px;line-height:1.1}
.big .g{font-size:12.5px;color:var(--mut);margin-top:10px;line-height:1.6}
.big+.big{margin-top:14px}
details.dimwhy{margin-top:14px;font-size:13px;color:var(--mut)}
details.dimwhy summary{cursor:pointer;font-weight:600}
details.dimwhy div{margin-top:8px;line-height:1.8}
.verdict{border-left:4px solid var(--pass);background:var(--card);border-radius:0 12px 12px 0;padding:24px 28px;max-width:980px;box-shadow:0 1px 3px rgba(0,0,0,.04)}
.verdict.dev{border-color:#d97706}.verdict.fail{border-color:var(--fail)}
.verdict .vtitle{font-size:19px;font-weight:700;margin-bottom:12px}
.verdict p{margin:0 0 12px;font-size:14.5px}
.verdict p:last-child{margin-bottom:0}
.devlist{margin:8px 0 0;padding-left:20px}
.devlist li{margin-bottom:6px}
footer{padding:38px 0 70px;color:var(--mut);font-size:12.5px;line-height:1.9}
#lb{position:fixed;inset:0;background:rgba(15,12,10,.94);display:none;z-index:100;flex-direction:column;align-items:center;justify-content:center}
#lb.on{display:flex}
#lb img{max-width:92vw;max-height:84vh;box-shadow:0 24px 90px rgba(0,0,0,.55)}
#lb-cap{color:#d6d3d1;font-size:13.5px;margin-top:16px;max-width:78vw;text-align:center;line-height:1.6}
#lb-x{position:absolute;top:14px;right:28px;color:#a8a29e;font-size:30px;cursor:pointer}
#lb-prev,#lb-next{position:absolute;top:50%;transform:translateY(-50%);color:#a8a29e;font-size:44px;cursor:pointer;user-select:none;padding:24px}
#lb-prev{left:16px}#lb-next{right:16px}
#lb-prev:hover,#lb-next:hover,#lb-x:hover{color:#fff}
@media (max-width:900px){.gal.g3,.gal.g4{grid-template-columns:repeat(2,1fr)}.scorebox{grid-template-columns:1fr}.wrap{padding:0 20px}}
"""

JS = """
(function(){
var lb=document.getElementById('lb'),img=document.getElementById('lb-img'),cap=document.getElementById('lb-cap');
var list=[],idx=0;
function render(){var a=list[idx];if(!a)return;img.src=a.getAttribute('href');cap.innerHTML=a.getAttribute('data-cap')||'';lb.classList.add('on');}
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

def shot(src, cap):
    return ('<a class="shot" href="%s" data-cap="%s"><span class="ph"><img loading="lazy" src="%s" alt=""></span>'
            '<span class="cap">%s</span></a>') % (asset(src), cap.replace('"', '&quot;'), asset(src), cap)

def gal(items, cols):
    cls = {2: "g2", 3: "g3", 4: "g4"}[cols]
    return '<div class="gal %s">%s</div>' % (cls, "".join(shot(s, c) for s, c in items))

def qa_cards(rows):
    out = []
    for i, (rule, ev, res, basis) in enumerate(rows):
        label, kind = res
        out.append(
            '<div class="qa"><div class="top"><span class="rule">%s</span>'
            '<span class="chip sm %s">%s</span><span class="basis">%s</span></div>'
            '<div class="ev">%s</div></div>' % (rule, kind, label, basis, ev))
    return "".join(out)

def score_bars(dims, total, gated, overall_kind):
    rows = []
    for name, weight, sc, why in dims:
        pct = int(sc / 5 * 100)
        rows.append('<div class="row"><span>%s <span style="color:#a8a29e">·%d%%</span></span>'
                    '<span class="track"><span class="fill" style="width:%d%%"></span></span>'
                    '<span class="val">%d</span></div>' % (name, weight, pct, sc))
    whys = "".join('<div><b>%s</b> — %s</div>' % (n, w) for n, _, _, w in dims)
    return ('<div class="scorebox"><div class="bars">%s'
            '<details class="dimwhy"><summary>各维度评分依据</summary><div>%s</div></details></div>'
            '<div><div class="big"><div class="k">quality_score</div><div class="v">%s</div>'
            '<div class="g">统一 rubric 八维度加权归一（design-agent-v0/eval/rubrics/unified-design-agent-rubric-v0.1.md，来自 agentic-adhoc 仓库）</div></div>'
            '<div class="big"><div class="k">gated_score</div><div class="v" style="font-size:17px;line-height:1.5;margin-top:10px">%s</div></div></div></div>'
            % ("".join(rows), whys, total, gated))

def report(c):
    navlinks = "".join('<a href="#p%d">%s</a>' % (i + 1, t) for i, t in
                       enumerate(["任务与需求", "做法", "输入与产出", "QA 质检", "合格判定"]))
    chips = "".join('<span class="chip %s">%s</span>' % (k, t) for t, k in c["chips"])
    facts = ('<div class="facts"><span>案例目录 <b>%s</b></span><span>成品 <b>%d</b> 张</span>'
             '<span>验收特写 <b>%d</b> 张</span><span>quality_score <b>%s</b></span>'
             '<span>报告 <b>2026-10-28 · v2 重制</b></span></div>'
             % (c["dir"], len(c["outputs"]), len(c["crops"]), c["score"]))
    return f"""<!DOCTYPE html><html lang="zh"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{c['title']} · 任务报告</title><style>{CSS}</style></head><body>
<nav class="nav"><div class="wrap"><span class="brand">试穿任务报告</span><span class="links">{navlinks}</span><a class="home" href="index.html">&#8592; 八任务总览</a></div></nav>
<header class="hero"><div class="wrap">
<div class="eyebrow">Fashion Try-on Benchmark · Task Report</div>
<h1>{c['title']}</h1>
<div class="chips">{chips}</div>
{facts}
</div></header>
<div class="wrap">
<section id="p1"><div class="sh"><span class="no">01</span><h2>任务是什么 · 客户需求 · 做到什么程度</h2></div><div class="prose">{c['s1']}</div></section>
<section id="p2"><div class="sh"><span class="no">02</span><h2>怎么做的</h2></div><div class="prose">{c['s2']}</div></section>
<section id="p3"><div class="sh"><span class="no">03</span><h2>输入与产出可视化</h2></div>
<h3 class="lab">输入 · 客户 brief 引用图</h3>
{gal(c['inputs'], 4)}
<h3 class="lab">产出 · 成品图（点开看原图，左右方向键翻张）</h3>
{gal(c['outputs'], 3)}
{('<h3 class="lab">验收特写 · 关键区 2-3&#215; 放大</h3>' + gal(c['crops'], 4)) if c['crops'] else ''}
</section>
<section id="p4"><div class="sh"><span class="no">04</span><h2>按本任务 QA 规则质检</h2></div>
<div class="prose" style="margin-bottom:18px"><p style="font-size:13.5px;color:var(--mut)">任务级明文规则逐条核验 + 统一 rubric 八维度评分。及格线：hard gates 全过且 quality_score &#8805; 0.70。结论全部来自直接读图实测（find-defects-first + 关键区 2-3&#215; 特写），推断均已标注。</p></div>
{qa_cards(c['qa'])}
{score_bars(c['dims'], c['score'], c['gated'], c['vkind'])}
</section>
<section id="p5"><div class="sh"><span class="no">05</span><h2>合格判定</h2></div>
<div class="verdict {c['vkind']}"><div class="vtitle">{c['vtitle']}</div>{c['vbody']}</div>
</section>
<footer>数据来源：本目录 gen_reports_v2.py（判定/QA/评分原样取自 v1，未改动结论）· 各 case spec/meta.json（模型/prompt/seed/输入输出哈希）· 工作文档 2026-10-27_各图生成过程与代码清单_工作文档.md。<br>benchmark 红线：client-brief/ 字节不动 · 不虚构缺失数据 · 历史生成结果不作输入参考 · 参考对标图（不可直接用）从未喂给任何模型。</footer>
</div>
{LIGHTBOX}
<script>{JS}</script>
</body></html>"""

# ================= 数据（判定/QA/评分原样取自 v1） =================
CASES = []

CASES.append(dict(
    key="client-006",
    title="client-006 · 开衫模特换装（五姿势）",
    dir="projects/2026-08-28-client-006-fashion-model-swap",
    chips=[("PASS with deviations", "dev"), ("衣长/胸围量化 + 模特一致性核实 待办", "todo")],
    score="0.79",
    s1="""<p><b>任务</b>：给同一模特生成 5 张不同姿势的图，统一穿 brief 指定的象牙白针织开衫（clothing-test.jpeg）。</p>
<p><b>客户明文需求（source-record constraints_stated_by_client）</b>：① 主要把控服装细节——服装细节保真是本任务核心，不是摄影美感；② <b>衣长与胸围是两个量化验收指标</b>；③ 每款 5 张、同一模特；④ 姿势可在 5 张间变化。</p>
<p><b>做到的程度</b>：5 张成品全部出图并逐张像素级验收；服装结构条款（全扣紧无内衬/双黄罗纹袖口/9 颗淡黄扣/宽罗纹下摆尖角搭位）写进 prompt 硬条款并逐张核验。<span class="warn">衣长/胸围：客户未给尺寸表（record 明文记录），无 pass/fail 阈值；比例对照法已在 constraints_we_added 定义，本次未执行量化测量——如实标注为待办。</span></p>""",
    s2="""<p>链路：本地 ComfyUI(8289) + qwen-image-2.1 edit + outfit-swap LoRA（euler/simple cfg1.0 steps25，resolution 跟随模特图原生尺寸）。每 take 一张模特图 + 同一张服装图 + 姿势条款 prompt。</p>
<p>过程：take01-04 一次出图；take05 幻觉出白色蕾丝短裙 → take05fix（seed 20261051，加下装硬锁+发丝条款）修复下装但门襟黄扣 10&#8800;9 → <b>take05fix2（seed 20261056）3&#215; 特写逐颗数扣 = 9 颗整（门襟 7+搭位 2，与产品分布一致），PASS</b>。元数据按 benchmark 红线落 meta.json（模型/prompt/seed/输入输出 SHA-256）。</p>""",
    inputs=[
        (R"projects/2026-08-28-client-006-fashion-model-swap/client-brief/clothing-test.jpeg", "服装图 clothing-test.jpeg（象牙白开衫·9 黄扣）"),
        (R"projects/2026-08-28-client-006-fashion-model-swap/client-brief/model-ref.jpeg", "模特图 model-ref.jpeg"),
        (R"projects/2026-08-28-client-006-fashion-model-swap/client-brief/model-refs/e0542f50-db4b-40c1-9884-82c3ac3396a8.jpeg", "模特参考 e0542f50（take02 用）"),
    ],
    outputs=[
        (COMFY + "/outfit_swap_00006_.png", "take01 · 自然正面站立 · PASS"),
        (COMFY + "/outfit_swap_00008_.png", "take02 · 保持源姿势 · PASS（左下摆旁细杂痕披露）"),
        (COMFY + "/outfit_swap_00010_.png", "take03 · 保持源姿势 · PASS（608&#215;800 源图偏小披露）"),
        (COMFY + "/outfit_swap_00012_.png", "take04 · 保持姿势室内 · PASS（下摆塞腰披露）"),
        (COMFY + "/outfit_swap_00035_.png", "take05fix2 · 3/4 转身 · PASS（9 扣整数）"),
    ],
    crops=[
        (R"outputs/viz/accept-zoom-2026-10-28/c6_placket_full.png", "3&#215; 门襟特写（逐颗数扣验收：9 颗整）"),
    ],
    qa=[
        ("服装细节保真（客户核心要求）", "象牙白针织/双黄罗纹袖口/宽罗纹下摆+尖角搭位逐张 3&#215; 特写核对，take05fix2 门襟 7+搭位 2=9 颗与产品分布一致", ("PASS", "pass"), "工作文档 Case3 + spec per_take note"),
        ("全扣紧·无内衬外露（we_added 硬条款）", "prompt 硬条款 + 5 张实测无内衬外露", ("PASS", "pass"), "spec prompt + 验收"),
        ("每款 5 张·同一模特（客户约束）", "5 张已出；take01/05fix2 用 model-ref，take02-04 用 model-refs 三张——是否同一人未逐张人脸核实（审计项开放）", ("待核实", "todo"), "README + 缩略图比对"),
        ("衣长/胸围量化验收（客户指标）", "无客户尺寸表→无阈值；比例对照法已定义未执行", ("未执行", "todo"), "source-record in-9 同款缺席记录"),
        ("9 颗淡黄扣（产品结构）", "take05fix 曾 10 颗（门襟多 1）→ take05fix2 修至 9 颗整", ("PASS", "pass"), "c6_placket/c6_placket_full 特写"),
    ],
    dims=[
        ("Brief adherence", 15, 5, "5 张全部按服装硬条款+姿势执行；take05 幻觉经两轮修复闭环"),
        ("Visual quality", 20, 4, "take02 细杂痕/take04 下摆塞腰/take05fix2 墨镜自加——均有披露，无结构性缺陷"),
        ("Brand consistency", 15, 4, "服装图与产品图逐区一致；take05fix 曾扣数漂移已修复"),
        ("Refinement ability", 15, 4, "两轮修正均为增量（下装锁/扣数），未破坏已过内容"),
        ("Cross-asset consistency", 10, 4, "5 张同款服装一致；模特身份一致性待核实（同上）"),
        ("Production readiness", 10, 3, "meta.json 齐备（哈希/seed/prompt）；衣长胸围测量未执行"),
        ("Efficiency", 5, 4, "take05 一张两轮重跑，其余一次过"),
    ],
    gated="gates 全过（无 hard-gate 违约）",
    rework=[
        ("初跑 · take05", "take01-04 一次过；take05 模型幻觉出白色蕾丝短裙——产品只有开衫，下装不属于本任务", "fail"),
        ("第 1 轮 · take05fix（seed 20261051）", "prompt 加下装硬锁（NOT skirt / NOT lace dress）+发丝条款 → 下装修复，但门襟黄扣数出 10 颗（产品 9 颗：门襟 7+搭位 2）", "dev"),
        ("第 2 轮 · take05fix2（seed 20261056）", "换 seed 重跑 → 3× 特写逐颗数扣 = 9 颗整，与产品分布一致 → PASS", "pass"),
    ],
    vkind="dev",
    vtitle="判定：5 张成品合格（PASS with deviations）",
    vbody="""<p>偏差披露：</p><ul class="devlist"><li>take02 左下摆旁细杂痕</li><li>take03 源图 608&#215;800 偏小</li><li>take04 下摆塞进裤腰（产品不塞）</li><li>take05fix2 头顶墨镜为模型自加（prompt 未要求）</li></ul>
<p><b>衣长/胸围量化对照未执行</b>——无客户尺寸表无阈值（record 明文），比例对照法已定义；模特「同一人」约束的核实项开放。两项待办不阻塞出图合格判定，但未闭环前不宣布整体完成。</p>""",
))

CASES.append(dict(
    key="lead-003",
    title="lead-003 · 五张 lookbook 套装（3 外景 + 2 棚拍）",
    dir="projects/2026-09-10-lead-003-fashion-lookbook-set",
    chips=[("PASS", "pass")],
    score="0.82",
    s1="""<p><b>任务</b>：用 brief 的合成模特 + 两件套 SKU（淡天蓝罗纹针织衫 + 奶白高腰阔腿牛仔裤），出 5 张姿势不同的全身图。</p>
<p><b>客户明文需求（生图要求.txt 原文 5 条）</b>：① 姿势不呆板需放松；② 5 张姿势不同全身图（3 外景 2 棚拍，棚拍一正一背）；③ 5 张背景不可完全相同（同场景可变角度/景色/道具）；④ 衣服款看平铺图、需还原衣服细节；⑤ 模特用「模特形象」文件夹的形象。另有 25 页品牌 AI 生图规范 PDF（交付标准/姿势词汇/七类拒绝分类法）在 brief 内。</p>
<p><b>做到的程度</b>：5 张全部出图；10-28 审计把「规则→引用绑定」补齐——外景 3 张场景基调与 场景动作参考 两张对齐、take04 白贝壳手包对齐 包参考.png、白运动鞋对齐鞋参考；草帽墨镜属场景参考的环境搭配，指定配饰清单（in-6 包/鞋/耳环）已满足。<span class="ok">审计闭合，不需重跑。</span></p>""",
    s2="""<p>链路同上（统一机制见工作文档&#167;一）。模特图=模特形象/模特形象.png；服装图=work/garment-composite.png（两件 SKU 平铺并排）。take01-05 seed 20261030-34；4 张 wrapper 1200s 超时后从 ComfyUI /history 按 seed 恢复指针。</p>""",
    inputs=[
        (R"projects/2026-09-10-lead-003-fashion-lookbook-set/client-brief/模特形象/模特形象.png", "模特形象.png（合成模特·身份）"),
        (R"projects/2026-09-10-lead-003-fashion-lookbook-set/client-brief/SWGQ305139022+SWGQ110019014/SWGQ110019014/SWGQ110019014 (1).jpg", "上身 SKU 平铺（owns 上衣细节）"),
        (R"projects/2026-09-10-lead-003-fashion-lookbook-set/client-brief/SWGQ305139022+SWGQ110019014/SWGQ305139022/SWGQ305139022 (1).jpg", "下身 SKU 平铺（owns 裤装细节）"),
        (R"projects/2026-09-10-lead-003-fashion-lookbook-set/client-brief/SWGQ305139022+SWGQ110019014/场景动作参考.jpg", "场景动作参考 1（外景基调）"),
        (R"projects/2026-09-10-lead-003-fashion-lookbook-set/client-brief/SWGQ305139022+SWGQ110019014/场景动作参考1.jpg", "场景动作参考 2（外景基调）"),
        (R"projects/2026-09-10-lead-003-fashion-lookbook-set/client-brief/SWGQ305139022+SWGQ110019014/包参考.png", "包参考.png（白色贝壳包）"),
    ],
    outputs=[
        (COMFY + "/outfit_swap_00009_.png", "take01 · 棚拍正面浅灰底"),
        (COMFY + "/outfit_swap_00014_.png", "take02 · 棚拍背面"),
        (COMFY + "/outfit_swap_00017_.png", "take03 · 户外铺石街+店铺立面（对齐场景参考2）"),
        (COMFY + "/outfit_swap_00021_.png", "take04 · 街拍行走+白色贝壳包（对齐包参考）"),
        (COMFY + "/outfit_swap_00025_.png", "take05 · 土色质感墙倚靠（对齐场景参考1）"),
    ],
    crops=[],
    qa=[
        ("5 张姿势不同·全身（生图要求②）", "5 take 五种姿势：棚拍正/背 + 户外站/行走/倚墙", ("PASS", "pass"), "五张整图实测"),
        ("3 外景 2 棚拍（生图要求②）", "结构精确匹配", ("PASS", "pass"), "同上"),
        ("背景不可完全相同（生图要求③）", "浅灰棚/白棚/铺石街/街拍/土色墙——五种环境", ("PASS", "pass"), "同上"),
        ("衣服细节按平铺图还原（生图要求④）", "罗纹针织衫翻折 polo 领/3 扣门襟/罗纹袖口/侧开衩 + 高腰阔腿牛仔裤纽扣门襟/斜插袋+贴袋，缩略图核对", ("PASS", "pass"), "工作文档 Case4"),
        ("模特用指定形象（生图要求⑤）", "5 张同一合成模特身份", ("PASS", "pass"), "五张脸型发型一致"),
        ("配饰按 in-6 参考（包/鞋/耳环）", "take04 白贝壳手包=包参考.png；白复古运动鞋；小金圈耳环", ("PASS", "pass"), "10-28 审计闭合"),
        ("场景基调按 in-7 参考", "外景 3 张对齐两张场景动作参考的街面/铺石/店铺立面基调", ("PASS", "pass"), "10-28 审计闭合"),
    ],
    dims=[
        ("Brief adherence", 15, 5, "五条生图要求逐条满足"),
        ("Visual quality", 20, 4, "5 张整体构图/光影可用，个别背景元素生成感（如实披露，未逐张特写复核）"),
        ("Brand consistency", 15, 5, "身份/服装/配饰全部对齐指定参考"),
        ("Refinement ability", 15, 3, "本组无需返工（第一次全过）"),
        ("Cross-asset consistency", 10, 4, "5 张同一人物同一套装，背景按要求各异"),
        ("Production readiness", 10, 4, "meta.json 齐；无尺寸表→无量化门槛（同 corpus 级缺席）"),
        ("Efficiency", 5, 4, "4 次 wrapper 超时恢复（流程内），无重跑"),
    ],
    gated="gates 全过",
    vkind="pass",
    vtitle="判定：5 张成品合格",
    vbody="""<p>客户五条明文要求逐条实测满足；规则→引用绑定审计（场景/包/鞋/耳环）10-28 闭合，无需重跑。</p>
<p>披露：本组为整图级验收+缩略图核对，未做逐张 3&#215; 特写（批次最早、当时的验收粒度记录在工作文档）；衣长/胸围同 corpus 级无尺寸表。历史反馈（record 内）按 benchmark 规则作 context，不并入首请求验收。</p>""",
))

CASES.append(dict(
    key="shein",
    title="shein · A/B 两款波西米亚两件套（每款 5 views）",
    dir="projects/2026-09-15-shein-image-test",
    chips=[("姿势与服装维度 PASS", "dev"), ("生产规格 FAIL（3584&#215;4800/精修未达）", "fail"), ("4K 方案待用户拍板", "todo")],
    score="0.68",
    s1="""<p><b>任务</b>：A 款（藏青波西米亚两件套）与 B 款（黑色挂脖菠萝印花两件套），每款复刻 5 个 views。</p>
<p><b>客户明文需求</b>：① initial_query：「3:4比例，<b>4K分辨率（3584&#215;4800）</b>，含精修可直接上架」；② README 分工：<b>样衣图 owns garment details；姿势参考 owns poses</b>（A/B 款各 5 张姿势参考图）；搭配需求 owns styling；模版以及模特 supplies model/scene；③ record quality_gates（历史 internal QA 口径）：每款 5 views、10 张唯一、3584&#215;4800 RGB JPEG。</p>
<p><b>做到的程度</b>：姿势违规（首批 10 张全部自编姿势、0 张姿势参考）已整改——10-28 重摆批后 <b>A/B 各 5 张姿势参考全覆盖</b>；服装细节按样衣图逐区 3&#215; 特写核对；中缝竖纹经样衣三视定案为「异款裙特征、非本款缺陷」，NO-stripe 条款正确。<span class="bad">4K 缺口：链路 1920 基准实出 1664&#215;2208，无通用超分模型——3584&#215;4800 未达成，需用户拍板方案。</span></p>""",
    s2="""<p>链路同上（--resolution 1920 强制，因 B 模特图小）。系统性事故「双联拼图」（A05/B01fix/B02/B04 连续）定位为静态中性取景触发，修正一律加单人硬条款（NOT a diptych...）。10-28 姿势对齐批：A06/A07/A08 + B04fix2&#8594;B04fix2b、B02fix2&#8594;B02fix2c/B03fixb，姿势描述从姿势参考图逐张翻译成 extras 文本；B04fix2 首跑姿势未达成，强化「arms behind back」措辞+换 seed 后达成。</p>""",
    inputs=[
        (R"projects/2026-09-15-shein-image-test/client-brief/A款/样衣图/AiarrcQxFm-WJrjE4fNBZKtmurkCDSZQ.png", "A 款样衣图（owns A 细节）"),
        (R"projects/2026-09-15-shein-image-test/client-brief/B款/样衣图/AiarrcQxFm-e1VQHgz5BfLn7BqxE45Wx.png", "B 款样衣图正面（owns B 细节）"),
        (R"projects/2026-09-15-shein-image-test/client-brief/B款/样衣图/sKPJ0w1gQVeg9JMTYGNxaw.jpeg", "B 款样衣图背面（X 交叉带）"),
        (R"projects/2026-09-15-shein-image-test/client-brief/B款/姿势参考/akuvbHARSbO4nxJTLweonw.png", "B 姿势参考1（双手背后全身）"),
        (R"projects/2026-09-15-shein-image-test/client-brief/B款/姿势参考/_kthmSoHRne3hIegtQ6e6g.png", "B 姿势参考4（单手提裙摆）"),
        (R"projects/2026-09-15-shein-image-test/client-brief/B款/搭配需求（不用看脸）/FCAwY9BVQDuJPrLKwt7FQg.png", "B 搭配需求（owns styling）"),
    ],
    outputs=[
        (COMFY + "/outfit_swap_00038_.png", "A06 = A姿势参考1（提裙摆）· PASS-dev"),
        (COMFY + "/outfit_swap_00039_.png", "A07 = A姿势参考4（扶腰·镂空呈现）· PASS-dev"),
        (COMFY + "/outfit_swap_00040_.png", "A08 双手提裙摆加拍 · PASS-dev"),
        (COMFY + "/outfit_swap_00041_.png", "B04fix2b = B姿势参考1（双手背后）· PASS-dev"),
        (COMFY + "/outfit_swap_00042_.png", "B02fix2c = B姿势参考2（躯干·镂空呈现）· PASS-dev"),
        (COMFY + "/outfit_swap_00044_.png", "B03fixb = B姿势参考3（近景双手背后）· PASS-dev"),
        (COMFY + "/outfit_swap_00037_.png", "B02fix2 = B姿势参考4（提裙摆）· PASS-dev"),
        (COMFY + "/outfit_swap_00033_.png", "B05 = B姿势参考5（背面回头）· PASS"),
        (COMFY + "/outfit_swap_00011_.png", "A01 正面垂手（首批自编姿势·退役披露件）"),
    ],
    crops=[
        (R"outputs/viz/accept-zoom-2026-10-28/refposes/a07_cutout_side.jpg", "A07 侧腰镂空 3&#215; 特写（金链描边）"),
        (R"outputs/viz/accept-zoom-2026-10-28/refposes/b04fix2b_midseam.jpg", "B04fix2b 中缝 3&#215;（无竖纹·条款生效）"),
        (R"outputs/viz/accept-zoom-2026-10-28/refposes/b04fix2b_waist.jpg", "B04fix2b 腰头 3&#215;（黄黑菱形带对齐）"),
    ],
    qa=[
        ("样衣图 owns garment details", "A：胸前黑绳结带/喇叭袖雏菊心形袖口/金链腰际带/腰隙金链镂空/花卉纵列+鸟纹+雏菊心形裙底边——逐区特写核对（镂空呈现度按 take 披露）；B：黑金菱形挂脖边/红牡丹黄菠萝绿叶橙佩斯利/黄金几何腰带/背面 X 交叉+颈后结——对齐", ("PASS", "pass"), "qa_* 特写 + 10-28 批特写"),
        ("姿势参考 owns poses（README 明文）", "首批违规（自编姿势）→ 10-28 整改后 A/B 各 5 张姿势参考全覆盖：A ref1-5=A06/A05fix/A03/A07/A04；B ref1-5=B04fix2b/B02fix2c/B03fixb/B02fix2/B05", ("PASS（整改后）", "pass"), "spec_A/B per_take 审计注记"),
        ("单人单框（系统性事故整改）", "双联事故 4 例（A05/B01fix/B02/B04）全部修复：A05fix/B01fix2/B02fix/B04fix2b 实测单人；修复批全部带单人硬条款", ("PASS", "pass"), "工作文档&#167;系统性发现"),
        ("中缝竖纹（B01 事故定案）", "样衣三视（正/侧/背）无中缝带；姿势参考 5 张有此带但为白底黄百合异款裙 → NO-stripe 条款正确，10-28 批实测无中缝", ("PASS（维持原判）", "pass"), "10-28 定案记录"),
        ("3584&#215;4800 4K（initial_query 明文）", "实出 1664&#215;2208（--resolution 1920 上限）；ComfyUI 无通用超分模型", ("FAIL", "fail"), "链路参数 + models/upscale_models 清单"),
        ("含精修可直接上架", "无精修工序（Gemini native-4K 为历史项目路径，本链不具备）", ("FAIL", "fail"), "同上"),
        ("搭配按搭配需求/styling 参考", "B：银垂坠耳环/银镯/戒指/米色绑带平底凉鞋 &#10003;；A：赤脚（参考图有白色平底拖鞋——披露）", ("PASS-dev", "dev"), "姿势参考/搭配需求图对照"),
    ],
    dims=[
        ("Brief adherence", 15, 4, "服装/姿势/搭配维度达标；4K 与精修两项明文规格未达"),
        ("Visual quality", 20, 4, "成品可用；镂空形态偏差/腰头图案漂移/底边带层缺失逐张披露"),
        ("Brand consistency", 15, 4, "样衣细节高度还原；镂空等结构项呈现度不一"),
        ("Refinement ability", 15, 4, "姿势未达成经一轮强化措辞+换 seed 闭环（B04fix2&#8594;2b）"),
        ("Cross-asset consistency", 10, 4, "同款多 take 服装一致；A/B 背景色调按 prompt 统一"),
        ("Production readiness", 10, 2, "4K/精修/JPEG 规格未达；meta 齐备"),
        ("Efficiency", 5, 3, "B04fix2 一次重跑；双联事故 4 例返工"),
    ],
    gated="生产有效性 gate 未过（4K/精修）&#8594; gated 0 分",
    rework=[
        ("初跑批 · 10 张", "两类系统性缺陷：① 姿势全部自编、0 张对齐姿势参考（违反 README「姿势参考 owns poses」明文）；② 「双联拼图」事故 4 例（A05/B01fix/B02/B04）——静态中性取景触发模型把单人画成两人", "fail"),
        ("第 1 轮 · 双联专项修复", "每张加「单人单框」硬条款（NOT a diptych...）→ A05fix/B01fix2/B02fix/B04fix2 四张重跑，实测全部单人，双联清零；姿势问题未动", "dev"),
        ("第 2 轮 · 姿势整改批（10-28）", "5 张姿势参考逐张翻译成姿势描述文本写入 prompt，10 张全部重摆（A06/A07/A08 + B04fix2→2b、B02fix2→2c、B03fixb 等）→ A/B 各 5 张姿势参考全覆盖；本轮 B04fix2 首摆姿势仍未达成", "dev"),
        ("第 3 轮 · B04 二跑", "强化「arms behind back」措辞 + 换 seed → B04fix2b 双手背后姿势达成，A/B 姿势参考全部闭环", "pass"),
    ],
    vkind="fail",
    vtitle="判定：内容维度合格，生产规格维度不合格",
    vbody="""<p>姿势（对齐 5 参考）、服装（样衣细节）、单人构图、搭配——按任务明文规则逐条实测通过（整改后）。但 initial_query 的 3584&#215;4800 与「含精修可直接上架」两项<b>链路能力外</b>（qwen 链 1920 上限、无通用超分模型、无精修工序），按统一 rubric 生产有效性 gate 判 FAIL，gated_score 记 0。<b>这不是重跑能解决的——需要用户拍板</b>：①装 ESRGAN 类超分模型（环境级动作）②直接大分辨率生成（质量未知）③维持现状按能力上限披露交付。</p>
<p>偏差披露（全量见 spec per_take）：</p><ul class="devlist"><li>A 组镂空呈现度不一（A06/A08 未呈现/A07 偏大偏圆）</li><li>B 组腰头图案漂移、底边绿叶带层缺失、B02fix2c 角度偏 3/4</li><li>A 组赤脚 vs 参考图拖鞋</li><li>首批自编姿势 5 张退役为披露件</li></ul>""",
))

CASES.append(dict(
    key="lead-006",
    title="lead-006 · 主图（e-commerce）与 A+ 页",
    dir="projects/2026-09-23-lead-006-fashion-main-aplus",
    chips=[("主图 PASS（mainC 推荐）", "pass"), ("A+ 页未交付", "fail"), ("A/B/C 选片由用户定", "todo")],
    score="0.79",
    s1="""<p><b>任务</b>：A+ 工作簿 image37 模特穿蓝灰麻灰针织衫 + 藏青白花阔腿裤，出 e-commerce 主图（纯白底）与 A+ 页。README：当前范围=一张主图 + 一张 A+ 图（工作簿还描述了更广的四色六 view brief，以 record 区分）。</p>
<p><b>做到的程度</b>：主图 A/B/C 三候选——<b>mainC（seed 20261065）对齐 references/pose-reference.png（左手插裤袋）</b>；mainA/B 姿势未绑 pose-reference（违规已补齐）；split V 领/百褶垂坠/hi-lo 下摆/白花阔腿裤逐区 3&#215; 特写核对。<span class="bad">A+ 页未制作（工作量：工作簿 308MB + 版式参考排布，为独立工序）。</span></p>""",
    s2="""<p>链路同上。预处理：image37 带场景复杂背景 → sdmatte-matting 抠人 → 贴纯白底（image37_white.png）；服装图=work/garment-composite.png。mainC 姿势条款按 pose-reference 逐要素翻译（左手插袋/肘外弯/右臂垂/微笑）。</p>""",
    inputs=[
        (R"projects/2026-09-23-lead-006-fashion-main-aplus/references/pose-reference.png", "pose-reference.png（姿势：左手插裤袋）"),
        (R"projects/2026-09-23-lead-006-fashion-main-aplus/references/length-reference.png", "length-reference.png（长度）"),
        (R"projects/2026-09-23-lead-006-fashion-main-aplus/references/aplus-layout-reference.png", "aplus-layout-reference.png（A+ 版式）"),
        (R"projects/2026-09-23-lead-006-fashion-main-aplus/references/top-reference.jpg", "top-reference.jpg（上衣）"),
    ],
    outputs=[
        (COMFY + "/outfit_swap_00043_.png", "<b>mainC = pose-reference（左手插裤袋）· PASS · 推荐候选</b>"),
        (COMFY + "/outfit_swap_00020_.png", "mainA · 保持 image37 原姿势（姿势违规·披露）"),
        (COMFY + "/outfit_swap_00024_.png", "mainB · 自编持手机+草编包（姿势违规·披露）"),
    ],
    crops=[
        (R"outputs/viz/accept-zoom-2026-10-28/refposes/mainC_neckline.jpg", "mainC 领口 3&#215;（split V+百褶垂坠）"),
        (R"outputs/viz/accept-zoom-2026-10-28/refposes/mainC_hem.jpg", "mainC 插袋 3&#215;（姿势达成+hi-lo 下摆）"),
        (R"outputs/viz/accept-zoom-2026-10-28/refposes/mainC_pants.jpg", "mainC 裤印花 3&#215;（白花枝叶均匀）"),
    ],
    qa=[
        ("pose-reference owns 姿势", "mainA/B 未绑姿势（审计认定违规）→ mainC 左手插裤袋姿势实测达成", ("PASS（整改后）", "pass"), "10-28 mainC 验收"),
        ("纯白底 e-commerce 主图", "mainA/B/C 全部纯白底单人", ("PASS", "pass"), "三张整图"),
        ("服装：split V 领/胸前百褶/hi-lo/白花阔腿裤", "逐区 3&#215; 特写核对，与样衣拼图一致", ("PASS", "pass"), "mainC 3&#215; 特写"),
        ("length-reference（衣长）", "裤长及踝对齐；上衣 hi-lo 与参考一致性未逐像素比对（披露）", ("PASS-dev", "dev"), "mainC_pants 特写"),
        ("A+ 页（README 明文范围）", "未制作", ("未执行", "fail"), "—"),
        ("身份/赤脚", "image37 金发模特保真；赤脚与 A/B 一致（原模特赤脚）", ("PASS-dev", "dev"), "三张整图"),
    ],
    dims=[
        ("Brief adherence", 15, 4, "主图姿势/白底/服装达标；A+ 页未交付"),
        ("Visual quality", 20, 5, "mainC 构图/光影/细节全部特写级核对通过"),
        ("Brand consistency", 15, 4, "pose/length 引用绑定（C 达成，A/B 披露）"),
        ("Refinement ability", 15, 4, "姿势违规经一轮补跑闭环"),
        ("Cross-asset consistency", 10, 4, "A/B/C 同一服装同一身份"),
        ("Production readiness", 10, 3, "meta 齐；A+ 缺席"),
        ("Efficiency", 5, 4, "mainC 一次过"),
    ],
    gated="工件契约 gate 未过（A+ 缺席）&#8594; 范围内判主图合格",
    rework=[
        ("初跑 · mainA / mainB", "mainA 保持 image37 原姿势、mainB 自编持手机+草编包——两张均未绑 pose-reference，审计认定违反「pose-reference owns 姿势」", "fail"),
        ("第 1 轮 · mainC 补跑（seed 20261065）", "pose-reference 逐要素翻译进 prompt（左手插裤袋/肘外弯/右臂垂/微笑）+ image37 抠人贴纯白底 → 一次达成，成为唯一姿势合规候选 → PASS", "pass"),
    ],
    vkind="dev",
    vtitle="判定：主图合格（mainC 推荐）；A+ 页未交付，不宣布任务整体完成",
    vbody="""<p>mainA/B 保留作姿势候选披露；mainC 是唯一对齐 pose-reference 的候选。<b>A/B/C 选片由用户定</b>；A+ 页需要单独工序（工作簿解析+版式排布），是否启动待用户指令。length-reference 的衣长逐像素比对未做（比例对照法同 corpus 级无阈值）。</p>""",
))

CASES.append(dict(
    key="loungewear",
    title="loungewear · 居家服模特图",
    dir="projects/2026-10-06-loungewear-model-image",
    chips=[("暂 PASS with 待办", "dev"), ("4K 未达", "fail")],
    score="0.66",
    s1="""<p><b>任务</b>：model-image.png 模特穿上「拍摄」目录的浅灰雪豹纹羊羔绒两件套（拉链外套+长裤），卧室场景。</p>
<p><b>客户明文需求（生图要求.txt 4 条）</b>：① 先生成一张图，<b>可先 1080p 再转 4K</b>；② 参考图目录下是参考图，场景也可以用这种床上的景；③ 要做的宽松一点；④ 衣服在「拍摄」目录，注意颜色/图案/领口/袖口/下身/上下身结合。</p>
<p><b>做到的程度</b>：1 take 出图，四区（领口拉链/口袋下摆/袖口手指/脚口）3&#215; 特写自查通过。<span class="bad">4K 未做（1248&#215;1248）</span>；<span class="warn">「参考图 supplies bedroom setting and pose」的逐张姿势比对未做（只对齐了卧室场景基调）——审计待办。</span></p>""",
    s2="""<p>链路同上。服装图=work/garment-composite.png（5525 上衣平铺+5533 裤平铺并排）。seed 20261027。</p>""",
    inputs=[
        (R"projects/2026-10-06-loungewear-model-image/client-brief/model-image.png", "model-image.png（模特·外观）"),
        (R"projects/2026-10-06-loungewear-model-image/client-brief/拍摄/微信图片_20261005182956_5524_653.jpg", "拍摄目录产品图（管细节）"),
        (R"projects/2026-10-06-loungewear-model-image/client-brief/参考图/0.jpg", "参考图（管场景与姿势）"),
    ],
    outputs=[
        (R"outputs/tryon-gen-2026-10-27-loungewear/loungewear_take01.png", "take01 成品（1248&#215;1248）"),
        (R"outputs/tryon-gen-2026-10-27-loungewear/work/garment-composite.png", "过程件 · 服装拼图（两件平铺并排）"),
    ],
    crops=[],
    qa=[
        ("先 1080p 再转 4K（生图要求①）", "实出 1248&#215;1248，未达 1080p 竖版基准、无 4K", ("FAIL", "fail"), "出图元数据"),
        ("场景按参考图（卧室/床上景）", "卧室场景+毛拖鞋对齐参考基调；床上景未用（披露）", ("PASS-dev", "dev"), "整图对照"),
        ("宽松版型（生图要求③）", "上装宽松垂坠实测", ("PASS", "pass"), "袖口/下摆特写"),
        ("颜色/图案/领口/袖口/下身/上下身结合（生图要求④）", "雪豹纹+粉心/立领全拉链/罗纹袖口/斜插袋/罗纹脚口四区 3&#215; 特写通过", ("PASS", "pass"), "10-27 自查记录"),
        ("参考图 owns pose 的逐张比对", "未执行（姿势为自编自然站姿）", ("待办", "todo"), "10-28 审计"),
    ],
    dims=[
        ("Brief adherence", 15, 3, "细节/宽松达标；4K 未达、姿势参考未逐张绑定"),
        ("Visual quality", 20, 4, "四区特写通过"),
        ("Brand consistency", 15, 4, "服装对齐拍摄目录产品图"),
        ("Refinement ability", 15, 3, "无返工记录"),
        ("Cross-asset consistency", 10, 3, "单 take 无跨图一致性问题"),
        ("Production readiness", 10, 2, "4K 缺席；meta 手写结构齐备"),
        ("Efficiency", 5, 4, "一次过"),
    ],
    gated="生产规格 gate 未过（4K）",
    vkind="dev",
    vtitle="判定：出图内容暂合格，两项硬缺口未闭环",
    vbody="""<p>① 4K（客户明文「转成4k」）——链路无 4K 路径，与 shein 同一决策项（用户拍板超分方案）；② 参考图 owns pose 的逐张比对未做——若比对后姿势不符需重跑。两项闭环前本任务不计「完成」。</p>""",
))

CASES.append(dict(
    key="kidswear",
    title="kidswear · 童装人台换装（正/背两面）",
    dir="projects/2026-10-15-kidswear-mannequin-outfit-swap",
    chips=[("PASS（含 10-23 用户验收）", "pass")],
    score="0.87",
    s1="""<p><b>任务</b>：guidelines.txt：「给了模特和人台图换衣，正面和背面 2 张图。注意衣服和模特不同角度的效果、服装的材质。我们有 QA rubrics for fashion ai，可以建 QA gates 迭代到过。」</p>
<p><b>做到的程度</b>：front/back 两张出图（10-23），VLM 初筛 4/4 PASS + <b>2026-10-23 用户验收通过（本 corpus 唯一有用户验收记录的案例）</b>。角度专项：正面（12 号模特+6 号人台着装）/背面（10 号模特+7 号人台）。</p>""",
    s2="""<p>链路同上（--resolution 0 跟随人台图）。seed 20261023 正反同 seed。成品直接落 outputs/tryon-gen-2026-10-23-kidswear/。</p>""",
    inputs=[
        (R"projects/2026-10-15-kidswear-mannequin-outfit-swap/client-brief/Weixin Image_20261014192022_12_412.png", "12 号模特（正面人物源）"),
        (R"projects/2026-10-15-kidswear-mannequin-outfit-swap/client-brief/Weixin Image_20261014191955_6_412.png", "6 号人台着装（正面服装源）"),
        (R"projects/2026-10-15-kidswear-mannequin-outfit-swap/client-brief/Weixin Image_20261014191957_7_412.png", "7 号人台着装（背面服装源）"),
    ],
    outputs=[
        (R"outputs/tryon-gen-2026-10-23-kidswear/front_01_model12_garment6_seed20261023.png", "front 成品（896&#215;1184）"),
        (R"outputs/tryon-gen-2026-10-23-kidswear/back_01_model10_garment7_seed20261023.png", "back 成品（896&#215;1184）"),
    ],
    crops=[],
    qa=[
        ("正面/背面 2 张（guidelines 明文）", "front_01 + back_01 两张", ("PASS", "pass"), "成品清单"),
        ("不同角度效果+材质（guidelines）", "VLM 初筛 4/4 PASS（角度/材质/结构）；10-23 用户验收", ("PASS", "pass"), "vlm-accept-*.txt + 用户验收记录"),
        ("QA rubrics 建 gates 迭代（guidelines）", "当年以 VLM gates 初筛迭代；10-27 起按用户指令改直接读图验收", ("PASS", "pass"), "工作文档&#167;7"),
    ],
    dims=[
        ("Brief adherence", 15, 5, "guidelines 逐条满足"),
        ("Visual quality", 20, 4, "用户验收通过（10-23）"),
        ("Brand consistency", 15, 4, "人台/模特图正确配对"),
        ("Refinement ability", 15, 3, "无返工记录"),
        ("Cross-asset consistency", 10, 4, "正/背两面服装一致"),
        ("Production readiness", 10, 4, "meta+README 齐"),
        ("Efficiency", 5, 5, "一次过"),
    ],
    gated="gates 全过",
    vkind="pass",
    vtitle="判定：两张成品合格——本 corpus 唯一有用户直接验收记录的案例（2026-10-23）",
    vbody="""<p>备注：验收方式为当时的 VLM gates（Qwen3.5-4B）+用户拍板；若按 10-28 起的直接读图标准复核，可另行安排（未执行，如实标注）。</p>""",
))

CASES.append(dict(
    key="plaid",
    title="plaid · 印花款式换衣（母款版型 &#215; 新印花）",
    dir="projects/2026-09-21-shein-image-plaid",
    chips=[("PASS", "pass")],
    score="0.85",
    s1="""<p><b>任务</b>（xlsx + 嵌入图解析后确认）：新款 W3040126051800594 按母款 W3041125101601310 套——<b>母款版型不变（米白碎花蕾丝 V 领短袖泡泡袖收腰 A 字 midi 连衣裙），印花换成新面料：粉底黑波点雪纺</b>（xlsx 嵌入 image3，带箭头标注）。模特形象参考=Weixin 图中的模特；场景/首图展示参考=Weixin 图（米色墙、酒红腋下包、金饰）。</p>
<p><b>做到的程度</b>：试验样（seed 20261071）一次通过：波点均匀、白色蕾丝沿边保留、收腰 A 字版型精确、酒红包+金饰对齐参考。正式+备选共 3 张全部 PASS（take02 波点偏大偏密披露）。</p>""",
    s2="""<p>链路同上。image2=母款人台正面图（xlsx image1）|粉波点面料图（image3）二联并排；image1=Weixin 185328 正面站立模特。试验样先行验证「换印花保版型」可行性后挂 2 张备选。</p>""",
    inputs=[
        (R"projects/2026-09-21-shein-image-plaid/client-brief/xlsx_media/image1.jpeg", "母款人台正面（版型源·米白碎花版）"),
        (R"projects/2026-09-21-shein-image-plaid/client-brief/xlsx_media/image3.png", "新印花面料（粉底黑波点雪纺·箭头标注）"),
        (R"projects/2026-09-21-shein-image-plaid/client-brief/Weixin Image_2026-09-21_185328_365.png", "模特形象+场景/首图参考（母款黑碎花上身版）"),
    ],
    outputs=[
        (COMFY + "/outfit_swap_00046_.png", "<b>plaid_sample01 · PASS · 正式候选</b>"),
        (COMFY + "/outfit_swap_00048_.png", "plaid_take02 · PASS-dev（波点偏大偏密）"),
        (COMFY + "/outfit_swap_00050_.png", "plaid_take03 · PASS-dev（裙长略长）"),
    ],
    crops=[
        (R"outputs/viz/accept-zoom-2026-10-28/refposes/pl_neckline.jpg", "蕾丝 V 领 2&#215; 特写（白色蕾丝立体保留）"),
        (R"outputs/viz/accept-zoom-2026-10-28/refposes/pl_dots.jpg", "裙身波点 2&#215;（均匀无变形）"),
    ],
    qa=[
        ("母款版型 1:1（xlsx「按母款套」）", "深 V 白蕾丝沿边/蕾丝袖口泡泡短袖/收腰褶裥/A 字裙摆逐区核对", ("PASS", "pass"), "pl_neckline/pl_dots 特写"),
        ("新印花=粉底黑波点雪纺（xlsx image3）", "波点径/间距/雪纺垂坠对齐面料图（take02 偏大偏密披露）", ("PASS", "pass"), "pl_dots 特写"),
        ("白色蕾丝 trim 保持白", "三张实测蕾丝均为白色", ("PASS", "pass"), "整图+特写"),
        ("模特形象+搭配参考", "同一棕发模特/金圈耳环/心形项链/酒红腋下包/金宽镯", ("PASS", "pass"), "三张整图"),
        ("场景按首图展示参考", "米色墙基调对齐", ("PASS", "pass"), "整图对照"),
    ],
    dims=[
        ("Brief adherence", 15, 5, "母款版型+新印花核心需求精确达成"),
        ("Visual quality", 20, 4, "波点均匀/蕾丝立体；take02 点径偏差披露"),
        ("Brand consistency", 15, 4, "模特/搭配/场景对齐参考图"),
        ("Refinement ability", 15, 4, "试验样先行验证配方，批量无返工"),
        ("Cross-asset consistency", 10, 4, "三张同款同印花同模特"),
        ("Production readiness", 10, 4, "spec/meta 齐备（xlsx 需求文本 254 字符全量记录）"),
        ("Efficiency", 5, 5, "试验样一次过+批量一次过"),
    ],
    gated="gates 全过",
    vkind="pass",
    vtitle="判定：3 张成品合格",
    vbody="""<p>偏差披露：take02 波点比面料图偏大偏密；sample01/take03 裙长略长于母款 midi。需求备注列若有未提取到的细则（xlsx 表格文本仅 254 字符，需求主要在参考图），以参考图为准已覆盖；xlsx 是否寄样/是否需要列与出图无关。</p>""",
))

CASES.append(dict(
    key="dayang",
    title="dayang · 棕格纹西装试稿（DOCX 明文验收）",
    dir="projects/2026-09-26-dayang-suit-image-test",
    chips=[("PASS with deviations（内容维度）", "dev"), ("4K 未达", "fail")],
    score="0.78",
    s1="""<p><b>任务</b>：按《服装AIGC外协试稿制作要求.docx》——线稿版型 1:1 还原（平驳领两粒扣+斜插袋盖上衣；侧调节袢双扣+翻边裤脚裤）+ 棕格纹面料（4.5cm 格比）+ 指定配饰 + 指定模特姿势 + 纯白底自然柔光 + 4K 3:4。</p>
<p><b>客户明文验收标准（docx &#167;五原文）</b>：① 服装版型、面料花型高度匹配参考；② 配饰严格遵循配饰参考图；③ 模特姿势与参考一致，无人体畸形、无穿模；④ 纯白背景光线柔和自然；⑤ 分辨率 3:4 符合要求、无明显 AI 瑕疵。</p>
<p><b>做到的程度</b>：试验样（00045）一次通过——「线稿+面料图」输入组合直接生成真实格纹西装；正式+备选共 3 张。<b>指定配饰与姿态参考图不同：墨绿 T914 细斜纹领带（非黑领带）+黑双扣孟克鞋（非乐福）——以配饰参考图为准</b>。<span class="bad">4K 未达（1664&#215;2208）。</span></p>""",
    s2="""<p>链路同上。image2=西装线稿|裤线稿|面料图三联（4546&#215;1648）；image1=模卡全身裁片（model-full.png）；姿势条款=正面站立双手垂（按模特姿态参考图）。试验样先行验证线稿输入可行性。</p>""",
    inputs=[
        (R"projects/2026-09-26-dayang-suit-image-test/client-brief/西装款式线稿图/Notch Slant Flap 2SB.png", "上衣线稿（Notch Slant Flap 2SB）"),
        (R"projects/2026-09-26-dayang-suit-image-test/client-brief/西装款式线稿图/Trouser sketch.png", "裤线稿（侧调节袢+翻边）"),
        (R"projects/2026-09-26-dayang-suit-image-test/client-brief/西装款式线稿图/面料图.png", "面料图（棕格纹 4.5cm 格比）"),
        (R"projects/2026-09-26-dayang-suit-image-test/client-brief/模特姿态+模卡/模特姿态参考图.jpeg", "模特姿态参考图（正面站立双手垂）"),
        (R"projects/2026-09-26-dayang-suit-image-test/client-brief/配饰穿搭/领带（注意纹理）.jpeg", "指定领带（墨绿 T914 细斜纹）"),
        (R"projects/2026-09-26-dayang-suit-image-test/client-brief/配饰穿搭/皮鞋.jpeg", "指定皮鞋（黑色双扣孟克）"),
    ],
    outputs=[
        (COMFY + "/outfit_swap_00045_.png", "<b>dayang_sample01 · PASS-dev · 正式候选（鞋型正确）</b>"),
        (COMFY + "/outfit_swap_00047_.png", "dayang_take02 · PASS-dev（鞋变德比·披露）"),
        (COMFY + "/outfit_swap_00049_.png", "dayang_take03 · PASS-dev（鞋变德比·披露）"),
    ],
    crops=[
        (R"outputs/viz/accept-zoom-2026-10-28/refposes/dy_jacket.jpg", "上装 2&#215;（平驳领/双扣/袋盖/墨绿斜纹领带）"),
        (R"outputs/viz/accept-zoom-2026-10-28/refposes/dy_shoes.jpg", "鞋+翻边裤脚 2&#215;（双扣孟克清晰）"),
    ],
    qa=[
        ("版型 1:1 按线稿（docx&#167;一）", "平驳领/两粒扣/双袋盖斜插袋/翻边裤脚/侧调节袢——裁片核对；<b>左胸手巾袋缺失（线稿有 breast welt pocket）三张一致</b>", ("PASS-dev", "dev"), "dy_jacket/dy_shoes 特写"),
        ("面料肌理花色高还原（docx&#167;一）", "棕黑格纹+细蓝 overcheck、织纹真实、格比均匀", ("PASS", "pass"), "dy_jacket 特写"),
        ("配饰严格按配饰参考图（docx&#167;五②）", "墨绿斜纹领带+白衬衫+黑孟克鞋 &#10003;；take02/03 鞋变系带德比（偏离指定）", ("PASS-dev", "dev"), "dy_shoes（sample01 对/take02-03 偏）"),
        ("姿势与参考一致·无畸形穿模（docx&#167;五③）", "正面站立双手垂对齐姿态参考；人体/手部/鞋型正常", ("PASS", "pass"), "三张整图"),
        ("纯白背景自然柔光（docx&#167;五④）", "白底+柔光实测", ("PASS", "pass"), "整图"),
        ("2K/4K·3:4 无 AI 瑕疵（docx&#167;五⑤）", "3:4 &#10003;；<b>4K 未达（1664&#215;2208）</b>；无明显瑕疵（特写核对）", ("FAIL（4K）", "fail"), "元数据+特写"),
    ],
    dims=[
        ("Brief adherence", 15, 4, "版型/面料/配饰/姿势达标；4K 未达"),
        ("Visual quality", 20, 4, "三张可用；手巾袋缺失+鞋型偏差披露"),
        ("Brand consistency", 15, 5, "配饰以指定参考图为准（纠正了姿态参考图的误导项）"),
        ("Refinement ability", 15, 4, "试验样先行，批量无返工"),
        ("Cross-asset consistency", 10, 4, "三张同款同面料"),
        ("Production readiness", 10, 2, "4K 缺席；spec/meta 齐"),
        ("Efficiency", 5, 5, "试验样+批量均一次过"),
    ],
    gated="生产规格 gate 未过（4K）",
    vkind="dev",
    vtitle="判定：内容维度合格（sample01 为正式候选），4K 规格未达",
    vbody="""<p>DOCX 五条验收标准逐条实测：①②③④ 过（含披露项：左胸手巾袋缺失、take02/03 鞋型偏离、格纹 repeat 目测均匀）；⑤ 的 3:4 过、4K 不过——与 shein/loungewear 同一链路能力上限，<b>等用户拍板 4K 方案后可统一补齐</b>。resolution 参数 1920 基准为本链上限（int8 模型），直接拉高基准的风险未验证。</p>""",
))

# ---------- 生成 ----------
os.makedirs(OUTDIR, exist_ok=True)
for c in CASES:
    p = os.path.join(OUTDIR, "report-%s.html" % c["key"])
    open(p, "w", encoding="utf-8").write(report(c))
    print("written:", p)

# index：8 张案例卡
cards = []
for c in CASES:
    hero = asset(c["outputs"][0][0])
    chips = "".join('<span class="chip sm %s">%s</span> ' % (k, t) for t, k in c["chips"])
    cards.append(
        '<a class="shot" href="report-%s.html"><span class="ph"><img loading="lazy" src="%s" alt=""></span>'
        '<span class="cap"><b>%s</b><br><span style="color:#78716c;font-size:12.5px">%s</span><br>'
        '<span style="display:inline-block;margin-top:8px">%s</span>'
        '<span style="float:right;color:#1c1917;font-weight:700">%s</span></span></a>'
        % (c["key"], hero, c["key"], c["title"].split(" · ", 1)[-1], chips, c["score"]))
index = f"""<!DOCTYPE html><html lang="zh"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>试穿基准 · 八任务报告</title><style>{CSS}
.grid8{{display:grid;grid-template-columns:repeat(4,1fr);gap:18px}}
@media (max-width:1000px){{.grid8{{grid-template-columns:repeat(2,1fr)}}}}
</style></head><body>
<header class="hero"><div class="wrap">
<div class="eyebrow">Fashion Try-on Benchmark · 2026-10-28 · v2</div>
<h1>八任务报告</h1>
<p style="color:var(--mut);max-width:760px;margin:0">8 个真实试穿/出图任务的执行报告：任务与客户明文需求 → 做法 → 输入与产出可视化 → 按任务 QA 规则质检（统一 rubric 八维度）→ 合格判定。每份报告独立成页，点图看原图。</p>
</div></header>
<div class="wrap" style="padding-top:34px">
<div class="grid8">{"".join(cards)}</div>
<footer>判定/QA/评分数据与 v1 一致，未改动结论 · 图片已随包复制进 assets/（全相对路径，整文件夹可搬） · 各 case 明细见 outputs/tryon-gen-*/spec*.json 与 meta*.json</footer>
</div></body></html>"""
open(os.path.join(OUTDIR, "index.html"), "w", encoding="utf-8").write(index)
print("index written;", len(_assets), "assets copied")
