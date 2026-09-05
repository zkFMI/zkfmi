"""Tiny SVG chart generator for zkfmi.com. Standard library only.

Every chart is an inline <svg> that uses CSS custom properties for colour so it
follows the page theme. Data lives here next to the artifact it came from.
"""
import math

COLORS = ["var(--accent)", "var(--accent-2)", "var(--accent-3)", "var(--danger)", "var(--fg-2)"]

def _fmt(v):
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
    # legend
    lx = ml + 8
    for i, s in enumerate(series):
        c = COLORS[i % len(COLORS)]
        out.append(f'<rect x="{lx}" y="{mt+8+i*16}" width="14" height="3" fill="{c}"/>')
        out.append(f'<text class="cl" x="{lx+20}" y="{mt+13+i*16}">{s["name"]}</text>')
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

def all_charts():
    c = {}
    c["settle_width"] = line_chart(
        [
            {"name": "linear backend, settle (host-c)", "points": [(8, 8.5), (16, 14.8), (24, 21.2), (32, 27.6), (40, 34.0), (48, 40.6)]},
            {"name": "Bulletproof backend, settle (host-a)", "points": [(8, 2.09), (16, 2.78), (32, 4.26), (64, 7.02)]},
        ],
        title="Settlement cost against balance width", xlabel="balance width, bits", ylabel="ms per DvP",
        caption="Verification is linear in the width for the bit-decomposition backend (0.80 ms/bit, 2.1 ms intercept for the instruction itself) and roughly logarithmic for Bulletproofs. Hosts differ; see calibration. Artifacts: defmi.json, rust_bench.json.")
    c["package_width"] = line_chart(
        [
            {"name": "linear backend", "points": [(8, 29267), (16, 36435), (24, 43603), (32, 50771), (40, 57939), (48, 65107)]},
            {"name": "Bulletproof backend", "points": [(8, 2656), (16, 2912), (32, 3168), (64, 3424)]},
        ],
        title="Settlement package size against balance width", xlabel="balance width, bits", ylabel="bytes", logy=True,
        caption="896 B per bit on the linear backend against a package that barely moves with Bulletproofs: 3,424 B at 64 bits.")
    c["ring"] = line_chart(
        [
            {"name": "prove, payer's device", "points": [(2, 10.9), (4, 11.2), (8, 11.3), (16, 11.7), (32, 12.7), (64, 14.5), (128, 18.2), (256, 26.2), (512, 40.3)]},
            {"name": "verify, settlement node", "points": [(2, 1.8), (4, 2.1), (8, 2.4), (16, 2.6), (32, 3.1), (64, 3.7), (128, 4.7), (256, 6.4), (512, 9.3)]},
        ],
        title="Note ring: who pays for the anonymity set", xlabel="ring size (log scale)", ylabel="ms", logx=True,
        caption="The wire grows 224 B per doubling and verification stays under 10 ms to a ring of 512. Proving is what grows, so the payer caps the ring, not the node. Artifact: defmi.json.")
    c["ring_worth"] = line_chart(
        [
            {"name": "uniform decoys", "points": [(0, 1.0), (4, 0.547), (16, 0.359)]},
            {"name": "recency-matched decoys", "points": [(0, 1.0), (4, 0.062), (16, 0.062)]},
            {"name": "nominal 1/16", "points": [(0, 0.062), (16, 0.062)], "dashed": True},
        ],
        title="Observer's chance of naming the spent note, ring of 16", xlabel="other settlements between being paid and paying", ylabel="probability",
        caption="With no traffic the ring is worth nothing under either rule. With sixteen settlements of traffic, recency-matched decoys reach the nominal figure exactly; uniform decoys leave the observer at 5.8× it. Artifact: rings.json (host-a).")
    c["placement"] = bar_chart(
        [("same rack|0 ms", 0.166), ("same metro|1 ms", 0.617), ("domestic|5 ms", 1.619), ("Tokyo–Singapore|15 ms", 3.876), ("six near,|one at 120 ms", 22.998, 1), ("all far|120 ms", 26.148, 1)],
        title="One RFQ quote, 16 makers, by node placement", ylabel="seconds (log scale)", logy=True, unit=" s",
        caption="70 rounds, flat in makers and assets, so the wall clock is 70 × RTT of the slowest link. One distant node costs 86% of moving all seven. Artifacts: placement.json, sites.json (delay proxy on one host).")
    c["batching"] = line_chart(
        [{"name": "ms per quote at 15 ms one way", "points": [(1, 3425), (2, 1839), (4, 1007), (8, 574), (16, 377), (32, 284)]}],
        title="Requests per MPC job against time per quote", xlabel="requests in one job, Q (log scale)", ylabel="ms per quote", logx=True,
        caption="Rounds belong to the job, not the request: 69 rounds at Q=1, 5.5 per quote at Q=32. The job itself takes 9.1 s at Q=32, so one user's wait rises as throughput improves. Artifact: rounds.json.")
    c["netting"] = bar_chart(
        [("gross-gross", 400.0), ("gross-net", 320.1), ("net-net", 247.5), ("net-net|+ attested", 20.6, 2)],
        title="Settlement verification, 64 trades, 8 participants", ylabel="ms total", unit=" ms",
        caption="Netting removes range proofs but not the per-trade zkPI verification (3.5 ms each). Signing the cycle rather than each trade removes that, at the price of third-party verifiability of the allocation. Artifact: defmi.json.")
    c["rounds"] = bar_chart(
        [("inputs, reference,|price arithmetic", 10), ("+ direction|selection", 1), ("+ eligibility|gates", 9), ("+ binary|tournament", 32, 1)],
        title="Where the MPC rounds go, 16 makers", ylabel="rounds added", unit="",
        caption="The tournament is 62% of the depth and the eligibility layer 17%; the pricing arithmetic is effectively nothing. Only sequential depth of comparisons matters. Artifact: stages.json.")
    c["vetting"] = line_chart(
        [
            {"name": "verify, ms", "points": [(4, 0.66), (8, 0.96), (16, 1.33), (32, 1.82), (64, 2.61), (128, 3.84)]},
            {"name": "prove, ms", "points": [(4, 0.81), (8, 1.25), (16, 1.88), (32, 2.91), (64, 4.90), (128, 9.02)]},
        ],
        title="Vetting proof against crowd size", xlabel="crowd (log scale)", ylabel="ms", logx=True,
        caption="Predicted to double with the crowd; grew about 1.4× per doubling instead, the batched multi-scalar multiplication showing through. That miss moved the default crowd from 16 to 128. Artifact: vetting.json.")
    c["audit_cost"] = bar_chart(
        [("Rivinius 2022|verifiable + blame + robust", 20, 3), ("Rivinius 2022|(100 ms RTT)", 11, 3), ("zkFMI|verifiable, traffic", 2.0), ("zkFMI|verifiable, wall clock", 1.07)],
        title="What making the computation checkable costs, × plain protocol", ylabel="multiple", unit="×",
        caption="Different regimes, stated in both directions: their construction delivers blame and robustness, this one does not; their overhead is inside every multiplication, this one is a wider field. Artifacts: binding_chain.json, matched_field.json.")
    return c
