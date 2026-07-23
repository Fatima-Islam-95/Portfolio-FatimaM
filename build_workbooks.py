#!/usr/bin/env python3
"""Build packaged Tableau workbooks (.twbx) for portfolio dashboards 3-6.
One tidy CSV per project drives one workbook (federated text connection)."""
import os, csv, zipfile, shutil, xml.dom.minidom as minidom

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data")
WB = os.path.join(ROOT, "workbooks")
os.makedirs(DATA, exist_ok=True); os.makedirs(WB, exist_ok=True)

TIDY_COLS = [("panel","string","dimension","nominal"),
             ("category","string","dimension","ordinal"),
             ("series","string","dimension","nominal"),
             ("value","real","measure","quantitative"),
             ("unit","string","dimension","nominal"),
             ("source_type","string","dimension","nominal")]
CAP = {"panel":"Panel","category":"Category","series":"Series","value":"Value","unit":"Unit","source_type":"Source type"}
RT = {"string":"129","integer":"20","real":"5"}

# -------- datasets: (slug, csv_name, ds_id, [tidy rows], {panel:(mark,color)}) --------
def rows_paygap():
    r=[("1. Progress 1997-2025","All employees 15+","1997",82,"cents","Official"),
       ("1. Progress 1997-2025","All employees 15+","2025",88,"cents","Official"),
       ("1. Progress 1997-2025","Prime age 25-54","1997",81,"cents","Official"),
       ("1. Progress 1997-2025","Prime age 25-54","2025",89,"cents","Official"),
       ("2. Intersectional gap 2025","Non-racialized women","Cents per dollar",88,"cents","Official"),
       ("2. Intersectional gap 2025","Indigenous women","Cents per dollar",79,"cents","Official"),
       ("2. Intersectional gap 2025","Racialized women","Cents per dollar",78,"cents","Official")]
    panels={"1. Progress 1997-2025":("Bar",True),"2. Intersectional gap 2025":("Bar",False)}
    return r,panels

def rows_simpson():
    dept=[("A",62,82),("B",63,68),("C",37,34),("D",33,35),("E",28,24),("F",6,7)]
    womenshare={"A":12,"B":4,"C":65,"D":47,"E":67,"F":48}
    r=[("1. Overall admit rate","All applicants","Men",44.5,"%","Official"),
       ("1. Overall admit rate","All applicants","Women",30.4,"%","Official")]
    for d,m,w in dept:
        r.append(("2. Admit rate by department",f"Dept {d}","Men",m,"%","Official"))
        r.append(("2. Admit rate by department",f"Dept {d}","Women",w,"%","Official"))
    for d,_,_ in dept:
        r.append(("3. Share of applicants who are women",f"Dept {d}","% women",womenshare[d],"%","Official"))
    panels={"1. Overall admit rate":("Bar",True),"2. Admit rate by department":("Bar",True),
            "3. Share of applicants who are women":("Bar",False)}
    return r,panels

def rows_cpi():
    r=[("1. Component inflation (June 2026 YoY)","Gasoline","YoY %",20.5,"%","Official"),
       ("1. Component inflation (June 2026 YoY)","Transportation","YoY %",6.7,"%","Official"),
       ("1. Component inflation (June 2026 YoY)","Food from stores","YoY %",3.9,"%","Official"),
       ("1. Component inflation (June 2026 YoY)","All-items (CPI)","YoY %",2.8,"%","Official"),
       ("1. Component inflation (June 2026 YoY)","Shelter","YoY %",1.5,"%","Official"),
       ("2. Gasoline decelerating","May 2026","Gasoline YoY",33.2,"%","Official"),
       ("2. Gasoline decelerating","June 2026","Gasoline YoY",20.5,"%","Official")]
    panels={"1. Component inflation (June 2026 YoY)":("Bar",False),"2. Gasoline decelerating":("Bar",False)}
    return r,panels

