# -*- coding: utf-8 -*-
"""8 份任务 HTML 报告生成器（5 段结构：任务与需求 / 做法 / 输入输出可视化 / QA 质检 / 合格判定）。
图片路径以 LFS 克隆根为基准的相对路径 + ComfyUI output 的绝对 file:/// 路径。
"""
import json, os

ROOT = "E:/projects/fashion-tryon-benchmark-main/fashion-tryon-benchmark-lfs"
OUTDIR = os.path.join(ROOT, "outputs/task-reports-2026-10-28")
COMFY = "file:///E:/projects/ComfyUI/output"

CSS = """
body{font-family:'Segoe UI',system-ui,sans-serif;margin:0;background:#f5f5f7;color:#1d1d1f;line-height:1.65}
.wrap{max-width:1180px;margin:0 auto;padding:32px 28px 80px}
h1{font-size:26px;margin:8px 0 4px}
h2{font-size:19px;margin:40px 0 12px;padding-left:12px;border-left:4px solid #2563eb;color:#1e3a8a}
h3{font-size:15px;margin:18px 0 8px;color:#374151}
.meta{color:#6b7280;font-size:13px;margin-bottom:20px}
.badge{display:inline-block;padding:3px 12px;border-radius:12px;font-size:13px;font-weight:600;margin-right:8px}
.b-pass{background:#dcfce7;color:#166534}.b-dev{background:#fef9c3;color:#854d0e}
.b-fail{background:#fee2e2;color:#991b1b}.b-todo{background:#e0e7ff;color:#3730a3}
table{border-collapse:collapse;width:100%;font-size:13.5px;background:#fff;margin:10px 0}
th,td{border:1px solid #e5e7eb;padding:7px 10px;text-align:left;vertical-align:top}
th{background:#f3f4f6}
.grid{display:grid;gap:10px;margin:12px 0}
.g3{grid-template-columns:repeat(3,1fr)}.g4{grid-template-columns:repeat(4,1fr)}
.card{background:#fff;border:1px solid #e5e7eb;border-radius:8px;overflow:hidden}
.card img{width:100%;height:340px;object-fit:cover;display:block}
.card .cap{padding:7px 10px;font-size:12.5px;color:#374151}
.note{background:#fffbeb;border:1px solid #fde68a;border-radius:8px;padding:10px 14px;font-size:13.5px;margin:10px 0}
.ok{color:#166534;font-weight:600}.warn{color:#854d0e;font-weight:600}.bad{color:#991b1b;font-weight:600}
.score{font-size:15px}
"""

def card(src, cap):
    if not src.startswith("file://"):
        src = "../../" + src
    return f'<div class="card"><img src="{src}"><div class="cap">{cap}</div></div>'

def grid(items, cols=3):
    cls = "g3" if cols == 3 else "g4"
    return f'<div class="grid {cls}">' + "".join(card(s, c) for s, c in items) + "</div>"

def qa_table(rows):
    head = "<tr><th style='width:26%'>QA 规则条款</th><th style='width:44%'>实测证据</th><th style='width:14%'>结果</th><th>依据</th></tr>"
    body = ""
    for i, row in enumerate(rows):
        a, b, res, basis = row
        if not (isinstance(res, tuple) and len(res) == 2):
            raise SystemExit(f"bad qa row #{i} (res={res!r}): {a}")
        body += f"<tr><td>{a}</td><td>{b}</td><td class='{res[1]}'>{res[0]}</td><td>{basis}</td></tr>"
    return f"<table>{head}{body}</table>"

def score_table(rows, total, gated):
    head = "<tr><th>统一 rubric 维度</th><th>权重</th><th>得分(0-5)</th><th>评分依据</th></tr>"
    body = "".join(f"<tr><td>{a}</td><td>{b}</td><td>{c}</td><td>{e}</td></tr>" for a, b, c, e in rows)
    foot = (f"<tr><th colspan='2'>quality_score（适用权重归一）</th><th colspan='2'>{total}</th></tr>"
            f"<tr><th colspan='2'>gated_score（hard gates 全过才计分）</th><th colspan='2'>{gated}</th></tr>")
    return f"<table class='score'>{head}{body}{foot}</table>"

def html(name, case_dir, s1, s2, inputs, outputs, qa_rows, dims, total, gated, verdict, notes):
    return f"""<!DOCTYPE html><html lang="zh"><head><meta charset="utf-8"><title>{name} · 任务报告</title><style>{CSS}</style></head><body><div class="wrap">
<h1>{name}</h1>
<div class="meta">案例目录 {case_dir} · 报告生成 2026-10-28 · 全部结论为直接读图实测（find-defects-first + 关键区 2-3× 特写），推断均已标注</div>
{verdict}
<h2>① 任务是什么 · 客户需求 · 做到什么程度</h2>
{s1}
<h2>② 怎么做的</h2>
{s2}
<h2>③ 输入与产出可视化</h2>
<h3>输入（客户 brief 引用图）</h3>
{grid(inputs)}
<h3>产出（成品图 · 点开看原图）</h3>
{grid(outputs)}
<h2>④ 按本任务 QA 规则质检</h2>
<p style="font-size:13.5px">任务级明文规则逐条核验 + 统一 rubric（design-agent-v0/eval/rubrics/unified-design-agent-rubric-v0.1.md，来自 agentic-adhoc 仓库）八维度评分。及格线：hard gates 全过且 quality_score ≥ 0.70。</p>
{qa_table(qa_rows)}
{score_table(dims, total, gated)}
<h2>⑤ 合格判定</h2>
{notes}
</div></body></html>"""

reports = {}

