#!/usr/bin/env python3
"""Build 3 new interactive dashboards + the portfolio index site.
Self-contained HTML, dataviz-skill palette, real StatCan / published data."""
import os, shutil
ROOT = os.path.dirname(os.path.abspath(__file__))
DASH = os.path.join(ROOT, "dashboards")
os.makedirs(DASH, exist_ok=True)

# ---------- shared CSS ----------
CSS = """
 :root{color-scheme:light dark}
 .viz-root{--surface-1:#fcfcfb;--page:#f9f9f7;--text-primary:#0b0b0b;--text-secondary:#52514e;
   --muted:#898781;--grid:#e1e0d9;--series-1:#2a78d6;--series-2:#eb6834;--series-3:#1baf7a;
   --neutral:#898781;--crit:#d03b3b;--good:#006300}
 @media (prefers-color-scheme:dark){:root:where(:not([data-theme='light'])) .viz-root{
   --surface-1:#1a1a19;--page:#0d0d0d;--text-primary:#fff;--text-secondary:#c3c2b7;
   --muted:#898781;--grid:#2c2c2a;--series-1:#3987e5;--series-2:#d95926;--series-3:#199e70;
   --neutral:#a5a39a;--crit:#e66767;--good:#0ca30c}}
 *{box-sizing:border-box} body{margin:0;background:var(--page);color:var(--text-primary);
   font-family:system-ui,-apple-system,'Segoe UI',sans-serif;line-height:1.5}
 .viz-root{max-width:1120px;margin:0 auto;padding:26px 22px 44px}
 .back{font-size:13px;color:var(--series-1);text-decoration:none} .back:hover{text-decoration:underline}
 h1{font-size:22px;margin:10px 0 4px} p.sub{margin:0;color:var(--text-secondary);font-size:14px;max-width:82ch}
 .kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:14px;margin:22px 0}
 .kpi{background:var(--surface-1);border:1px solid rgba(11,11,11,.10);border-radius:12px;padding:14px 16px}
 .kpi .n{font-size:25px;font-weight:700} .kpi .l{font-size:12.5px;color:var(--text-secondary);margin-top:2px}
 .grid-wrap{display:grid;grid-template-columns:1fr 1fr;gap:16px}
 .card{background:var(--surface-1);border:1px solid rgba(11,11,11,.10);border-radius:12px;padding:16px 18px}
 .card.span2{grid-column:1/-1}
 .card h2{font-size:15px;margin:0 0 2px} .card p.note{font-size:12.5px;color:var(--text-secondary);margin:0 0 10px}
 .legend{display:flex;gap:16px;flex-wrap:wrap;font-size:12.5px;color:var(--text-secondary);margin:2px 0 8px}
 .legend span{display:inline-flex;align-items:center;gap:6px} .sw{width:12px;height:12px;border-radius:3px}
 .grid{stroke:var(--grid);stroke-width:1} .ref{stroke:var(--crit);stroke-width:1.4;stroke-dasharray:4 3}
 .ytick,.xlab,.vlab{fill:var(--muted);font-family:system-ui} .ytick{font-size:9px}
 .xlab{font-size:11px;fill:var(--text-secondary)} .vlab{font-size:10.5px;fill:var(--text-primary);font-weight:600}
 .takeaway{margin-top:20px;background:var(--surface-1);border:1px solid rgba(11,11,11,.10);
   border-left:4px solid var(--series-1);border-radius:10px;padding:14px 18px;font-size:14px}
 footer{margin-top:16px;font-size:12px;color:var(--muted)} a{color:var(--series-1)}
"""

def page(title, body):
    return f"""<!DOCTYPE html><html lang='en'><head><meta charset='utf-8'/>
<meta name='viewport' content='width=device-width, initial-scale=1'/><title>{title}</title>
<style>{CSS}</style></head><body><div class='viz-root'>
<a class='back' href='../index.html'>&larr; Back to portfolio</a>
{body}
</div></body></html>"""

