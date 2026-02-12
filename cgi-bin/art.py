TOKEN = "shuw"
TMMARK = "##c"
pb_cmd = "./pb lua dbop.lua "
pb_hint = "cat flk_hint.txt"
pb_full = "flk_full.md"


from typing import Union
def _fname_bydt(ddir, dt)->str:
    import os
    cmd = f"find ../{ddir}/ -name {dt}*.md"
    fname = ""
    with os.popen(cmd) as fd:
        fname = fd.read().strip()
    return fname

def _db_cur(dname: str)->tuple:
    import sqlite3
    db = sqlite3.connect(f"./{dname}.db", isolation_level=None)
    return (db.cursor(), db)

def _b64dec(inp, des="str")->Union[str, bytes]:
    """wrap base64 decode and patch for droidscript"""
    import base64
    comp_inp = inp
    if (lostpad := len(inp)%4) != 0:  # droidscript POST will drop base64 last =, complement it
        comp_inp = inp + "="*(4-lostpad)
    if des == "bin":
        return base64.b64decode(comp_inp)
    else:
        return base64.b64decode(comp_inp).decode('utf-8')

################# blog ####################
def blread(prm):
    db = prm["db"]
    dt = prm["dt"]
    cur, sqldb = _db_cur(db)
    cur.execute(f"select content, attr from blog where date={dt}")
    lst = cur.fetchone()
    if lst is None:
        print("unknown|")
    else:
        print(f"{lst[1]}|{lst[0]}")

def bledit(prm):
    """receive push edited blog and save as markdown"""
    if prm["token"] != TOKEN:
        print("not allowed")
        return
    db = prm["db"]
    dt = prm["dt"]
    txt = _b64dec(prm["txt"])
    tag = prm["tag"]
    cur, sqldb = _db_cur(db)
    cur.execute(f"insert or replace into blog(date,content,attr) values(?,?,?)", (dt, txt, tag))
    sqldb.close()
    print(f"upsert {dt} len:{len(txt)}")

def blappd(prm):
    txt = _b64dec(prm["txt"])
    fname = "../pub/b2/230430_think.md" # TODO
    if len(txt) >= 4:
        with open(fname, "a") as f:
            f.write("\n"+txt.strip())
        import os
        st = os.stat(fname)
        print(fname[10:], st.st_size)
    else:
        with open(fname, "r") as f:
            print(f.read())

def randBlog(prm):
    db = prm["db"]
    tag = prm["tag"]
    if tag == "unknown":
        filtag = "1=1"
    else:
        filtag = f"attr='{tag}'"
    cur, sqldb = _db_cur(db)
    cur.execute(f"select count(1) from blog where {filtag}")
    lst = cur.fetchone()
    import random
    off = random.randint(0, lst[0]-1)
    cur.execute(f"select date, content from blog where {filtag} order by date limit 1 offset {off}")
    lst = cur.fetchone()
    print(lst[0], lst[1])


################# search ####################
def _btitle(ctx):
    """retrieve title from blog"""
    if ctx[0] == "#":   # first line but drop leading #
        ln = ctx.find("\n")
        return ctx[2:ln]
    else:  # all first line when second line is ==
        ln = ctx.find("==")
        return ctx[:ln-1]

def pub_blog_kwd(prm):
    """ search only public blog
    k: keyword. special usage: > or < choose date; - exclusive content; all other is and"""
    def _find_ctx_dt(cur, k):
        arrk = k.split(" ")
        where_clause = "where 1=1"
        for i in arrk:
            if i=="" or i.find(";")>=0 or i.find("--")>=0:
                continue  # drop evel token
            elif (i[0] == ">" or i[0] == "<") and len(i)==7:
                where_clause += f" and date {i}"
            elif i[0] == "-":
                where_clause += f" and content not like '%{i[1:]}%'"
            else:
                where_clause += f" and content like '%{i}%'"
        if where_clause == "where 1=1":
            return []
        cur.execute(f"""select date, substr(content, 1, 30) from blog {where_clause}""")
        return cur.fetchall()
    k = prm["k"]
    import json
    cur, _ = _db_cur("shuw") # only for public blog
    lst = _find_ctx_dt(cur, k)
    ret = [(str(dt),_btitle(ctx)) for dt,ctx in lst]
    print(json.dumps(ret))