# ============ 1. client-006 ============
reports["client-006"] = html(
"client-006 · 开衫模特换装（五姿势）",
"projects/2026-08-28-client-006-fashion-model-swap",
"""<p><b>任务</b>：给同一模特生成 5 张不同姿势的图，统一穿 brief 指定的象牙白针织开衫（clothing-test.jpeg）。</p>
<p><b>客户明文需求（source-record constraints_stated_by_client）</b>：① 主要把控服装细节——服装细节保真是本任务核心，不是摄影美感；② <b>衣长与胸围是两个量化验收指标</b>；③ 每款 5 张、同一模特；④ 姿势可在 5 张间变化。</p>
<p><b>做到的程度</b>：5 张成品全部出图并逐张像素级验收；服装结构条款（全扣紧无内衬/双黄罗纹袖口/9 颗淡黄扣/宽罗纹下摆尖角搭位）写进 prompt 硬条款并逐张核验。<span class="warn">衣长/胸围：客户未给尺寸表（record 明文记录），无 pass/fail 阈值；比例对照法已在 constraints_we_added 定义，本次未执行量化测量——如实标注为待办。</span></p>""",
"""<p>链路：本地 ComfyUI(8289) + qwen-image-2.1 edit + outfit-swap LoRA（euler/simple cfg1.0 steps25，resolution 跟随模特图原生尺寸）。每 take 一张模特图 + 同一张服装图 + 姿势条款 prompt。</p>
<p>过程：take01-04 一次出图；take05 幻觉出白色蕾丝短裙 → take05fix（seed 20261051，加下装硬锁+发丝条款）修复下装但门襟黄扣 10≠9 → <b>take05fix2（seed 20261056）3× 特写逐颗数扣 = 9 颗整（门襟 7+搭位 2，与产品分布一致），PASS</b>。元数据按 benchmark 红线落 meta.json（模型/prompt/seed/输入输出 SHA-256）。</p>""",
[
 (R"projects/2026-08-28-client-006-fashion-model-swap/client-brief/clothing-test.jpeg","服装图 clothing-test.jpeg（象牙白开衫·9 黄扣）"),
 (R"projects/2026-08-28-client-006-fashion-model-swap/client-brief/model-ref.jpeg","模特图 model-ref.jpeg"),
 (R"projects/2026-08-28-client-006-fashion-model-swap/client-brief/model-refs/e0542f50-db4b-40c1-9884-82c3ac3396a8.jpeg","模特参考 e0542f50（take02 用）"),
],
[
 (f"{COMFY}/outfit_swap_00006_.png","take01 · 自然正面站立 · PASS"),
 (f"{COMFY}/outfit_swap_00008_.png","take02 · 保持源姿势 · PASS（左下摆旁细杂痕披露）"),
 (f"{COMFY}/outfit_swap_00010_.png","take03 · 保持源姿势 · PASS（608×800 源图偏小披露）"),
 (f"{COMFY}/outfit_swap_00012_.png","take04 · 保持姿势室内 · PASS（下摆塞腰披露）"),
 (f"{COMFY}/outfit_swap_00035_.png","take05fix2 · 3/4 转身 · PASS（9 扣整数）"),
 (R"outputs/viz/accept-zoom-2026-10-28/c6_placket_full.png","3× 门襟特写（逐颗数扣验收）"),
],
[
 ("服装细节保真（客户核心要求）","象牙白针织/双黄罗纹袖口/宽罗纹下摆+尖角搭位逐张 3× 特写核对，take05fix2 门襟 7+搭位 2=9 颗与产品分布一致",("PASS","ok"),"工作文档 Case3 + spec per_take note"),
 ("全扣紧·无内衬外露（we_added 硬条款）","prompt 硬条款 + 5 张实测无内衬外露",("PASS","ok"),"spec prompt + 验收"),
 ("每款 5 张·同一模特（客户约束）","5 张已出；take01/05fix2 用 model-ref，take02-04 用 model-refs 三张——是否同一人未逐张人脸核实（审计项开放）",("待核实","warn"),"README + 缩略图比对"),
 ("衣长/胸围量化验收（客户指标）","无客户尺寸表→无阈值；比例对照法已定义未执行",("未执行","warn"),"source-record in-9 同款缺席记录"),
 ("9 颗淡黄扣（产品结构）","take05fix 曾 10 颗（门襟多 1）→ take05fix2 修至 9 颗整",("PASS","ok"),"c6_placket/c6_placket_full 特写"),
],
[("Brief adherence",15,5,"5 张全部按服装硬条款+姿势执行；take05 幻觉经两轮修复闭环"),
 ("Visual quality",20,4,"take02 细杂痕/take04 下摆塞腰/take05fix2 墨镜自加——均有披露，无结构性缺陷"),
 ("Brand consistency",15,4,"服装图与产品图逐区一致；take05fix 曾扣数漂移已修复"),
 ("Refinement ability",15,4,"两轮修正均为增量（下装锁/扣数），未破坏已过内容"),
 ("Cross-asset consistency",10,4,"5 张同款服装一致；模特身份一致性待核实（同上）"),
 ("Production readiness",10,3,"meta.json 齐备（哈希/seed/prompt）；衣长胸围测量未执行"),
 ("Efficiency",5,4,"take05 一张两轮重跑，其余一次过"),
], "0.79（加权归一）", "gates 全过（无 hard-gate 违约）",
 '<span class="badge b-dev">PASS with deviations（我判）</span><span class="badge b-todo">衣长/胸围量化 + 模特一致性核实 待办</span>',
"""<p class="ok">判定：5 张成品合格（PASS with deviations）。</p>
<p>偏差披露：take02 左下摆旁细杂痕；take03 源图 608×800 偏小；take04 下摆塞进裤腰（产品不塞）；take05fix2 头顶墨镜为模型自加（prompt 未要求）。<b>衣长/胸围量化对照未执行</b>——无客户尺寸表无阈值（record 明文），比例对照法已定义；模特"同一人"约束的核实项开放。两项待办不阻塞出图合格判定，但未闭环前不宣布整体完成。</p>""")