# ---------- SVG helpers ----------
def grouped_bars(pairs, ymax, w, h, colors, unit="", pad_l=38, pad_b=30, pad_t=14, ref=None, ticks=6, pctlab=False):
    plot_w=w-pad_l-10; plot_h=h-pad_b-pad_t; ng=len(pairs); gw=plot_w/ng
    s=[f"<svg viewBox='0 0 {w} {h}' width='100%' role='img'>"]
    for i in range(0,ticks):
        val=ymax*i/(ticks-1); yy=pad_t+plot_h-(val/ymax)*plot_h
        s.append(f"<line x1='{pad_l}' y1='{yy:.1f}' x2='{w-10}' y2='{yy:.1f}' class='grid'/>")
        s.append(f"<text x='{pad_l-4}' y='{yy+3:.1f}' class='ytick' text-anchor='end'>{val:.0f}</text>")
    if ref is not None:
        yy=pad_t+plot_h-(ref/ymax)*plot_h
        s.append(f"<line x1='{pad_l}' y1='{yy:.1f}' x2='{w-10}' y2='{yy:.1f}' class='ref'/>")
        s.append(f"<text x='{w-12}' y='{yy-4:.1f}' class='xlab' text-anchor='end' fill='var(--crit)'>parity (100)</text>")
    for gi,(glabel,series) in enumerate(pairs):
        n=len(series); bw=min(46,(gw-16)/max(n,1)); gx=pad_l+gi*gw+(gw-bw*n-5*(n-1))/2
        for si,(slabel,val) in enumerate(series):
            color=colors[slabel] if isinstance(colors,dict) else colors[si]
            bh=(val/ymax)*plot_h; x=gx+si*(bw+5); yy=pad_t+plot_h-bh
            s.append(f"<rect x='{x:.1f}' y='{yy:.1f}' width='{bw:.1f}' height='{bh:.1f}' rx='3' fill='{color}'><title>{glabel} — {slabel}: {val}{unit}</title></rect>")
            lab=f"{val}{unit}"
            s.append(f"<text x='{x+bw/2:.1f}' y='{yy-4:.1f}' class='vlab' text-anchor='middle'>{lab}</text>")
        s.append(f"<text x='{pad_l+gi*gw+gw/2:.1f}' y='{h-9}' class='xlab' text-anchor='middle'>{glabel}</text>")
    s.append("</svg>"); return "".join(s)

def hbars(rows, xmax, w, h, unit="%", pad_l=150, pad_r=44, pad_t=8, pad_b=8, highlight=None):
    # rows: list of (label, value, color)
    n=len(rows); rh=(h-pad_t-pad_b)/n; plot_w=w-pad_l-pad_r
    s=[f"<svg viewBox='0 0 {w} {h}' width='100%' role='img'>"]
    for i,(label,val,color) in enumerate(rows):
        y=pad_t+i*rh; bw=(val/xmax)*plot_w if val>=0 else 0
        cy=y+rh/2
        s.append(f"<text x='{pad_l-8}' y='{cy+3:.1f}' class='xlab' text-anchor='end'>{label}</text>")
        s.append(f"<rect x='{pad_l}' y='{y+rh*0.18:.1f}' width='{bw:.1f}' height='{rh*0.64:.1f}' rx='3' fill='{color}'><title>{label}: {val}{unit}</title></rect>")
        s.append(f"<text x='{pad_l+bw+6:.1f}' y='{cy+3:.1f}' class='vlab' text-anchor='start'>{val}{unit}</text>")
    s.append("</svg>"); return "".join(s)

# ============================================================
# Dashboard 3 — Gender pay gap (intersectional)
# ============================================================
def build_paygap():
    kpi = [("88¢","earned by women per $1 by men, all employees 15+ (2025)"),
           ("89¢","among prime-age workers 25–54 (2025)"),
           ("+6¢","progress since 1997 (was 82¢)"),
           ("78¢","for racialized women — the widest gap")]
    kpihtml="".join(f"<div class='kpi'><div class='n' style='color:var(--series-1)'>{n}</div><div class='l'>{l}</div></div>" for n,l in kpi)
    # Panel 1: progress over time (1997 vs 2025), two groups
    p1=grouped_bars([("All employees 15+",[("1997",82),("2025",88)]),
                     ("Prime age 25–54",[("1997",81),("2025",89)])],
                    100,540,240,{"1997":"var(--neutral)","2025":"var(--series-1)"},unit="¢",ref=100)
    # Panel 2: intersectional (2025), cents per $1 of non-Indigenous non-racialized men
    p2=hbars([("Non-racialized women",88,"var(--series-1)"),
              ("Indigenous women",79,"var(--series-2)"),
              ("Racialized women",78,"var(--series-2)")],100,560,150,unit="¢",pad_l=176)
    body=f"""<h1>The gender wage gap persists — and it isn't the same for every woman</h1>
<p class='sub'>Women's hourly earnings as a share of men's, Canada, Labour Force Survey. The overall gap has narrowed since 1997 but has stalled near 88¢ — and racialized and Indigenous women trail further, measured against non-Indigenous, non-racialized men.</p>
<div class='kpis'>{kpihtml}</div>
<div class='grid-wrap'>
  <div class='card'><h2>1 &nbsp;Slow progress, 1997 → 2025</h2>
    <p class='note'>Cents earned by women per $1 earned by men. Dashed line = pay parity (100¢).</p>
    <div class='legend'><span><i class='sw' style='background:var(--neutral)'></i>1997</span><span><i class='sw' style='background:var(--series-1)'></i>2025</span></div>
    {p1}</div>
  <div class='card'><h2>2 &nbsp;An intersectional gap (2025)</h2>
    <p class='note'>Cents per $1 earned by non-Indigenous, non-racialized men.</p>
    {p2}</div>
</div>
<div class='takeaway'><strong>Takeaway:</strong> A single "88 cents" hides real variation. Prime-age women reach 89¢, but racialized women (78¢) and Indigenous women (79¢) sit roughly 10 cents lower — a reminder that an aggregate gender gap can mask who is furthest from parity. Segment before you conclude.</div>
<footer>Source: Statistics Canada, <a href='https://www.statcan.gc.ca/o1/en/plus/9084-gender-wage-gap-persists'>The gender wage gap persists</a> (2025, Labour Force Survey). Reference group: non-Indigenous, non-racialized men.</footer>"""
    open(os.path.join(DASH,"gender-pay-gap.html"),"w").write(page("Gender pay gap — Canada",body))