def rows_pop():
    r=[("1. Q4 population change by year","2023","People",256804,"persons","Official"),
       ("1. Q4 population change by year","2024","People",80385,"persons","Official"),
       ("1. Q4 population change by year","2025","People",-103504,"persons","Official"),
       ("2. 2025 within the year","H1 2025","People",77136,"persons","Official"),
       ("2. 2025 within the year","H2 2025","People",-179572,"persons","Official")]
    panels={"1. Q4 population change by year":("Bar",False),"2. 2025 within the year":("Bar",False)}
    return r,panels

DATASETS = [
    ("gender-pay-gap","pay_gap_tidy.csv","federated.paygap01","Gender pay gap",*rows_paygap()),
    ("simpsons-paradox","berkeley_tidy.csv","federated.berkeley01","Simpson's paradox (Berkeley)",*rows_simpson()),
    ("inflation-drivers","cpi_tidy.csv","federated.cpi01","Inflation drivers (CPI June 2026)",*rows_cpi()),
    ("population-immigration","population_tidy.csv","federated.pop01","Population & immigration",*rows_pop()),
]

def write_csv(path, rows):
    with open(path,"w",newline="") as f:
        w=csv.writer(f); w.writerow([c[0] for c in TIDY_COLS]); w.writerows(rows)

def rel_cols():
    return "\n".join(f"          <column datatype='{dt}' name='{n}' ordinal='{i}' />" for i,(n,dt,_,_) in enumerate(TIDY_COLS))
def meta(csvname):
    out=[]
    for i,(n,dt,role,_) in enumerate(TIDY_COLS):
        agg="Sum" if role=="measure" else "Count"
        out.append(f"""        <metadata-record class='column'>
          <remote-name>{n}</remote-name><remote-type>{RT[dt]}</remote-type>
          <local-name>[{n}]</local-name><parent-name>[{csvname.replace('.csv','')}#csv]</parent-name>
          <remote-alias>{n}</remote-alias><ordinal>{i}</ordinal>
          <local-type>{dt}</local-type><aggregation>{agg}</aggregation><contains-null>true</contains-null>
        </metadata-record>""")
    return "\n".join(out)
def ds_cols():
    return "\n".join(f"      <column caption='{CAP[n]}' datatype='{dt}' name='[{n}]' role='{role}' type='{typ}' />" for (n,dt,role,typ) in TIDY_COLS)

def datasource(ds_id, nc, csvname, csvdir):
    return f"""    <datasource caption='{csvname.replace('.csv','')}' inline='true' name='{ds_id}' version='18.1'>
      <connection class='federated'>
        <named-connections>
          <named-connection caption='{csvname.replace('.csv','')}' name='{nc}'>
            <connection class='textscan' directory='{csvdir}' filename='{csvname}' password='' server='' />
          </named-connection>
        </named-connections>
        <relation connection='{nc}' name='{csvname}' table='[{csvname.replace('.csv','')}#csv]' type='table'>
          <columns character-set='UTF-8' header='yes' locale='en_US_POSIX' separator=','>
{rel_cols()}
          </columns>
        </relation>
        <metadata-records>
{meta(csvname)}
        </metadata-records>
      </connection>
{ds_cols()}
    </datasource>"""

def worksheet(ds_id, name, mark, color):
    cols = f"([{ds_id}].[none:category:nk] / [{ds_id}].[none:series:nk])" if color else f"[{ds_id}].[none:category:nk]"
    rows = f"[{ds_id}].[sum:value:qk]"
    color_enc = f"            <color column='[{ds_id}].[series]' />\n" if color else ""
    deps = f"""          <datasource-dependencies datasource='{ds_id}'>
            <column caption='Panel' datatype='string' name='[panel]' role='dimension' type='nominal' />
            <column caption='Category' datatype='string' name='[category]' role='dimension' type='ordinal' />
            <column caption='Series' datatype='string' name='[series]' role='dimension' type='nominal' />
            <column caption='Value' datatype='real' name='[value]' role='measure' type='quantitative' />
            <column-instance column='[category]' derivation='None' name='[none:category:nk]' pivot='key' type='nominal' />
            <column-instance column='[series]' derivation='None' name='[none:series:nk]' pivot='key' type='nominal' />
            <column-instance column='[value]' derivation='Sum' name='[sum:value:qk]' pivot='key' type='quantitative' />
          </datasource-dependencies>"""
    return f"""    <worksheet name='{name}'>
      <table>
        <view>
          <datasources><datasource caption='data' name='{ds_id}' /></datasources>
{deps}
          <filter class='categorical' column='[{ds_id}].[panel]'>
            <groupfilter function='member' level='[panel]' member='&quot;{name}&quot;' />
          </filter>
          <slices><column>[{ds_id}].[panel]</column></slices>
          <aggregation value='true' />
        </view>
        <style /><panes>
          <pane selection-relaxation-option='selection-relaxation-allow'>
            <view><breakdown value='auto' /></view>
            <mark class='{mark}' /><encodings>
{color_enc}            </encodings>
          </pane>
        </panes>
        <rows>{rows}</rows><cols>{cols}</cols>
      </table>
    </worksheet>"""

