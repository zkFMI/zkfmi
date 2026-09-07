"""Tiny SVG chart generator for zkfmi.com. Standard library only.

Every chart is an inline <svg> that uses CSS custom properties for colour so it
follows the page theme. Data lives here next to the artifact it came from.
"""
import math

COLORS = ["var(--accent)", "var(--accent-2)", "var(--accent-3)", "var(--danger)", "var(--fg-2)"]

def _fmt(v):
    if float(v).is_integer():
        return f"{v:,.0f}"
    if v >= 1000:
        return f"{v:,.0f}"
    if v >= 100:
        return f"{v:.0f}"
    if v >= 10:
        return f"{v:.1f}"
    return f"{v:.2f}".rstrip("0").rstrip(".")

def _ticks(lo, hi, n=5):
    if hi <= lo:
        return [lo]
    raw = (hi - lo) / n
    mag = 10 ** math.floor(math.log10(raw))
    for m in (1, 2, 2.5, 5, 10):
        step = m * mag
        if (hi - lo) / step <= n + 1:
            break
    start = math.floor(lo / step) * step
    ticks = []
    t = start
    while t <= hi + step * 0.001:
        ticks.append(round(t, 10))
        t += step
    # The axis must reach the largest value, or the top point leaves the plot.
    while ticks[-1] < hi - step * 0.001:
        ticks.append(round(ticks[-1] + step, 10))
    return ticks

def line_chart(series, *, title, xlabel, ylabel, logx=False, logy=False, width=640, height=320, y0=True, note=None, caption=None):
    """series: list of dicts {name, points: [(x, y), ...]}"""
    ml, mr, mt, mb = 56, 18, 34, 46
    pw, ph = width - ml - mr, height - mt - mb
    xs = [p[0] for s in series for p in s["points"]]
    ys = [p[1] for s in series for p in s["points"]]
    fx = (lambda v: math.log2(v)) if logx else (lambda v: v)
    fy = (lambda v: math.log10(v)) if logy else (lambda v: v)
    xlo, xhi = min(xs), max(xs)
    ylo, yhi = (0 if (y0 and not logy) else min(ys)), max(ys)
    if logy:
        ylo = 10 ** math.floor(math.log10(min(ys)))
        yhi = 10 ** math.ceil(math.log10(max(ys)))
    else:
        yt = _ticks(ylo, yhi)
        ylo, yhi = yt[0], yt[-1]
    if logx:
        xticks = sorted(set(xs))
    else:
        xticks = _ticks(xlo, xhi, 6)
        xlo, xhi = xticks[0], xticks[-1]
    def X(v): return ml + (fx(v) - fx(xlo)) / (fx(xhi) - fx(xlo) or 1) * pw
    def Y(v): return mt + ph - (fy(v) - fy(ylo)) / (fy(yhi) - fy(ylo) or 1) * ph
    out = [f'<svg class="chart" viewBox="0 0 {width} {height}" role="img" aria-label="{title}">']
    out.append(f'<text class="ct" x="{ml}" y="18">{title}</text>')
    # y grid
    yticks = [10 ** i for i in range(int(math.log10(ylo)), int(math.log10(yhi)) + 1)] if logy else _ticks(ylo, yhi)
    for t in yticks:
        y = Y(t)
        out.append(f'<line class="cg" x1="{ml}" y1="{y:.1f}" x2="{ml+pw}" y2="{y:.1f}"/>')
        out.append(f'<text class="cl" x="{ml-6}" y="{y+4:.1f}" text-anchor="end">{_fmt(t)}</text>')
    for t in xticks:
        x = X(t)
        out.append(f'<line class="cg" x1="{x:.1f}" y1="{mt}" x2="{x:.1f}" y2="{mt+ph}"/>')
        out.append(f'<text class="cl" x="{x:.1f}" y="{mt+ph+16}" text-anchor="middle">{_fmt(t)}</text>')
    out.append(f'<text class="cl" x="{ml+pw/2:.1f}" y="{height-8}" text-anchor="middle">{xlabel}</text>')
    out.append(f'<text class="cl" transform="translate(14,{mt+ph/2:.1f}) rotate(-90)" text-anchor="middle">{ylabel}</text>')
    for i, s in enumerate(series):
        c = COLORS[i % len(COLORS)]
        pts = " ".join(f"{X(x):.1f},{Y(y):.1f}" for x, y in s["points"])
        dash = ' stroke-dasharray="5 4"' if s.get("dashed") else ""
        out.append(f'<polyline fill="none" stroke="{c}" stroke-width="2.2"{dash} points="{pts}"/>')
        for x, y in s["points"]:
            out.append(f'<circle cx="{X(x):.1f}" cy="{Y(y):.1f}" r="3.2" fill="{c}"><title>{s["name"]}: {xlabel} {_fmt(x)}, {_fmt(y)}</title></circle>')
    # legend: in whichever top corner the data leaves more room; on the right
    # the swatch sits after the text, so no text width has to be guessed.
    mid = ml + pw / 2
    left_high = min((Y(y) for s in series for x, y in s["points"] if X(x) <= mid), default=height)
    right_high = min((Y(y) for s in series for x, y in s["points"] if X(x) > mid), default=height)
    for i, s in enumerate(series):
        c = COLORS[i % len(COLORS)]
        if right_high > left_high:
            out.append(f'<rect x="{ml+pw-8-14}" y="{mt+8+i*16}" width="14" height="3" fill="{c}"/>')
            out.append(f'<text class="cl" x="{ml+pw-8-14-6}" y="{mt+13+i*16}" text-anchor="end">{s["name"]}</text>')
        else:
            out.append(f'<rect x="{ml+8}" y="{mt+8+i*16}" width="14" height="3" fill="{c}"/>')
            out.append(f'<text class="cl" x="{ml+28}" y="{mt+13+i*16}">{s["name"]}</text>')
    if note:
        out.append(f'<text class="cl" x="{ml+pw}" y="{mt-6}" text-anchor="end">{note}</text>')
    out.append("</svg>")
    svg = "\n".join(out)
    if caption:
        return f'<figure class="fig">{svg}<figcaption>{caption}</figcaption></figure>'
    return svg