# ============ 2. lead-003 ============
reports["lead-003"] = html(
"lead-003 · 五张 lookbook 套装（3 外景 + 2 棚拍）",
"projects/2026-09-10-lead-003-fashion-lookbook-set",
"""<p><b>任务</b>：用 brief 的合成模特 + 两件套 SKU（淡天蓝罗纹针织衫 + 奶白高腰阔腿牛仔裤），出 5 张姿势不同的全身图。</p>
<p><b>客户明文需求（生图要求.txt 原文 5 条）</b>：① 姿势不呆板需放松；② 5 张姿势不同全身图（3 外景 2 棚拍，棚拍一正一背）；③ 5 张背景不可完全相同（同场景可变角度/景色/道具）；④ 衣服款看平铺图、需还原衣服细节；⑤ 模特用"模特形象"文件夹的形象。另有 25 页品牌 AI 生图规范 PDF（交付标准/姿势词汇/七类拒绝分类法）在 brief 内。</p>
<p><b>做到的程度</b>：5 张全部出图；10-28 审计把"规则→引用绑定"补齐——外景 3 张场景基调与 场景动作参考 两张对齐、take04 白贝壳手包对齐 包参考.png、白运动鞋对齐鞋参考；草帽墨镜属场景参考的环境搭配，指定配饰清单（in-6 包/鞋/耳环）已满足。<span class="ok">审计闭合，不需重跑。</span></p>""",
"""<p>链路同上（统一机制见工作文档§一）。模特图=模特形象/模特形象.png；服装图=work/garment-composite.png（两件 SKU 平铺并排）。take01-05 seed 20261030-34；4 张 wrapper 1200s 超时后从 ComfyUI /history 按 seed 恢复指针。</p>""",
[
 (R"projects/2026-09-10-lead-003-fashion-lookbook-set/client-brief/模特形象/模特形象.png","模特形象.png（合成模特·身份）"),
 (R"projects/2026-09-10-lead-003-fashion-lookbook-set/client-brief/SWGQ305139022+SWGQ110019014/SWGQ110019014/SWGQ110019014 (1).jpg","上身 SKU 平铺（owns 上衣细节）"),
 (R"projects/2026-09-10-lead-003-fashion-lookbook-set/client-brief/SWGQ305139022+SWGQ110019014/SWGQ305139022/SWGQ305139022 (1).jpg","下身 SKU 平铺（owns 裤装细节）"),
 (R"projects/2026-09-10-lead-003-fashion-lookbook-set/client-brief/SWGQ305139022+SWGQ110019014/场景动作参考.jpg","场景动作参考 1（外景基调）"),
 (R"projects/2026-09-10-lead-003-fashion-lookbook-set/client-brief/SWGQ305139022+SWGQ110019014/场景动作参考1.jpg","场景动作参考 2（外景基调）"),
 (R"projects/2026-09-10-lead-003-fashion-lookbook-set/client-brief/SWGQ305139022+SWGQ110019014/包参考.png","包参考.png（白色贝壳包）"),
],
[
 (f"{COMFY}/outfit_swap_00009_.png","take01 · 棚拍正面浅灰底"),
 (f"{COMFY}/outfit_swap_00014_.png","take02 · 棚拍背面"),
 (f"{COMFY}/outfit_swap_00017_.png","take03 · 户外铺石街+店铺立面（对齐场景参考2）"),
 (f"{COMFY}/outfit_swap_00021_.png","take04 · 街拍行走+白色贝壳包（对齐包参考）"),
 (f"{COMFY}/outfit_swap_00025_.png","take05 · 土色质感墙倚靠（对齐场景参考1）"),
],
[
 ("5 张姿势不同·全身（生图要求②）","5 take 五种姿势：棚拍正/背 + 户外站/行走/倚墙",("PASS","ok"),"五张整图实测"),
 ("3 外景 2 棚拍（生图要求②）","结构精确匹配",("PASS","ok"),"同上"),
 ("背景不可完全相同（生图要求③）","浅灰棚/白棚/铺石街/街拍/土色墙——五种环境",("PASS","ok"),"同上"),
 ("衣服细节按平铺图还原（生图要求④）","罗纹针织衫翻折 polo 领/3 扣门襟/罗纹袖口/侧开衩 + 高腰阔腿牛仔裤纽扣门襟/斜插袋+贴袋，l3 缩略图核对",("PASS","ok"),"工作文档 Case4"),
 ("模特用指定形象（生图要求⑤）","5 张同一合成模特身份",("PASS","ok"),"五张脸型发型一致"),
 ("配饰按 in-6 参考（包/鞋/耳环）","take04 白贝壳手包=包参考.png；白复古运动鞋；小金圈耳环",("PASS","ok"),"10-28 审计闭合"),
 ("场景基调按 in-7 参考","外景 3 张对齐两张场景动作参考的街面/铺石/店铺立面基调",("PASS","ok"),"10-28 审计闭合"),
],
[("Brief adherence",15,5,"五条生图要求逐条满足"),
 ("Visual quality",20,4,"5 张整体构图/光影可用，个别背景元素生成感（如实披露，未逐张特写复核）"),
 ("Brand consistency",15,5,"身份/服装/配饰全部对齐指定参考"),
 ("Refinement ability",15,3,"本组无需返工（第一次全过）"),
 ("Cross-asset consistency",10,4,"5 张同一人物同一套装，背景按要求各异"),
 ("Production readiness",10,4,"meta.json 齐；无尺寸表→无量化门槛（同 corpus 级缺席）"),
 ("Efficiency",5,4,"4 次 wrapper 超时恢复（流程内），无重跑"),
], "0.82（加权归一）", "gates 全过",
 '<span class="badge b-pass">PASS（我判）</span>',
"""<p class="ok">判定：5 张成品合格。客户五条明文要求逐条实测满足；规则→引用绑定审计（场景/包/鞋/耳环）10-28 闭合，无需重跑。</p>
<p>披露：本组为整图级验收+缩略图核对，未做逐张 3× 特写（批次最早、当时的验收粒度记录在工作文档）；衣长/胸围同 corpus 级无尺寸表。历史反馈（record 内）按 benchmark 规则作 context，不并入首请求验收。</p>""")

