# Fatima Islam — Data Analyst Portfolio

A self-contained portfolio website, six interactive dashboards, downloadable Tableau
workbooks, a one-page résumé, and a written case study. All plain HTML/CSS/SVG — no
build tools, no server. Opens in any browser and hosts anywhere.

## Structure

```
portfolio/
├── index.html                       ← the portfolio site (start here)
├── resume.html                      ← one-page résumé (matches the site)
├── Fatima_Islam_Resume.pdf          ← print-ready PDF of the résumé
├── dashboards/                      ← the six interactive dashboards
│   ├── health-crude-vs-asr.html
│   ├── housing-young-renters.html
│   ├── gender-pay-gap.html
│   ├── simpsons-paradox.html
│   ├── inflation-drivers.html
│   └── population-immigration.html
├── case-studies/
│   └── housing-young-renters.html   ← problem / approach / finding write-up
├── workbooks/                       ← downloadable Tableau .twbx for all six
│   ├── health_cancer_mortality.twbx
│   ├── housing_young_renters.twbx
│   ├── gender_pay_gap.twbx
│   ├── simpsons_paradox.twbx
│   ├── inflation_drivers.twbx
│   └── population_immigration.twbx
├── data/                            ← tidy CSVs behind the workbooks
├── build_portfolio.py · build_project6.py · build_workbooks.py
└── README.md
```

Open `index.html` (with the whole folder present) and every link works: each card
opens its dashboard, downloads its `.twbx`, and the housing card also links to the
case study. There's a Résumé button in the header.

## Before you publish — three edits

1. **LinkedIn URL** — replace `https://www.linkedin.com/in/your-profile` everywhere
   (in `index.html`, `resume.html`, and `case-studies/`).
2. **Résumé placeholders** — in `resume.html` the highlighted spots (Experience,
   Education, City, portfolio URL, certifications) are yours to fill in. Re-export the
   PDF after editing (open `resume.html`, print → Save as PDF, Letter, no margins), or
   ask me to regenerate it.
3. **Confirm the email** is the one you want public.

## Publish it (free)

- **GitHub Pages:** push this folder to a repo → Settings → Pages → deploy from
  `main`/root.
- **Netlify / Cloudflare Pages:** drag the `portfolio` folder onto the dashboard;
  it's live in seconds with a shareable URL.

## The six projects

Each is built from a real, cited source and follows one idea — where a headline
number misleads and what segmenting reveals:

1. **Health / data literacy** — crude vs. age-standardized cancer mortality (StatCan).
2. **Housing / equity** — recent & young renters' cost burden, 2021 Census. *(+ case study)*
3. **Labour / equity** — intersectional gender wage gap (Labour Force Survey, 2025).
4. **Method / statistics** — Simpson's paradox, Berkeley 1973 admissions (Bickel et al., 1975).
5. **Prices / time series** — CPI component spread behind the headline (StatCan, June 2026).
6. **Demographics / composition** — Canada's 2025 population decline and components of change (StatCan).

## About the Tableau workbooks

Each `.twbx` bundles its data and opens in Tableau Desktop or free Tableau Public.
They were authored programmatically (built without Tableau on hand to test-open), so
the XML is standard and the data is bundled; if a version is fussy, the tidy CSVs in
`data/` rebuild any dashboard in minutes. The health and housing workbooks also have
fuller standalone project folders (data + docs) delivered separately.

## Regenerate

```bash
python3 build_workbooks.py   # the six .twbx + tidy CSVs (3–6)
python3 build_portfolio.py   # dashboards 03–05
python3 build_project6.py    # dashboard 06
```