def bar_chart(bars, *, title, ylabel, width=640, height=300, logy=False, caption=None, unit=""):
    """bars: list of (label, value[, color_index])"""
    ml, mr, mt, mb = 56, 18, 34, 54
    pw, ph = width - ml - mr, height - mt - mb
    vals = [b[1] for b in bars]
    if logy:
        ylo = 10 ** math.floor(math.log10(min(vals)))
        yhi = 10 ** math.ceil(math.log10(max(vals) * 1.6))
        fy = math.log10
        yticks = [10 ** i for i in range(int(math.log10(ylo)), int(math.log10(yhi)) + 1)]
    else:
        yt = _ticks(0, max(vals) * 1.15)
        ylo, yhi = 0, yt[-1]
        fy = lambda v: v
        yticks = yt
    def Y(v): return mt + ph - (fy(v) - fy(ylo)) / (fy(yhi) - fy(ylo) or 1) * ph
    n = len(bars)
    slot = pw / n
    bw = slot * 0.62
    out = [f'<svg class="chart" viewBox="0 0 {width} {height}" role="img" aria-label="{title}">']
    out.append(f'<text class="ct" x="{ml}" y="18">{title}</text>')
    for t in yticks:
        y = Y(t)
        out.append(f'<line class="cg" x1="{ml}" y1="{y:.1f}" x2="{ml+pw}" y2="{y:.1f}"/>')
        out.append(f'<text class="cl" x="{ml-6}" y="{y+4:.1f}" text-anchor="end">{_fmt(t)}</text>')
    out.append(f'<text class="cl" transform="translate(14,{mt+ph/2:.1f}) rotate(-90)" text-anchor="middle">{ylabel}</text>')
    for i, b in enumerate(bars):
        label, v = b[0], b[1]
        c = COLORS[b[2] % len(COLORS)] if len(b) > 2 else COLORS[0]
        x = ml + slot * i + (slot - bw) / 2
        y = Y(v)
        out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{mt+ph-y:.1f}" rx="3" fill="{c}" opacity="0.85"><title>{label}: {_fmt(v)}{unit}</title></rect>')
        out.append(f'<text class="cl cv" x="{x+bw/2:.1f}" y="{y-5:.1f}" text-anchor="middle">{_fmt(v)}{unit}</text>')
        # wrap label on <br>
        parts = label.split("|")
        for j, part in enumerate(parts):
            out.append(f'<text class="cl" x="{x+bw/2:.1f}" y="{mt+ph+16+j*13}" text-anchor="middle">{part}</text>')
    out.append("</svg>")
    svg = "\n".join(out)
    if caption:
        return f'<figure class="fig">{svg}<figcaption>{caption}</figcaption></figure>'
    return svg