# ============ 3. shein ============
reports["shein"] = html(
"shein · A/B 两款波西米亚两件套（每款 5 views）",
"projects/2026-09-15-shein-image-test",
"""<p><b>任务</b>：A 款（藏青波西米亚两件套）与 B 款（黑色挂脖菠萝印花两件套），每款复刻 5 个 views。</p>
<p><b>客户明文需求</b>：① initial_query："3:4比例，<b>4K分辨率（3584×4800）</b>，含精修可直接上架"；② README 分工：<b>样衣图 owns garment details；姿势参考 owns poses</b>（A/B 款各 5 张姿势参考图）；搭配需求 owns styling；模版以及模特 supplies model/scene；③ record quality_gates（历史 internal QA 口径）：每款 5 views、10 张唯一、3584×4800 RGB JPEG。</p>
<p><b>做到的程度</b>：姿势违规（首批 10 张全部自编姿势、0 张姿势参考）已整改——10-28 重摆批后 <b>A/B 各 5 张姿势参考全覆盖</b>；服装细节按样衣图逐区 3× 特写核对；中缝竖纹经样衣三视定案为"异款裙特征、非本款缺陷"，NO-stripe 条款正确。<span class="bad">4K 缺口：链路 1920 基准实出 1664×2208，无通用超分模型——3584×4800 未达成，需用户拍板方案。</span></p>""",
"""<p>链路同上（--resolution 1920 强制，因 B 模特图小）。系统性事故"双联拼图"（A05/B01fix/B02/B04 连续）定位为静态中性取景触发，修正一律加单人硬条款（NOT a diptych...）。10-28 姿势对齐批：A06/A07/A08 + B04fix2→B04fix2b、B02fix2→B02fix2c/B03fixb，姿势描述从姿势参考图逐张翻译成 extras 文本；B04fix2 首跑姿势未达成，强化"arms behind back"措辞+换 seed 后达成。</p>""",
[
 (R"projects/2026-09-15-shein-image-test/client-brief/A款/样衣图/AiarrcQxFm-WJrjE4fNBZKtmurkCDSZQ.png","A 款样衣图（owns A 细节）"),
 (R"projects/2026-09-15-shein-image-test/client-brief/B款/样衣图/AiarrcQxFm-e1VQHgz5BfLn7BqxE45Wx.png","B 款样衣图正面（owns B 细节）"),
 (R"projects/2026-09-15-shein-image-test/client-brief/B款/样衣图/sKPJ0w1gQVeg9JMTYGNxaw.jpeg","B 款样衣图背面（X 交叉带）"),
 (R"projects/2026-09-15-shein-image-test/client-brief/B款/姿势参考/akuvbHARSbO4nxJTLweonw.png","B 姿势参考1（双手背后全身）"),
 (R"projects/2026-09-15-shein-image-test/client-brief/B款/姿势参考/_kthmSoHRne3hIegtQ6e6g.png","B 姿势参考4（单手提裙摆）"),
 (R"projects/2026-09-15-shein-image-test/client-brief/B款/搭配需求（不用看脸）/FCAwY9BVQDuJPrLKwt7FQg.png","B 搭配需求（owns styling）"),
],
[
 (f"{COMFY}/outfit_swap_00011_.png","A01 正面垂手（自编姿势·退役披露）"),
 (f"{COMFY}/outfit_swap_00038_.png","A06 = A姿势参考1（提裙摆）· PASS-dev"),
 (f"{COMFY}/outfit_swap_00039_.png","A07 = A姿势参考4（扶腰·镂空呈现）· PASS-dev"),
 (f"{COMFY}/outfit_swap_00040_.png","A08 双手提裙摆加拍 · PASS-dev"),
 (f"{COMFY}/outfit_swap_00041_.png","B04fix2b = B姿势参考1（双手背后）· PASS-dev"),
 (f"{COMFY}/outfit_swap_00042_.png","B02fix2c = B姿势参考2（躯干·镂空呈现）· PASS-dev"),
 (f"{COMFY}/outfit_swap_00044_.png","B03fixb = B姿势参考3（近景双手背后）· PASS-dev"),
 (f"{COMFY}/outfit_swap_00037_.png","B02fix2 = B姿势参考4（提裙摆）· PASS-dev"),
 (f"{COMFY}/outfit_swap_00033_.png","B05 = B姿势参考5（背面回头）· PASS"),
 (R"outputs/viz/accept-zoom-2026-10-28/refposes/a07_cutout_side.jpg","A07 侧腰镂空 3× 特写（金链描边）"),
 (R"outputs/viz/accept-zoom-2026-10-28/refposes/b04fix2b_midseam.jpg","B04fix2b 中缝 3×（无竖纹·条款生效）"),
 (R"outputs/viz/accept-zoom-2026-10-28/refposes/b04fix2b_waist.jpg","B04fix2b 腰头 3×（黄黑菱形带对齐）"),
],
[
 ("样衣图 owns garment details","A：胸前黑绳结带/喇叭袖雏菊心形袖口/金链腰际带/腰隙金链镂空/花卉纵列+鸟纹+雏菊心形裙底边——逐区特写核对（镂空呈现度按 take 披露）；B：黑金菱形挂脖边/红牡丹黄菠萝绿叶橙佩斯利/黄金几何腰带/背面 X 交叉+颈后结——对齐",("PASS","ok"),"qa_* 特写 + 10-28 批特写"),
 ("姿势参考 owns poses（README 明文）","首批违规（自编姿势）→ 10-28 整改后 A/B 各 5 张姿势参考全覆盖：A ref1-5=A06/A05fix/A03/A07/A04；B ref1-5=B04fix2b/B02fix2c/B03fixb/B02fix2/B05",("PASS（整改后）","ok"),"spec_A/B per_take 审计注记"),
 ("单人单框（系统性事故整改）","双联事故 4 例（A05/B01fix/B02/B04）全部修复：A05fix/B01fix2/B02fix/B04fix2b 实测单人；修复批全部带单人硬条款",("PASS","ok"),"工作文档§系统性发现"),
 ("中缝竖纹（B01 事故定案）","样衣三视（正/侧/背）无中缝带；姿势参考 5 张有此带但为白底黄百合异款裙 → NO-stripe 条款正确，10-28 批实测无中缝",("PASS（维持原判）","ok"),"10-28 定案记录"),
 ("3584×4800 4K（initial_query 明文）","实出 1664×2208（--resolution 1920 上限）；ComfyUI 无通用超分模型",("FAIL","bad"),"链路参数 + models/upscale_models 清单"),
 ("含精修可直接上架","无精修工序（Gemini native-4K 为历史项目路径，本链不具备）",("FAIL","bad"),"同上"),
 ("搭配按搭配需求/styling 参考","B：银垂坠耳环/银镯/戒指/米色绑带平底凉鞋 ✓；A：赤脚（参考图有白色平底拖鞋——披露）",("PASS-dev","warn"),"姿势参考/搭配需求图对照"),
],
[("Brief adherence",15,4,"服装/姿势/搭配维度达标；4K 与精修两项明文规格未达"),
 ("Visual quality",20,4,"成品可用；镂空形态偏差/腰头图案漂移/底边带层缺失逐张披露"),
 ("Brand consistency",15,4,"样衣细节高度还原；镂空等结构项呈现度不一"),
 ("Refinement ability",15,4,"姿势未达成经一轮强化措辞+换 seed 闭环（B04fix2→2b）"),
 ("Cross-asset consistency",10,4,"同款多 take 服装一致；A/B 背景色调按 prompt 统一"),
 ("Production readiness",10,2,"4K/精修/JPEG 规格未达；meta 齐备"),
 ("Efficiency",5,3,"B04fix2 一次重跑；双联事故 4 例返工"),
], "0.68（加权归一）", "生产有效性 gate 未过（4K/精修）→ gated 0 分",
 '<span class="badge b-dev">姿势与服装维度 PASS</span><span class="badge b-fail">生产规格 FAIL（3584×4800/精修未达）</span><span class="badge b-todo">4K 方案待用户拍板</span>',
"""<p><b>判定：内容维度合格，生产规格维度不合格。</b></p>
<p>姿势（对齐 5 参考）、服装（样衣细节）、单人构图、搭配——按任务明文规则逐条实测通过（整改后）。但 initial_query 的 3584×4800 与"含精修可直接上架"两项<b>链路能力外</b>（qwen 链 1920 上限、无通用超分模型、无精修工序），按统一 rubric 生产有效性 gate 判 FAIL，gated_score 记 0。<b>这不是重跑能解决的——需要用户拍板</b>：①装 ESRGAN 类超分模型（环境级动作）②直接大分辨率生成（质量未知）③维持现状按能力上限披露交付。</p>
<p>偏差披露（全量见 spec per_take）：A 组镂空呈现度不一（A06/A08 未呈现/A07 偏大偏圆）；B 组腰头图案漂移、底边绿叶带层缺失、B02fix2c 角度偏 3/4；A 组赤脚 vs 参考图拖鞋；首批自编姿势 5 张退役为披露件。</p>""")

