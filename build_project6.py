#!/usr/bin/env python3
"""Build dashboard 6: Canada's population fell in 2025 (immigration-driven)."""
import os
ROOT=os.path.dirname(os.path.abspath(__file__)); DASH=os.path.join(ROOT,"dashboards")
CSS="""
 :root{color-scheme:light dark}
 .viz-root{--surface-1:#fcfcfb;--page:#f9f9f7;--text-primary:#0b0b0b;--text-secondary:#52514e;
   --muted:#898781;--grid:#e1e0d9;--series-1:#2a78d6;--good:#0ca30c;--crit:#d03b3b;--neutral:#898781}
 @media (prefers-color-scheme:dark){:root:where(:not([data-theme='light'])) .viz-root{
   --surface-1:#1a1a19;--page:#0d0d0d;--text-primary:#fff;--text-secondary:#c3c2b7;
   --muted:#8f8d86;--grid:#2c2c2a;--series-1:#3987e5;--good:#0ca30c;--crit:#e66767;--neutral:#a5a39a}}
 *{box-sizing:border-box} body{margin:0;background:var(--page);color:var(--text-primary);
   font-family:system-ui,-apple-system,'Segoe UI',sans-serif;line-height:1.55}
 .viz-root{max-width:1120px;margin:0 auto;padding:26px 22px 44px}
 .back{font-size:13px;color:var(--series-1);text-decoration:none}
 h1{font-size:22px;margin:10px 0 4px} p.sub{margin:0;color:var(--text-secondary);font-size:14px;max-width:82ch}
 .kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:14px;margin:22px 0}
 .kpi{background:var(--surface-1);border:1px solid rgba(11,11,11,.10);border-radius:12px;padding:14px 16px}
 .kpi .n{font-size:24px;font-weight:700} .kpi .l{font-size:12.5px;color:var(--text-secondary);margin-top:2px}
 .grid-wrap{display:grid;grid-template-columns:1fr 1fr;gap:16px}
 .card{background:var(--surface-1);border:1px solid rgba(11,11,11,.10);border-radius:12px;padding:16px 18px}
 .card.span2{grid-column:1/-1}
 .card h2{font-size:15px;margin:0 0 2px} .card p.note{font-size:12.5px;color:var(--text-secondary);margin:0 0 10px}
 .grid{stroke:var(--grid);stroke-width:1} .zero{stroke:var(--baseline,#c3c2b7);stroke-width:1.3}
 .xlab,.vlab{fill:var(--muted);font-family:system-ui} .xlab{font-size:11px;fill:var(--text-secondary)}
 .vlab{font-size:11px;fill:var(--text-primary);font-weight:600}
 .takeaway{margin-top:20px;background:var(--surface-1);border:1px solid rgba(11,11,11,.10);
   border-left:4px solid var(--series-1);border-radius:10px;padding:14px 18px;font-size:14px}
 footer{margin-top:16px;font-size:12px;color:var(--muted)} a{color:var(--series-1)}
"""
def vbar_signed(pairs, ymin, ymax, w, h, pad_l=52, pad_b=28, pad_t=14):
    plot_w=w-pad_l-12; plot_h=h-pad_b-pad_t; n=len(pairs); gw=plot_w/n
    def yy(v): return pad_t+plot_h-(v-ymin)/(ymax-ymin)*plot_h
    s=[f"<svg viewBox='0 0 {w} {h}' width='100%' role='img'>"]
    zero=yy(0)
    for gl in range(int(ymin),int(ymax)+1,100000):
        y=yy(gl); s.append(f"<line x1='{pad_l}' y1='{y:.1f}' x2='{w-12}' y2='{y:.1f}' class='grid'/>")
        s.append(f"<text x='{pad_l-5}' y='{y+3:.1f}' class='xlab' text-anchor='end' style=\"font-size:9px\">{gl//1000}k</text>")
    s.append(f"<line x1='{pad_l}' y1='{zero:.1f}' x2='{w-12}' y2='{zero:.1f}' class='zero'/>")
    for i,(label,val) in enumerate(pairs):
        color="var(--good)" if val>=0 else "var(--crit)"
        bw=min(70,gw*0.5); x=pad_l+i*gw+(gw-bw)/2
        top=yy(max(val,0)); bh=abs(yy(val)-zero)
        s.append(f"<rect x='{x:.1f}' y='{top:.1f}' width='{bw:.1f}' height='{bh:.1f}' rx='3' fill='{color}'><title>{label}: {val:+,}</title></rect>")
        ly=(top-6) if val>=0 else (yy(val)+15)
        s.append(f"<text x='{x+bw/2:.1f}' y='{ly:.1f}' class='vlab' text-anchor='middle'>{val:+,}</text>")
        s.append(f"<text x='{x+bw/2:.1f}' y='{h-9}' class='xlab' text-anchor='middle'>{label}</text>")
    s.append("</svg>"); return "".join(s)