# ---------------------------------------------------------------- the charts


JA = {
    "linear backend, settle (host-c)": "線形バックエンド、決済（host-c）",
    "Bulletproof backend, settle (host-a)": "Bulletproof バックエンド、決済（host-a）",
    "Settlement cost against balance width": "残高ビット幅に対する決済コスト",
    "balance width, bits": "残高のビット幅",
    "ms per DvP": "DvP 1 件あたり ms",
    "Verification is linear in the width for the bit-decomposition backend (0.80 ms/bit, 2.1 ms intercept for the instruction itself) and roughly logarithmic for Bulletproofs. Hosts differ; see calibration. Artifacts: defmi.json, rust_bench.json.":
        "ビット分解バックエンドの検証はビット幅に線形（0.80 ms/bit、指図自体の切片 2.1 ms）、Bulletproofs ではおよそ対数。ホストが異なるので較正値を参照。artifact: defmi.json、rust_bench.json。",
    "linear backend": "線形バックエンド",
    "Bulletproof backend": "Bulletproof バックエンド",
    "Settlement package size against balance width": "残高ビット幅に対する決済パッケージの大きさ",
    "bytes": "バイト",
    "896 B per bit on the linear backend against a package that barely moves with Bulletproofs: 3,424 B at 64 bits.":
        "線形バックエンドは 1 ビットあたり 896 B。Bulletproofs ではほとんど増えず、64 ビットで 3,424 B。",
    "prove, payer's device": "証明、支払側の端末",
    "verify, settlement node": "検証、決済ノード",
    "Note ring: who pays for the anonymity set": "note の ring: 匿名集合の費用を誰が払うか",
    "ring size (log scale)": "ring の大きさ（対数目盛）",
    "The wire grows 224 B per doubling and verification stays under 10 ms to a ring of 512. Proving is what grows, so the payer caps the ring, not the node. Artifact: defmi.json.":
        "wire は 2 倍ごとに 224 B 増え、検証は ring 512 まで 10 ms 未満に収まる。増えるのは証明側なので、ring の上限を決めるのはノードではなく支払側。artifact: defmi.json。",
    "uniform decoys": "一様なおとり",
    "recency-matched decoys": "新しさを揃えたおとり",
    "nominal 1/16": "名目値 1/16",
    "Observer's chance of naming the spent note, ring of 16": "観察者が使われた note を当てる確率、ring 16",
    "other settlements between being paid and paying": "受け取りから支払いまでの間にあった他の決済の数",
    "probability": "確率",
    "With no traffic the ring is worth nothing under either rule. With sixteen settlements of traffic, recency-matched decoys reach the nominal figure exactly; uniform decoys leave the observer at 5.8× it. Artifact: rings.json (host-a).":
        "通信がなければどちらの規則でも ring は無価値。16 件の決済が挟まると、新しさを揃えたおとりは名目値にちょうど届き、一様なおとりでは観察者の確率は名目値の 5.8× に留まる。artifact: rings.json（host-a）。",
    "same rack|0 ms": "同一ラック|0 ms", "same metro|1 ms": "同一都市圏|1 ms", "domestic|5 ms": "国内|5 ms",
    "Tokyo–Singapore|15 ms": "東京–シンガポール|15 ms", "six near,|one at 120 ms": "6 台が近く|1 台が 120 ms", "all far|120 ms": "全台が遠い|120 ms",
    "One RFQ quote, 16 makers, by node placement": "見積 1 件、メイカー 16 社、ノード配置別",
    "seconds (log scale)": "秒（対数目盛）",
    "70 rounds, flat in makers and assets, so the wall clock is 70 × RTT of the slowest link. One distant node costs 86% of moving all seven. Artifacts: placement.json, sites.json (delay proxy on one host).":
        "70 ラウンドでメイカー数・資産数に依存しないため、壁時計時間は最も遅い経路の RTT × 70。遠いノードが 1 台あるだけで、7 台すべてを遠くへ移した場合の 86% のコストになる。artifact: placement.json、sites.json（1 台のホスト上で遅延を模擬）。",
    "ms per quote at 15 ms one way": "片道 15 ms での見積 1 件あたり ms",
    "Requests per MPC job against time per quote": "MPC ジョブあたりの依頼数と見積 1 件あたりの時間",
    "requests in one job, Q (log scale)": "1 ジョブ内の依頼数 Q（対数目盛）",
    "ms per quote": "見積 1 件あたり ms",
    "Rounds belong to the job, not the request: 69 rounds at Q=1, 5.5 per quote at Q=32. The job itself takes 9.1 s at Q=32, so one user's wait rises as throughput improves. Artifact: rounds.json.":
        "ラウンドは依頼ではなくジョブに属する。Q=1 で 69 ラウンド、Q=32 では見積 1 件あたり 5.5。ジョブ自体は Q=32 で 9.1 s かかるので、処理量が上がると一人の利用者の待ち時間は延びる。artifact: rounds.json。",
    "gross-gross": "gross-gross", "gross-net": "gross-net", "net-net": "net-net", "net-net|+ attested": "net-net|+ attestation",
    "Settlement verification, 64 trades, 8 participants": "決済の検証、64 取引、8 参加者",
    "ms total": "合計 ms",
    "Netting removes range proofs but not the per-trade zkPI verification (3.5 ms each). Signing the cycle rather than each trade removes that, at the price of third-party verifiability of the allocation. Artifact: defmi.json.":
        "ネッティングは範囲証明を減らすが、取引ごとの zkPI 検証（各 3.5 ms）は減らさない。取引ごとではなくサイクルに署名すればそれも消えるが、配分の第三者検証可能性を失う。artifact: defmi.json。",
    "inputs, reference,|price arithmetic": "入力、参照値、|価格の算術", "+ direction|selection": "+ 方向の|選択", "+ eligibility|gates": "+ 資格の|ゲート", "+ binary|tournament": "+ 二分|トーナメント",
    "Where the MPC rounds go, 16 makers": "MPC のラウンドの内訳、メイカー 16 社",
    "rounds added": "追加ラウンド数",
    "The tournament is 62% of the depth and the eligibility layer 17%; the pricing arithmetic is effectively nothing. Only sequential depth of comparisons matters. Artifact: stages.json.":
        "トーナメントが深さの 62%、資格の層が 17%。価格の算術は実質ゼロ。比較の逐次的な深さだけが効く。artifact: stages.json。",
    "verify, ms": "検証、ms", "prove, ms": "証明、ms",
    "Vetting proof against crowd size": "群の大きさに対する審査証明",
    "crowd (log scale)": "群（対数目盛）",
    "Predicted to double with the crowd; grew about 1.4× per doubling instead, the batched multi-scalar multiplication showing through. That miss moved the default crowd from 16 to 128. Artifact: vetting.json.":
        "群が 2 倍で 2 倍になると予測したが、実際は 2 倍ごとに約 1.4×。まとめて行う多スカラー乗算が効いている。この外れで既定の群を 16 から 128 に変えた。artifact: vetting.json。",
    "Rivinius 2022|verifiable + blame + robust": "Rivinius 2022|検証可能 + 責任特定 + 頑健", "Rivinius 2022|(100 ms RTT)": "Rivinius 2022|（RTT 100 ms）",
    "zkFMI|verifiable, traffic": "zkFMI|検証可能、通信量", "zkFMI|verifiable, wall clock": "zkFMI|検証可能、壁時計時間",
    "What making the computation checkable costs, × plain protocol": "計算を検証可能にする代償、素のプロトコル比",
    "multiple": "倍率",
    "Different regimes, stated in both directions: their construction delivers blame and robustness, this one does not; their overhead is inside every multiplication, this one is a wider field. Artifacts: binding_chain.json, matched_field.json.":
        "前提が異なることを両方向から述べる。彼らの構成は責任特定と頑健性を与え、こちらは与えない。彼らの負荷はすべての乗算の内側にあり、こちらは体を広げることによる。artifact: binding_chain.json、matched_field.json。",
}