def any_kwd(prm):
    """search any db"""
    def _find_db_print(dname, arr):
        cur, _ = _db_cur(dname)
        where_clause = "where 1=1"
        for i in arr:
            if i[0] == '#':
                where_clause += f" and attr like '%{i[1:]}%'"
            else:
                where_clause += f" and content like '%{i}%'"
        cur.execute(f"select date, substr(content, 1, 25), attr from blog {where_clause} limit 20")
        lst = cur.fetchall()
        print(f'<span style="color: #00F;">{dname} blog</span>')
        for i in lst:
            print(f"{i[0]}|{_btitle(i[1])}|{i[2]}")
        cur.execute(f"select date, content, attr from tmrec {where_clause} limit 20")
        lst = cur.fetchall()
        print(f'<span style="color: #390;">{dname} tmrec</span>')
        for i in lst:
            print(f"{i[0]}|{i[1]}|{i[2]}")
        print(f'<span style="color: #FC3;">{dname} memo</span>')
        cur.execute(f"select date, content from memo where memo match '{arr[0]}*' limit 20") # TODO
        lst = cur.fetchall()
        for i in lst:
            print(f"{i[0]}|{i[1]}")
    k = _b64dec(prm["kwd"])
    arr = k.split(" ")
    _find_db_print("shuw", arr)


################# tmrec ####################
# tmread?db=shuw&dt=2208
def tmread(prm):
    db = prm["db"]
    dt = prm["dt"][:6]
    cur, sqldb = _db_cur(db)
    stmt = f"select date,content,attr from tmrec where date like '{dt}%';"
    if len(dt) == 6:
      stmt = f"select date,content,attr from tmrec where date={dt};"
    cur.execute(stmt)
    lst = cur.fetchall()
    for i in lst:
        print(f"{i[0]}|{i[1]}|{i[2]}<br>")

def tmupload(prm):
    db = prm["db"]
    dt = prm["dt"]
    txt = _b64dec(prm["txt"])
    attr = ''
    ctx = txt
    if (pos:=txt.find(TMMARK)) >= 0:
        ctx = txt[:pos]
        attr = txt[pos+len(TMMARK)-1:] # last reserve TMMARK
    cur, sqldb = _db_cur(db)
    stmt = f"INSERT OR REPLACE INTO tmrec VALUES({dt}, '{ctx}', '{attr}')"
    cur.execute(stmt)
    sqldb.commit()
    print(f"UPSERT {dt}, tag:{attr}.")
    cur.execute("SELECT date FROM tmrec order by date desc limit 5")
    print(f"Recent {[i[0] for i in cur.fetchall()]}")


def _pdo(cmd):
    import os
    ret = os.system(cmd)
    #with os.popen(cmd) as fd:
    #    ret = fd.read().strip()
    return ret
def _rtxt(t):
    with open(t, "r") as f:
        return f.read()
def _wtxt(t):
    with open(pb_full, "w") as f:
        f.write(t)
def _matchdb(kwd):
    import sqlite3
    db = sqlite3.connect(f"./shuw.db", isolation_level=None)
    cur = db.cursor()
    cur.execute(f"""select rowid, snippet(memo,0,'','','@',10), content
      from memo where memo match '{kwd}*' order by rank limit 20""")
    return cur.fetchall()

def pbdbkwd(prm):
    import os
    cmd = _b64dec(prm["cmd"])
    hd = cmd[0]
    if "!" == hd:
        _pdo(f"{pb_cmd} ramble")
        print(_rtxt("flk_hint.txt"))
    elif "#" == hd:
        _pdo(f"{pb_cmd} rowid {cmd[1:]}")
        print(_rtxt(pb_full))
    elif "*" == hd:
        ret = _pdo(f"{pb_cmd} like '{cmd[1:]}'")
        print(_rtxt("flk_hint.txt"))
    else:
        ret = _pdo(f"{pb_cmd} match '{cmd}'")
        print(_rtxt("flk_hint.txt"))

def pbdbop(prm):
    import re
    op = _b64dec(prm["op"])
    pos = op.find(",")
    cmd = op[:pos]
    txt = op[pos+1:]
    p = re.match("([a-z]+)\s*(\d*)\s*([a-z]*)", cmd)
    _wtxt(txt)
    act, rowid, tbl = p.group(1),p.group(2),p.group(3)
    if tbl == "" or tbl[0] == "m":
        _pdo(f"{pb_cmd} mod_m {act[0]} {rowid}")
    else:
        _pdo(f"{pb_cmd} mod_bt {tbl} {act[0]} {rowid}")
    print(_rtxt("flk_hint.txt"))