# ============================================================
# Dashboard 4 — Simpson's paradox (Berkeley 1973)
# ============================================================
def build_simpson():
    depts=[("A",825,512,108,89),("B",560,353,25,17),("C",325,120,593,202),
           ("D",417,138,375,131),("E",191,53,393,94),("F",373,22,341,24)]
    mA=sum(d[2] for d in depts); mN=sum(d[1] for d in depts)
    fA=sum(d[4] for d in depts); fN=sum(d[3] for d in depts)
    men_overall=round(mA/mN*100,1); women_overall=round(fA/fN*100,1)
    assert abs(men_overall-44.5)<0.3 and abs(women_overall-30.4)<0.3, (men_overall,women_overall)
    kpi=[(f"{men_overall:.0f}%","of men admitted overall"),
         (f"{women_overall:.0f}%","of women admitted overall"),
         ("4 of 6","departments where women were admitted at an equal or HIGHER rate"),
         ("↔","the paradox: aggregate reverses on segmentation")]
    kpihtml="".join(f"<div class='kpi'><div class='n'>{n}</div><div class='l'>{l}</div></div>" for n,l in kpi)
    p1=grouped_bars([("All applicants",[("Men",men_overall),("Women",women_overall)])],
                    100,300,230,{"Men":"var(--series-1)","Women":"var(--series-2)"},unit="%")
    pairs=[]
    for name,mn,ma,fn,fa in depts:
        pairs.append((f"Dept {name}",[("Men",round(ma/mn*100)),("Women",round(fa/fn*100))]))
    p2=grouped_bars(pairs,100,560,250,{"Men":"var(--series-1)","Women":"var(--series-2)"},unit="%")
    # Panel 3: women applied more to low-admit departments
    rows=[]
    for name,mn,ma,fn,fa in depts:
        share=round(fn/(mn+fn)*100)
        rows.append((f"Dept {name} ({round((ma+fa)/(mn+fn)*100)}% admit)",share,"var(--series-2)"))
    p3=hbars(rows,100,700,220,unit="% women")
    body=f"""<h1>Simpson's paradox: when the average lies</h1>
<p class='sub'>UC Berkeley's 1973 graduate admissions looked like clear gender bias — 44% of men admitted vs. 30% of women. But split by department, women were admitted at an equal or <em>higher</em> rate in most. The aggregate reversed because women applied disproportionately to the hardest-to-enter departments. A real, published dataset (Bickel, Hammel & O'Connell, <em>Science</em>, 1975).</p>
<div class='kpis'>{kpihtml}</div>
<div class='grid-wrap'>
  <div class='card'><h2>1 &nbsp;The headline: looks like bias</h2>
    <p class='note'>Overall admission rate, six largest departments.</p>
    <div class='legend'><span><i class='sw' style='background:var(--series-1)'></i>Men</span><span><i class='sw' style='background:var(--series-2)'></i>Women</span></div>
    {p1}</div>
  <div class='card'><h2>2 &nbsp;Split by department: it flips</h2>
    <p class='note'>Admission rate by department. Women ≥ men in A, B, D, F.</p>
    <div class='legend'><span><i class='sw' style='background:var(--series-1)'></i>Men</span><span><i class='sw' style='background:var(--series-2)'></i>Women</span></div>
    {p2}</div>
  <div class='card span2'><h2>3 &nbsp;Why: women applied to the competitive departments</h2>
    <p class='note'>Share of each department's applicants who were women. Women concentrated in departments C–F, which admitted far fewer applicants overall (the % next to each label is that department's overall admit rate).</p>
    {p3}</div>
</div>
<div class='takeaway'><strong>Takeaway:</strong> A lurking variable — which department people applied to — reversed the story. The overall rate wasn't measuring bias; it was measuring where men and women applied. Whenever groups differ in composition, always check whether an aggregate holds up once you segment.</div>
<footer>Source: P. J. Bickel, E. A. Hammel, J. W. O'Connell, "Sex Bias in Graduate Admissions: Data from Berkeley," <em>Science</em> 187 (1975); the canonical <code>UCBAdmissions</code> dataset (six largest departments).</footer>"""
    open(os.path.join(DASH,"simpsons-paradox.html"),"w").write(page("Simpson's paradox — Berkeley admissions",body))