p1=vbar_signed([("2023",256804),("2024",80385),("2025",-103504)],-200000,300000,540,250)
p2=vbar_signed([("H1 2025",77136),("H2 2025",-179572)],-200000,300000,420,250)
kpi=[("41.47M","population, Jan 1 2026"),
     ("−0.2%","population change in 2025 (−102,436) — a reversal from record growth"),
     ("−781","natural increase, Q4 2025: deaths outnumbered births"),
     ("−171,296","non-permanent residents in Q4 2025 as permits were cut")]
kpihtml="".join(f"<div class='kpi'><div class='n' style='color:var(--crit)'>{n}</div><div class='l'>{l}</div></div>" for n,l in kpi)

body=f"""<!DOCTYPE html><html lang='en'><head><meta charset='utf-8'/>
<meta name='viewport' content='width=device-width, initial-scale=1'/><title>Canada's population fell in 2025</title>
<style>{CSS}</style></head><body><div class='viz-root'>
<a class='back' href='../index.html'>&larr; Back to portfolio</a>
<h1>The growth was immigration all along: Canada's population fell in 2025</h1>
<p class='sub'>For years Canada's population climbed fast — almost entirely on international migration, not births. When immigration policy tightened in 2025 (non-permanent resident permits cut) and natural increase slipped below zero, the total population actually <strong>declined</strong> — the first annual drop in modern records. A case study in how a headline metric driven by one input reverses when that input changes.</p>
<div class='kpis'>{kpihtml}</div>
<div class='grid-wrap'>
  <div class='card'><h2>1 &nbsp;Fourth-quarter population change, by year</h2>
    <p class='note'>Net change in population during Q4 (Oct 1 → Jan 1). Green = growth, red = decline.</p>
    {p1}</div>
  <div class='card'><h2>2 &nbsp;2025 turned mid-year</h2>
    <p class='note'>The first half still grew; the second half more than erased it.</p>
    {p2}</div>
  <div class='card span2'><h2>3 &nbsp;Why it reversed</h2>
    <p class='note' style='font-size:13.5px;line-height:1.6'>Two things fell together. <strong>Natural increase</strong> (births minus deaths) turned <strong>negative (−781 in Q4 2025)</strong> — an aging population now has more deaths than births, so it adds nothing to growth. That left <strong>international migration</strong> as effectively the only source of growth. So when the government cut non-permanent resident permits — <strong>−171,296 non-permanent residents in Q4 2025</strong>, and permanent admissions down 19.6% year-over-year — the one engine of growth went into reverse and the population shrank. The lesson: when a total depends on a single component, the total <em>is</em> that component.</p></div>
</div>
<div class='takeaway'><strong>Takeaway:</strong> A number's trend can flip entirely on one input. Canada's population "growth" had quietly become a synonym for immigration; watching the aggregate hid that fragility. When a metric rides on one driver, track the driver — not the headline.</div>
<footer>Source: Statistics Canada, <a href='https://www150.statcan.gc.ca/n1/daily-quotidien/260318/dq260318b-eng.htm'>Canada's population estimates, fourth quarter 2025</a> (The Daily). Q4 net change 2023/2024/2025 and 2025 half-year figures as reported.</footer>
</div></body></html>"""
open(os.path.join(DASH,"population-immigration.html"),"w").write(body)
print("wrote population-immigration.html")