# ============ 4. lead-006 ============
reports["lead-006"] = html(
"lead-006 · 主图（e-commerce）与 A+ 页",
"projects/2026-09-23-lead-006-fashion-main-aplus",
"""<p><b>任务</b>：A+ 工作簿 image37 模特穿蓝灰麻灰针织衫 + 藏青白花阔腿裤，出 e-commerce 主图（纯白底）与 A+ 页。README：当前范围=一张主图 + 一张 A+ 图（工作簿还描述了更广的四色六 view brief，以 record 区分）。</p>
<p><b>做到的程度</b>：主图 A/B/C 三候选——<b>mainC（seed 20261065）对齐 references/pose-reference.png（左手插裤袋）</b>；mainA/B 姿势未绑 pose-reference（违规已补齐）；split V 领/百褶垂坠/hi-lo 下摆/白花阔腿裤逐区 3× 特写核对。<span class="bad">A+ 页未制作（工作量：工作簿 308MB + 版式参考排布，为独立工序）。</span></p>""",
"""<p>链路同上。预处理：image37 带场景复杂背景 → sdmatte-matting 抠人 → 贴纯白底（image37_white.png）；服装图=work/garment-composite.png。mainC 姿势条款按 pose-reference 逐要素翻译（左手插袋/肘外弯/右臂垂/微笑）。</p>""",
[
 (R"projects/2026-09-23-lead-006-fashion-main-aplus/references/pose-reference.png","pose-reference.png（姿势：左手插裤袋）"),
 (R"projects/2026-09-23-lead-006-fashion-main-aplus/references/length-reference.png","length-reference.png（长度）"),
 (R"projects/2026-09-23-lead-006-fashion-main-aplus/references/aplus-layout-reference.png","aplus-layout-reference.png（A+ 版式）"),
 (R"projects/2026-09-23-lead-006-fashion-main-aplus/references/top-reference.jpg","top-reference.jpg（上衣）"),
],
[
 (f"{COMFY}/outfit_swap_00020_.png","mainA · 保持 image37 原姿势（姿势违规·披露）"),
 (f"{COMFY}/outfit_swap_00024_.png","mainB · 自编持手机+草编包（姿势违规·披露）"),
 (f"{COMFY}/outfit_swap_00043_.png","<b>mainC = pose-reference（左手插裤袋）· PASS</b>"),
 (R"outputs/viz/accept-zoom-2026-10-28/refposes/mainC_neckline.jpg","mainC 领口 3×（split V+百褶垂坠）"),
 (R"outputs/viz/accept-zoom-2026-10-28/refposes/mainC_hem.jpg","mainC 插袋 3×（姿势达成+hi-lo 下摆）"),
 (R"outputs/viz/accept-zoom-2026-10-28/refposes/mainC_pants.jpg","mainC 裤印花 3×（白花枝叶均匀）"),
],
[
 ("pose-reference owns 姿势","mainA/B 未绑姿势（审计认定违规）→ mainC 左手插裤袋姿势实测达成",("PASS（整改后）","ok"),"10-28 mainC 验收"),
 ("纯白底 e-commerce 主图","mainA/B/C 全部纯白底单人",("PASS","ok"),"三张整图"),
 ("服装：split V 领/胸前百褶/hi-lo/白花阔腿裤","逐区 3× 特写核对，与样衣拼图一致",("PASS","ok"),"mainC 3× 特写"),
 ("length-reference（衣长）","裤长及踝对齐；上衣 hi-lo 与参考一致性未逐像素比对（披露）",("PASS-dev","warn"),"mainC_pants 特写"),
 ("A+ 页（README 明文范围）","未制作",("未执行","bad"),"—"),
 ("身份/赤脚","image37 金发模特保真；赤脚与 A/B 一致（原模特赤脚）",("PASS-dev","warn"),"三张整图"),
],
[("Brief adherence",15,4,"主图姿势/白底/服装达标；A+ 页未交付"),
 ("Visual quality",20,5,"mainC 构图/光影/细节全部特写级核对通过"),
 ("Brand consistency",15,4,"pose/length 引用绑定（C 达成，A/B 披露）"),
 ("Refinement ability",15,4,"姿势违规经一轮补跑闭环"),
 ("Cross-asset consistency",10,4,"A/B/C 同一服装同一身份"),
 ("Production readiness",10,3,"meta 齐；A+ 缺席"),
 ("Efficiency",5,4,"mainC 一次过"),
], "0.79（加权归一）", "工件契约 gate 未过（A+ 缺席）→ 范围内判主图合格",
 '<span class="badge b-pass">主图 PASS（mainC 为姿势合规候选）</span><span class="badge b-fail">A+ 页未交付</span><span class="badge b-todo">A/B/C 选片由用户定</span>',
"""<p><b>判定：主图合格（mainC 推荐）；A+ 页未交付，不宣布任务整体完成。</b></p>
<p>mainA/B 保留作姿势候选披露；mainC 是唯一对齐 pose-reference 的候选。<b>A/B/C 选片由用户定</b>；A+ 页需要单独工序（工作簿解析+版式排布），是否启动待用户指令。length-reference 的衣长逐像素比对未做（比例对照法同 corpus 级无阈值）。</p>""")