def all_charts(lang="en"):
    T = (lambda s: JA.get(s, s)) if lang == "ja" else (lambda s: s)
    c = {}
    c["settle_width"] = line_chart(
        [
            {"name": T("linear backend, settle (host-c)"), "points": [(8, 8.5), (16, 14.8), (24, 21.2), (32, 27.6), (40, 34.0), (48, 40.6)]},
            {"name": T("Bulletproof backend, settle (host-a)"), "points": [(8, 2.09), (16, 2.78), (32, 4.26), (64, 7.02)]},
        ],
        title=T("Settlement cost against balance width"), xlabel=T("balance width, bits"), ylabel=T("ms per DvP"),
        caption=T("Verification is linear in the width for the bit-decomposition backend (0.80 ms/bit, 2.1 ms intercept for the instruction itself) and roughly logarithmic for Bulletproofs. Hosts differ; see calibration. Artifacts: defmi.json, rust_bench.json."))
    c["package_width"] = line_chart(
        [
            {"name": T("linear backend"), "points": [(8, 29267), (16, 36435), (24, 43603), (32, 50771), (40, 57939), (48, 65107)]},
            {"name": T("Bulletproof backend"), "points": [(8, 2656), (16, 2912), (32, 3168), (64, 3424)]},
        ],
        title=T("Settlement package size against balance width"), xlabel=T("balance width, bits"), ylabel=T("bytes"), logy=True,
        caption=T("896 B per bit on the linear backend against a package that barely moves with Bulletproofs: 3,424 B at 64 bits."))
    c["ring"] = line_chart(
        [
            {"name": T("prove, payer's device"), "points": [(2, 10.9), (4, 11.2), (8, 11.3), (16, 11.7), (32, 12.7), (64, 14.5), (128, 18.2), (256, 26.2), (512, 40.3)]},
            {"name": T("verify, settlement node"), "points": [(2, 1.8), (4, 2.1), (8, 2.4), (16, 2.6), (32, 3.1), (64, 3.7), (128, 4.7), (256, 6.4), (512, 9.3)]},
        ],
        title=T("Note ring: who pays for the anonymity set"), xlabel=T("ring size (log scale)"), ylabel=T("ms"), logx=True,
        caption=T("The wire grows 224 B per doubling and verification stays under 10 ms to a ring of 512. Proving is what grows, so the payer caps the ring, not the node. Artifact: defmi.json."))
    c["ring_worth"] = line_chart(
        [
            {"name": T("uniform decoys"), "points": [(0, 1.0), (4, 0.547), (16, 0.359)]},
            {"name": T("recency-matched decoys"), "points": [(0, 1.0), (4, 0.062), (16, 0.062)]},
            {"name": T("nominal 1/16"), "points": [(0, 0.062), (16, 0.062)], "dashed": True},
        ],
        title=T("Observer's chance of naming the spent note, ring of 16"), xlabel=T("other settlements between being paid and paying"), ylabel=T("probability"),
        caption=T("With no traffic the ring is worth nothing under either rule. With sixteen settlements of traffic, recency-matched decoys reach the nominal figure exactly; uniform decoys leave the observer at 5.8× it. Artifact: rings.json (host-a)."))
    c["placement"] = bar_chart(
        [(T("same rack|0 ms"), 0.166), (T("same metro|1 ms"), 0.617), (T("domestic|5 ms"), 1.619), (T("Tokyo–Singapore|15 ms"), 3.876), (T("six near,|one at 120 ms"), 22.998, 1), (T("all far|120 ms"), 26.148, 1)],
        title=T("One RFQ quote, 16 makers, by node placement"), ylabel=T("seconds (log scale)"), logy=True, unit=" s",
        caption=T("70 rounds, flat in makers and assets, so the wall clock is 70 × RTT of the slowest link. One distant node costs 86% of moving all seven. Artifacts: placement.json, sites.json (delay proxy on one host)."))
    c["batching"] = line_chart(
        [{"name": T("ms per quote at 15 ms one way"), "points": [(1, 3425), (2, 1839), (4, 1007), (8, 574), (16, 377), (32, 284)]}],
        title=T("Requests per MPC job against time per quote"), xlabel=T("requests in one job, Q (log scale)"), ylabel=T("ms per quote"), logx=True,
        caption=T("Rounds belong to the job, not the request: 69 rounds at Q=1, 5.5 per quote at Q=32. The job itself takes 9.1 s at Q=32, so one user's wait rises as throughput improves. Artifact: rounds.json."))
    c["netting"] = bar_chart(
        [(T("gross-gross"), 400.0), (T("gross-net"), 320.1), (T("net-net"), 247.5), (T("net-net|+ attested"), 20.6, 2)],
        title=T("Settlement verification, 64 trades, 8 participants"), ylabel=T("ms total"), unit=" ms",
        caption=T("Netting removes range proofs but not the per-trade zkPI verification (3.5 ms each). Signing the cycle rather than each trade removes that, at the price of third-party verifiability of the allocation. Artifact: defmi.json."))
    c["rounds"] = bar_chart(
        [(T("inputs, reference,|price arithmetic"), 10), (T("+ direction|selection"), 1), (T("+ eligibility|gates"), 9), (T("+ binary|tournament"), 32, 1)],
        title=T("Where the MPC rounds go, 16 makers"), ylabel=T("rounds added"), unit="",
        caption=T("The tournament is 62% of the depth and the eligibility layer 17%; the pricing arithmetic is effectively nothing. Only sequential depth of comparisons matters. Artifact: stages.json."))
    c["vetting"] = line_chart(
        [
            {"name": T("verify, ms"), "points": [(4, 0.66), (8, 0.96), (16, 1.33), (32, 1.82), (64, 2.61), (128, 3.84)]},
            {"name": T("prove, ms"), "points": [(4, 0.81), (8, 1.25), (16, 1.88), (32, 2.91), (64, 4.90), (128, 9.02)]},
        ],
        title=T("Vetting proof against crowd size"), xlabel=T("crowd (log scale)"), ylabel=T("ms"), logx=True,
        caption=T("Predicted to double with the crowd; grew about 1.4× per doubling instead, the batched multi-scalar multiplication showing through. That miss moved the default crowd from 16 to 128. Artifact: vetting.json."))
    c["audit_cost"] = bar_chart(
        [(T("Rivinius 2022|verifiable + blame + robust"), 20, 3), (T("Rivinius 2022|(100 ms RTT)"), 11, 3), (T("zkFMI|verifiable, traffic"), 2.0), (T("zkFMI|verifiable, wall clock"), 1.07)],
        title=T("What making the computation checkable costs, × plain protocol"), ylabel=T("multiple"), unit="×",
        caption=T("Different regimes, stated in both directions: their construction delivers blame and robustness, this one does not; their overhead is inside every multiplication, this one is a wider field. Artifacts: binding_chain.json, matched_field.json."))
    return c