def build_twb(ds_id, nc, csvname, csvdir, panels):
    ws="\n".join(worksheet(ds_id,name,mk,col) for name,(mk,col) in panels.items())
    wins="\n".join(f"    <window class='worksheet' name='{name}' />" for name in panels)
    wins+="\n    <window class='dashboard' name='Dashboard' />"
    dz=[]
    ph=int(90000/max(len(panels),1))
    y=8000
    for i,name in enumerate(panels):
        dz.append(f"          <zone h='{ph}' id='{5+i}' name='{name}' w='100000' x='0' y='{y}' />"); y+=ph
    dash=f"""    <dashboard name='Dashboard'>
      <style /><size maxheight='900' maxwidth='1100' minheight='900' minwidth='1100' />
      <zones><zone h='100000' id='3' type-v2='layout-flow' w='100000' x='0' y='0'>
          <zone h='8000' id='4' param='vert' type-v2='text' w='100000' x='0' y='0'>
            <formatted-text><run bold='true' fontsize='13'>{csvname.replace('_',' ').replace('.csv','')} — portfolio dashboard</run></formatted-text>
          </zone>
{chr(10).join(dz)}
      </zone></zones>
    </dashboard>"""
    return f"""<?xml version='1.0' encoding='utf-8' ?>
<workbook original-version='18.1' source-build='2023.1.0' source-platform='win' version='18.1' xmlns:user='http://www.tableausoftware.com/xml/user'>
  <preferences><preference name='ui.shelf.height' value='26' /></preferences>
  <datasources>
{datasource(ds_id,nc,csvname,csvdir)}
  </datasources>
  <worksheets>
{ws}
  </worksheets>
  <dashboards>
{dash}
  </dashboards>
  <windows source-height='30'>
{wins}
  </windows>
</workbook>
"""

def main():
    for slug,csvname,ds_id,label,rows,panels in DATASETS:
        write_csv(os.path.join(DATA,csvname),rows)
        nc="textscan."+ds_id.split(".")[1]
        csvdir=f"Data/{csvname.replace('.csv','')}"
        build=os.path.join(WB,"_b_"+slug)
        if os.path.exists(build): shutil.rmtree(build)
        os.makedirs(os.path.join(build,csvdir))
        twbname=slug.replace("-","_")+".twb"
        twbpath=os.path.join(build,twbname)
        open(twbpath,"w",encoding="utf-8").write(build_twb(ds_id,nc,csvname,csvdir,panels))
        minidom.parse(twbpath)
        shutil.copy(os.path.join(DATA,csvname),os.path.join(build,csvdir,csvname))
        out=os.path.join(WB,slug.replace("-","_")+".twbx")
        if os.path.exists(out): os.remove(out)
        with zipfile.ZipFile(out,"w",zipfile.ZIP_DEFLATED) as z:
            z.write(twbpath,twbname); z.write(os.path.join(build,csvdir,csvname),f"{csvdir}/{csvname}")
        shutil.rmtree(build)
        print("built",os.path.basename(out),"| rows:",len(rows))

if __name__=="__main__":
    main()