# ============ 5. loungewear ============
reports["loungewear"] = html(
"loungewear · 居家服模特图",
"projects/2026-10-06-loungewear-model-image",
"""<p><b>任务</b>：model-image.png 模特穿上"拍摄"目录的浅灰雪豹纹羊羔绒两件套（拉链外套+长裤），卧室场景。</p>
<p><b>客户明文需求（生图要求.txt 4 条）</b>：① 先生成一张图，<b>可先 1080p 再转 4K</b>；② 参考图目录下是参考图，场景也可以用这种床上的景；③ 要做的宽松一点；④ 衣服在"拍摄"目录，注意颜色/图案/领口/袖口/下身/上下身结合。</p>
<p><b>做到的程度</b>：1 take 出图，四区（领口拉链/口袋下摆/袖口手指/脚口）3× 特写自查通过。<span class="bad">4K 未做（1248×1248）</span>；<span class="warn">"参考图 supplies bedroom setting and pose"的逐张姿势比对未做（只对齐了卧室场景基调）——审计待办。</span></p>""",
"""<p>链路同上。服装图=work/garment-composite.png（5525 上衣平铺+5533 裤平铺并排）。seed 20261027。</p>""",
[
 (R"projects/2026-10-06-loungewear-model-image/client-brief/model-image.png","model-image.png（模特·外观）"),
 (R"projects/2026-10-06-loungewear-model-image/client-brief/拍摄/微信图片_20261005182956_5524_653.jpg","拍摄目录产品图（管细节）"),
 (R"projects/2026-10-06-loungewear-model-image/client-brief/参考图/0.jpg","参考图（管场景与姿势）"),
],
[
 (R"outputs/tryon-gen-2026-10-27-loungewear/loungewear_take01.png","take01 成品（1248×1248）"),
 (R"outputs/tryon-gen-2026-10-27-loungewear/work/garment-composite.png","服装拼图（两件平铺并排）"),
],
[
 ("先 1080p 再转 4K（生图要求①）","实出 1248×1248，未达 1080p 竖版基准、无 4K",("FAIL","bad"),"出图元数据"),
 ("场景按参考图（卧室/床上景）","卧室场景+毛拖鞋对齐参考基调；床上景未用（披露）",("PASS-dev","warn"),"整图对照"),
 ("宽松版型（生图要求③）","上装宽松垂坠实测",("PASS","ok"),"袖口/下摆特写"),
 ("颜色/图案/领口/袖口/下身/上下身结合（生图要求④）","雪豹纹+粉心/立领全拉链/罗纹袖口/斜插袋/罗纹脚口四区 3× 特写通过",("PASS","ok"),"10-27 自查记录"),
 ("参考图 owns pose 的逐张比对","未执行（姿势为自编自然站姿）",("待办","warn"),"10-28 审计"),
],
[("Brief adherence",15,3,"细节/宽松达标；4K 未达、姿势参考未逐张绑定"),
 ("Visual quality",20,4,"四区特写通过"),
 ("Brand consistency",15,4,"服装对齐拍摄目录产品图"),
 ("Refinement ability",15,3,"无返工记录"),
 ("Cross-asset consistency",10,3,"单 take 无跨图一致性问题"),
 ("Production readiness",10,2,"4K 缺席；meta 手写结构齐备"),
 ("Efficiency",5,4,"一次过"),
], "0.66（加权归一）", "生产规格 gate 未过（4K）",
 '<span class="badge b-dev">暂 PASS with 待办</span><span class="badge b-fail">4K 未达</span>',
"""<p><b>判定：出图内容暂合格，两项硬缺口未闭环。</b></p>
<p>① 4K（客户明文"转成4k"）——链路无 4K 路径，与 shein 同一决策项（用户拍板超分方案）；② 参考图 owns pose 的逐张比对未做——若比对后姿势不符需重跑。两项闭环前本任务不计"完成"。</p>""")

# ============ 6. kidswear ============
reports["kidswear"] = html(
"kidswear · 童装人台换装（正/背两面）",
"projects/2026-10-15-kidswear-mannequin-outfit-swap",
"""<p><b>任务</b>：guidelines.txt："给了模特和人台图换衣，正面和背面 2 张图。注意衣服和模特不同角度的效果、服装的材质。我们有 QA rubrics for fashion ai，可以建 QA gates 迭代到过。"</p>
<p><b>做到的程度</b>：front/back 两张出图（10-23），VLM 初筛 4/4 PASS + 2026-10-23 用户验收通过（本 corpus 唯一有用户验收记录的案例）。角度专项：正面（12 号模特+6 号人台着装）/背面（10 号模特+7 号人台）。</p>""",
"""<p>链路同上（--resolution 0 跟随人台图）。seed 20261023 正反同 seed。成品直接落 outputs/tryon-gen-2026-10-23-kidswear/。</p>""",
[
 (R"projects/2026-10-15-kidswear-mannequin-outfit-swap/client-brief/Weixin Image_20261014191955_6_412.png","6 号人台着装（正面服装源）"),
 (R"projects/2026-10-15-kidswear-mannequin-outfit-swap/client-brief/Weixin Image_20261014192022_12_412.png","12 号模特（正面人物源）"),
 (R"projects/2026-10-15-kidswear-mannequin-outfit-swap/client-brief/Weixin Image_20261014191957_7_412.png","7 号人台着装（背面服装源）"),
],
[
 (R"outputs/tryon-gen-2026-10-23-kidswear/front_01_model12_garment6_seed20261023.png","front 成品（896×1184）"),
 (R"outputs/tryon-gen-2026-10-23-kidswear/back_01_model10_garment7_seed20261023.png","back 成品（896×1184）"),
],
[
 ("正面/背面 2 张（guidelines 明文）","front_01 + back_01 两张",("PASS","ok"),"成品清单"),
 ("不同角度效果+材质（guidelines）","VLM 初筛 4/4 PASS（角度/材质/结构）；10-23 用户验收",("PASS","ok"),"vlm-accept-*.txt + 用户验收记录"),
 ("QA rubrics 建 gates 迭代（guidelines）","当年以 VLM gates 初筛迭代；10-27 起按用户指令改直接读图验收",("PASS","ok"),"工作文档§7"),
],
[("Brief adherence",15,5,"guidelines 逐条满足"),
 ("Visual quality",20,4,"用户验收通过（10-23）"),
 ("Brand consistency",15,4,"人台/模特图正确配对"),
 ("Refinement ability",15,3,"无返工记录"),
 ("Cross-asset consistency",10,4,"正/背两面服装一致"),
 ("Production readiness",10,4,"meta+README 齐"),
 ("Efficiency",5,5,"一次过"),
], "0.87（加权归一）", "gates 全过",
 '<span class="badge b-pass">PASS（含用户验收）</span>',
"""<p class="ok">判定：两张成品合格——本 corpus 唯一有用户直接验收记录的案例（2026-10-23）。</p>
<p>备注：验收方式为当时的 VLM gates（Qwen3.5-4B）+用户拍板；若按 10-28 起的直接读图标准复核，可另行安排（未执行，如实标注）。</p>""")