################# anki ####################
def ankiReview(prm):
    """ anki remember """
    import datetime
    db = prm["db"]
    tbl = prm["tbl"]
    cur, sqldb = _db_cur(db)
    t = datetime.datetime.now()
    cur.execute(f"select date,lastday from anki where cata='{tbl}' and lastday <> {t.strftime('%Y%m%d')[2:]} order by recall asc limit 1")
    lst = cur.fetchone()
    last_day = lst[1]
    cur.execute(f"select date, content, attr from {tbl} where date={lst[0]}")
    lst = cur.fetchone()
    if len(lst) > 0:
        print(lst[0], lst[1], lst[2], last_day)
    else:
        print("today no anki")


def ankiMark(prm):
    def _up_recall(D, S, R, dT, dificulty)->tuple:
        REMEM_A = 1.5 # S remem
        FORGET_DECAY = 0.5  # S forget
        import math
        d = D - (dificulty-1) # - (1-R)
        d = max(d, 1)
        d = min(d, 5)
        if dificulty >= 1:
            s = int(S + d * dificulty * REMEM_A)
        else:
            s = int(S - d * FORGET_DECAY)
        s = max(s, 1)
        s = min(s, 180)
        r = "%.3f"%(1 / ((1+dT/s) * d))
        print(f"D:{D}, S:{S}, R:{R}, d:{d}, s:{s}, r:{r}")
        return r, f"{d}_{s}"
    import datetime
    db = prm["db"]
    tbl = prm["tbl"]
    dt = prm["dt"]
    dificulty = int(prm["d"])
    cur, sqldb = _db_cur(db)
    cur.execute(f"select d_s, recall, lastday from anki where date={dt}")
    lst = cur.fetchone()
    ds = lst[0].split('_')
    lastday = datetime.datetime.strptime(f'20{lst[2]}','%Y%m%d')
    t = datetime.datetime.now()
    ret = _up_recall(int(ds[0]), int(ds[1]), float(lst[1]), (t-lastday).days, dificulty)
    cur.execute(f"update anki set d_s='{ret[1]}', recall={ret[0]}, lastday={t.strftime('%Y%m%d')[2:]} where cata='{tbl}' and date={dt}")
    sqldb.commit()
    print(dt,"anki up")


################# boot & file ####################
def startup(prm):
    import os
    r = os.popen("curl http://qt.gtimg.cn/q=s_sz002236 2>/dev/null|awk -F~ '{print $4, $5, $6, $10}'")
    print(r.read())

def pic(prm):
    idx = prm["i"]
    print(f"""<html><head>
<meta http-equiv="content-type" content="text/html; charset=utf-8"></meta></head>
<body> <img src="/ar/bt/{idx}.j" alt="" />
</body></html>""")

def vd(prm):
    idx = prm["i"]
    print(f"""<html><head>
<meta http-equiv="content-type" content="text/html; charset=utf-8"></meta></head>
<body> <video src="/ar/bt/{idx}.mp4" />
</body></html>""")

def upfile(prm):
    fname = prm["fn"]
    ext = prm["ext"]
    picb64 = prm["pic"]
    idx = picb64.find(";base64,")
    if idx == -1:
        print(f"illega {picb64}")
    else:
        picd = _b64dec(picb64[idx+8:], des="bin")
        upfn = f"{fname}.{ext}"
        with open(upfn, "wb") as f:
            f.write(picd)
        import os
        st = os.stat(upfn)
        print(f"{upfn} {st.st_size}")

################# llm gemini ####################
def query_gemini(prompt):
    import json
    from urllib.request import Request, urlopen
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"thinkingConfig": {"thinkingBudget": 0}}
    }
    data = json.dumps(payload).encode('utf-8')
    req = Request( url=url, data=data,
        headers={ 'Content-Type': 'application/json',
            'X-goog-api-key': 'AIzaSyChvjyiU1TBzgyKqCY1lEe6ZSHAYxJggFo'
        }
    )
    with urlopen(req) as response:
        result = json.loads(response.read())
        return result['candidates'][0]['content']['parts'][0]['text']

def ask_llm(prm):
    txt = prm["txt"]
    res = query_gemini(txt)
    print(res)

################# test ####################
if __name__ == "__main__":
    prm = {"i":"8"}
    pic(prm)