# ============================================================
# Dashboard 5 — What's driving inflation (June 2026 CPI)
# ============================================================
def build_inflation():
    kpi=[("2.8%","headline all-items inflation, June 2026 (year-over-year)"),
         ("+20.5%","gasoline — 7× the headline"),
         ("+1.5%","shelter — well below headline"),
         ("weights","why a 20% jump barely moves 2.8%")]
    kpihtml="".join(f"<div class='kpi'><div class='n' style='color:var(--series-1)'>{n}</div><div class='l'>{l}</div></div>" for n,l in kpi)
    comps=[("Gasoline",20.5,"var(--series-2)"),("Transportation",6.7,"var(--series-2)"),
           ("Food from stores",3.9,"var(--series-2)"),("All-items (CPI)",2.8,"var(--series-1)"),
           ("Shelter",1.5,"var(--neutral)")]
    p1=hbars(comps,22,640,220,unit="%",pad_l=130)
    p2=grouped_bars([("Gasoline, YoY",[("May 2026",33.2),("June 2026",20.5)])],
                    40,420,230,{"May 2026":"var(--neutral)","June 2026":"var(--series-2)"},unit="%",ticks=5)
    body=f"""<h1>What's actually driving inflation? The headline hides the spread</h1>
<p class='sub'>Canada's all-items CPI rose 2.8% year-over-year in June 2026. But "2.8%" is a weighted blend of components moving very differently — gasoline up 20.5%, shelter up just 1.5%. The single number tells you almost nothing about what a given household actually feels.</p>
<div class='kpis'>{kpihtml}</div>
<div class='grid-wrap'>
  <div class='card span2'><h2>1 &nbsp;Component inflation vs. the 2.8% headline (June 2026, YoY)</h2>
    <p class='note'>Year-over-year price change by component. The blue bar is the all-items headline; components spread far above and below it.</p>
    {p1}</div>
  <div class='card'><h2>2 &nbsp;Why the headline stays calm</h2>
    <p class='note'>Gasoline is volatile but a small slice of the basket, so even a 20% swing moves the index only modestly — and it's already decelerating from May.</p>
    <div class='legend'><span><i class='sw' style='background:var(--neutral)'></i>May 2026</span><span><i class='sw' style='background:var(--series-2)'></i>June 2026</span></div>
    {p2}</div>
  <div class='card'><h2>3 &nbsp;The data-literacy point</h2>
    <p class='note' style='font-size:13.5px;line-height:1.55'>A headline rate is an <strong>average weighted by spending shares</strong>. Households that drive a lot, or spend more on groceries, experience an inflation rate well above 2.8%. When you read "inflation is X%", ask: which basket, and whose?</p>
  </div>
</div>
<div class='takeaway'><strong>Takeaway:</strong> One inflation number is a weighted average, not a universal experience. The spread across components — and each household's own basket — is where the real story lives. Always decompose the index before drawing conclusions.</div>
<footer>Source: Statistics Canada, <a href='https://www150.statcan.gc.ca/n1/daily-quotidien/260720/dq260720a-eng.htm'>Consumer Price Index, June 2026</a> (The Daily).</footer>"""
    open(os.path.join(DASH,"inflation-drivers.html"),"w").write(page("What's driving inflation — Canada",body))

build_paygap(); build_simpson(); build_inflation()
print("Built 3 dashboards:", [f for f in os.listdir(DASH) if f.endswith('.html')])