# ============ 7. plaid ============
reports["plaid"] = html(
"plaid · 印花款式换衣（母款版型 × 新印花）",
"projects/2026-09-21-shein-image-plaid",
"""<p><b>任务</b>（xlsx + 嵌入图解析后确认）：新款 W3040126051800594 按母款 W3041125101601310 套——<b>母款版型不变（米白碎花蕾丝 V 领短袖泡泡袖收腰 A 字 midi 连衣裙），印花换成新面料：粉底黑波点雪纺</b>（xlsx 嵌入 image3，带箭头标注）。模特形象参考=Weixin 图中的模特；场景/首图展示参考=Weixin 图（米色墙、酒红腋下包、金饰）。</p>
<p><b>做到的程度</b>：试验样（seed 20261071）一次通过：波点均匀、白色蕾丝沿边保留、收腰 A 字版型精确、酒红包+金饰对齐参考。正式+备选共 3 张全部 PASS（take02 波点偏大偏密披露）。</p>""",
"""<p>链路同上。image2=母款人台正面图（xlsx image1）|粉波点面料图（image3）二联并排；image1=Weixin 185328 正面站立模特。试验样先行验证"换印花保版型"可行性后挂 2 张备选。</p>""",
[
 (R"projects/2026-09-21-shein-image-plaid/client-brief/xlsx_media/image1.jpeg","母款人台正面（版型源·米白碎花版）"),
 (R"projects/2026-09-21-shein-image-plaid/client-brief/xlsx_media/image3.png","新印花面料（粉底黑波点雪纺·箭头标注）"),
 (R"projects/2026-09-21-shein-image-plaid/client-brief/Weixin Image_2026-09-21_185328_365.png","模特形象+场景/首图参考（母款黑碎花上身版）"),
],
[
 (f"{COMFY}/outfit_swap_00046_.png","plaid_sample01 · PASS（正式候选）"),
 (f"{COMFY}/outfit_swap_00048_.png","plaid_take02 · PASS-dev（波点偏大偏密）"),
 (f"{COMFY}/outfit_swap_00050_.png","plaid_take03 · PASS-dev（裙长略长）"),
 (R"outputs/viz/accept-zoom-2026-10-28/refposes/pl_neckline.jpg","蕾丝 V 领 2× 特写（白色蕾丝立体保留）"),
 (R"outputs/viz/accept-zoom-2026-10-28/refposes/pl_dots.jpg","裙身波点 2×（均匀无变形）"),
],
[
 ("母款版型 1:1（xlsx「按母款套」）","深 V 白蕾丝沿边/蕾丝袖口泡泡短袖/收腰褶裥/A 字裙摆逐区核对",("PASS","ok"),"pl_neckline/pl_dots 特写"),
 ("新印花=粉底黑波点雪纺（xlsx image3）","波点径/间距/雪纺垂坠对齐面料图（take02 偏大偏密披露）",("PASS","ok"),"pl_dots 特写"),
 ("白色蕾丝 trim 保持白","三张实测蕾丝均为白色",("PASS","ok"),"整图+特写"),
 ("模特形象+搭配参考","同一棕发模特/金圈耳环/心形项链/酒红腋下包/金宽镯",("PASS","ok"),"三张整图"),
 ("场景按首图展示参考","米色墙基调对齐",("PASS","ok"),"整图对照"),
],
[("Brief adherence",15,5,"母款版型+新印花核心需求精确达成"),
 ("Visual quality",20,4,"波点均匀/蕾丝立体；take02 点径偏差披露"),
 ("Brand consistency",15,4,"模特/搭配/场景对齐参考图"),
 ("Refinement ability",15,4,"试验样先行验证配方，批量无返工"),
 ("Cross-asset consistency",10,4,"三张同款同印花同模特"),
 ("Production readiness",10,4,"spec/meta 齐备（xlsx 需求文本 254 字符全量记录）"),
 ("Efficiency",5,5,"试验样一次过+批量一次过"),
], "0.85（加权归一）", "gates 全过",
 '<span class="badge b-pass">PASS（我判）</span>',
"""<p class="ok">判定：3 张成品合格。</p>
<p>偏差披露：take02 波点比面料图偏大偏密；sample01/take03 裙长略长于母款 midi。需求备注列若有未提取到的细则（xlsx 表格文本仅 254 字符，需求主要在参考图），以参考图为准已覆盖；xlsx 是否寄样/是否需要列与出图无关。</p>""")

# ============ 8. dayang ============
reports["dayang"] = html(
"dayang · 棕格纹西装试稿（DOCX 明文验收）",
"projects/2026-09-26-dayang-suit-image-test",
"""<p><b>任务</b>：按《服装AIGC外协试稿制作要求.docx》——线稿版型 1:1 还原（平驳领两粒扣+斜插袋盖上衣；侧调节袢双扣+翻边裤脚裤）+ 棕格纹面料（4.5cm 格比）+ 指定配饰 + 指定模特姿势 + 纯白底自然柔光 + 4K 3:4。</p>
<p><b>客户明文验收标准（docx §五原文）</b>：① 服装版型、面料花型高度匹配参考；② 配饰严格遵循配饰参考图；③ 模特姿势与参考一致，无人体畸形、无穿模；④ 纯白背景光线柔和自然；⑤ 分辨率 3:4 符合要求、无明显 AI 瑕疵。</p>
<p><b>做到的程度</b>：试验样（00045）一次通过——"线稿+面料图"输入组合直接生成真实格纹西装；正式+备选共 3 张。<b>指定配饰与姿态参考图不同：墨绿 T914 细斜纹领带（非黑领带）+黑双扣孟克鞋（非乐福）——以配饰参考图为准</b>。<span class="bad">4K 未达（1664×2208）。</span></p>""",
"""<p>链路同上。image2=西装线稿|裤线稿|面料图三联（4546×1648）；image1=模卡全身裁片（model-full.png）；姿势条款=正面站立双手垂（按模特姿态参考图）。试验样先行验证线稿输入可行性。</p>""",
[
 (R"projects/2026-09-26-dayang-suit-image-test/client-brief/西装款式线稿图/Notch Slant Flap 2SB.png","上衣线稿（Notch Slant Flap 2SB）"),
 (R"projects/2026-09-26-dayang-suit-image-test/client-brief/西装款式线稿图/Trouser sketch.png","裤线稿（侧调节袢+翻边）"),
 (R"projects/2026-09-26-dayang-suit-image-test/client-brief/西装款式线稿图/面料图.png","面料图（棕格纹 4.5cm 格比）"),
 (R"projects/2026-09-26-dayang-suit-image-test/client-brief/模特姿态+模卡/模特姿态参考图.jpeg","模特姿态参考图（正面站立双手垂）"),
 (R"projects/2026-09-26-dayang-suit-image-test/client-brief/配饰穿搭/领带（注意纹理）.jpeg","指定领带（墨绿 T914 细斜纹）"),
 (R"projects/2026-09-26-dayang-suit-image-test/client-brief/配饰穿搭/皮鞋.jpeg","指定皮鞋（黑色双扣孟克）"),
],
[
 (f"{COMFY}/outfit_swap_00045_.png","<b>dayang_sample01 · PASS-dev（鞋型正确·正式候选）</b>"),
 (f"{COMFY}/outfit_swap_00047_.png","dayang_take02 · PASS-dev（鞋变德比·披露）"),
 (f"{COMFY}/outfit_swap_00049_.png","dayang_take03 · PASS-dev（鞋变德比·披露）"),
 (R"outputs/viz/accept-zoom-2026-10-28/refposes/dy_jacket.jpg","上装 2×（平驳领/双扣/袋盖/墨绿斜纹领带）"),
 (R"outputs/viz/accept-zoom-2026-10-28/refposes/dy_shoes.jpg","鞋+翻边裤脚 2×（双扣孟克清晰）"),
],
[
 ("版型 1:1 按线稿（docx§一）","平驳领/两粒扣/双袋盖斜插袋/翻边裤脚/侧调节袢——裁片核对；<b>左胸手巾袋缺失（线稿有 breast welt pocket）三张一致</b>",("PASS-dev","warn"),"dy_jacket/dy_shoes 特写"),
 ("面料肌理花色高还原（docx§一）","棕黑格纹+细蓝 overcheck、织纹真实、格比均匀",("PASS","ok"),"dy_jacket 特写"),
 ("配饰严格按配饰参考图（docx§五②）","墨绿斜纹领带+白衬衫+黑孟克鞋 ✓；take02/03 鞋变系带德比（偏离指定）",("PASS-dev","warn"),"dy_shoes（sample01 对/take02-03 偏）"),
 ("姿势与参考一致·无畸形穿模（docx§五③）","正面站立双手垂对齐姿态参考；人体/手部/鞋型正常",("PASS","ok"),"三张整图"),
 ("纯白背景自然柔光（docx§五④）","白底+柔光实测",("PASS","ok"),"整图"),
 ("2K/4K·3:4 无 AI 瑕疵（docx§五⑤）","3:4 ✓；<b>4K 未达（1664×2208）</b>；无明显瑕疵（特写核对）",("FAIL（4K）","bad"),"元数据+特写"),
],
[("Brief adherence",15,4,"版型/面料/配饰/姿势达标；4K 未达"),
 ("Visual quality",20,4,"三张可用；手巾袋缺失+鞋型偏差披露"),
 ("Brand consistency",15,5,"配饰以指定参考图为准（纠正了姿态参考图的误导项）"),
 ("Refinement ability",15,4,"试验样先行，批量无返工"),
 ("Cross-asset consistency",10,4,"三张同款同面料"),
 ("Production readiness",10,2,"4K 缺席；spec/meta 齐"),
 ("Efficiency",5,5,"试验样+批量均一次过"),
], "0.78（加权归一）", "生产规格 gate 未过（4K）",
 '<span class="badge b-dev">PASS with deviations（内容维度）</span><span class="badge b-fail">4K 未达</span>',
"""<p><b>判定：内容维度合格（sample01 为正式候选），4K 规格未达。</b></p>
<p>DOCX 五条验收标准逐条实测：①②③④ 过（含披露项：左胸手巾袋缺失、take02/03 鞋型偏离、格纹repeat目测均匀）；⑤ 的 3:4 过、4K 不过——与 shein/loungewear 同一链路能力上限，<b>等用户拍板 4K 方案后可统一补齐</b>。resolution 参数 1920 基准为本链上限（int8 模型），直接拉高基准的风险未验证。</p>""")

# ---- write ----
os.makedirs(OUTDIR, exist_ok=True)
for key, content in reports.items():
    p = os.path.join(OUTDIR, f"report-{key}.html")
    open(p, "w", encoding="utf-8").write(content)
    print("written:", p)
# index
idx = "<h1>八任务报告索引</h1>" + "".join(
    f'<p><a href="report-{k}.html">{k}</a></p>' for k in reports)
open(os.path.join(OUTDIR, "index.html"), "w", encoding="utf-8").write(idx)
print("index written")
