--define global
local db_name = "./shuw.db"
local hint_name = "flk_hint.txt"
local full_name = "flk_full.md"

setmetatable(_G,{__newindex=function(_, k, v)local b=k:find('g_')if b~=1 then error('Error: global ['..k..'], only prefix [g_] allow')else rawset(_G,k,v)end end})

--helper tool
-- add space between hanzi and [english or digit]
local function hanzi_sep(s)
  s = s:gsub("，", ",")
  s = s:gsub("。", ".")
  s = s:gsub("？", "?")
  s = s:gsub("！", "!")
  s = s:gsub("：", ":")
  s = s:gsub("；", ";")
  s = s:gsub("、", ",")
  s = s:gsub("（", "(")
  s = s:gsub("）", ")")
  s = s:gsub("【", "[")
  s = s:gsub("】", "]")
  s = s:gsub("《", "<")
  s = s:gsub("》", ">")
  s = s:gsub("“", '"')
  s = s:gsub("”", '"')

  local function _isw(c)
    if (48<=c and c<=57) or (65<=c and c<=90) or (97<=c and c<=122) then
      return true
    else
      return false
    end
  end
  local ch_seq, str_seq, pre_ch_bel = {}, {}, 0 -- 0:other 1:ascii 2:hanzi
  for pos, c in utf8.codes(s) do
    if (pre_ch_bel==1 and c>=128) or (pre_ch_bel==2 and _isw(c)) then
      table.insert(str_seq, utf8.char(unpack(ch_seq)).." ")
      ch_seq = {}
    end
    table.insert(ch_seq, c)
    if _isw(c) then
      pre_ch_bel=1
    elseif c>=128 then
      pre_ch_bel=2
    else
      pre_ch_bel=0
    end
  end
  return table.concat(str_seq)..utf8.char(unpack(ch_seq))
end

local function curday() -- 6 digit date
  local date = os.date("*t") -- Get the current date and time as a table
  local year = tostring(date.year) -- Convert the year to a string
  local month = tostring(date.month) -- Convert the month to a string
  local day = tostring(date.day) -- Convert the day to a string

  -- Pad the month and day strings with a leading zero if they are only one digit
  if #month == 1 then month = "0" .. month end
  if #day == 1 then day = "0" .. day  end
  return year:sub(3,4) .. month .. day
end

local function fetchone(db, sql) -- always return table and use [1],[2] get col
  for a in db:rows(sql) do return a end
  return {}
end

local function fetchall(db, sql) -- always return table and use [1],[2] get col
  local lst = {}
  for a in db:rows(sql) do table.insert(lst, a) end
  return lst
end

local function tag2json(str)
  local matches = {}
  for mat in string.gmatch(str, "#[^ \n#'\"/?!;&@]+") do
    table.insert(matches, fmt('"{}"', mat:sub(2)))
  end
  return fmt("[{}]", table.concat(matches, ", "))
end

--universal fts
local function fts_match(db, txt, limit)
  -- txt and return is utf-8
  local function _cv_kwd2fts_syn(txt)
    -- convert search keyword to fts syntax
    txt = txt:gsub("^ +", "")
    txt = txt:gsub(" +$", "")
    local s = ""
    for i in txt:gmatch("([^%s]+)%s*") do
      if "-" == i:sub(1,1) then
        s = s.." NOT "..i:sub(2).."*"
      else
        s = s.." AND "..i.."*"
      end
    end
    return s:sub(6)
  end

  local lst = {}
  local i = 0
  if not limit then limit = 20 end
  txt = _cv_kwd2fts_syn(txt)
  return fetchall(db, [[select rowid, snippet(memo,0,'','','@',10), content
      from memo where memo match ']]..txt.."' order by rank limit "..limit)
end

local function fts_like(db, txt, limit)
  local function _cv_kwd2like(txt)
    txt = txt:gsub("^ +", "")
    txt = txt:gsub(" +$", "")
    local s = ""
    for i in txt:gmatch("([^%s]+)%s*") do
      if "-" == i:sub(1,1) then
        s = s.." and content not like '%"..i.."%'"
      else
        s = s.." and content like '%"..i.."%'"
      end
    end
    return s
  end
  if not limit then limit = 30 end
  txt = _cv_kwd2like(txt)
  local a = fetchall(db, "select date||'blog', substr(content,1,45) from blog where 1=1"..txt.." limit "..limit)
  local b = fetchall(db, "select date||'tmrec', substr(content,1,45) from tmrec where 1=1"..txt.." limit "..limit)
  local c = fetchall(db, "select rowid||'memo', substr(content,1,45) from memo where 1=1"..txt.." limit "..limit)
  for i,v in ipairs(b) do table.insert(a, v) end
  for i,v in ipairs(c) do table.insert(a, v) end
  return a
end

local function fts_ramble(db)
  local cnt = fetchone(db, "select count(1) from memo")[1]
  local lst, has_roll, r = {}, ""
  for i=1,10 do
    r = math.random(1, cnt)
    if not has_roll:find(r..",") then
      local a = fetchone( db, "select rowid, substr(content,1,50) from memo order by date limit 1 offset "..r )
      table.insert(lst, a)
      has_roll=has_roll..r..","
    end
    --print(has_roll)
    if #has_roll >20 then break end
  end
  return lst
end

local function fts_rowid(db, rowid) -- -> table
  -- {id, abstract, content(maybe has tag)}
  local id, tbl = rowid:match("(%d+)%s*(%a*)")
  if tbl:sub(1,1)=="b" then
    return fetchone(db, "select date, substr(content, 1, 40), content||' #'||attr from blog where date="..id)
  elseif tbl:sub(1,1)=="t" then
    return fetchone(db, "select date, content, content from tmrec where date="..id)
  else
    return fetchone(db, "select rowid, substr(content, 1, 40), content from memo where rowid="..id)
  end
end

local function fts_modify(db, tbl, dml, rowid, txt, attr)
  -- txt must be utf-8
  if not rowid then rowid = "" end
  if not attr then attr = "" end
  local act, ret
  if "m"==tbl:sub(1,1) then
    local sql = [[update memo set content=']]..txt.."',date="..curday().." where rowid="..rowid
    act = "update "..tbl..rowid
    if "i"==dml then
      sql = [[insert into memo values( ']]..txt.."',"..curday()..")"
      act = "insert "..tbl.." len(bytes): "..#txt
    elseif "d"==dml then
      sql = [[delete from memo where rowid=]]..rowid
      act = "delete "..tbl..rowid
    end
    ret = db:exec(sql)
    if "i"==dml then act=act.." rowid="..db:last_insert_rowid() end
  else -- blog or tmrec
    local sql = "update "..tbl.." set content='"..txt.."' where date="..rowid
    act = "update "..tbl..rowid
    if "i"==dml then
      sql = "insert into "..tbl.." values("..rowid..", '"..txt.."','"..attr.."')"
      act = "insert "..tbl..rowid..", len(bytes): "..#txt
    elseif "d"==dml then
      sql = "delete from "..tbl.." where date="..rowid
      act = "delete "..tbl..rowid
    end
    ret = db:exec(sql)
  end
  return ret==0 and "OK "..act or "Fail"..act
end


-- command line tool
local function _wc(fname, txt) -- write text to file
  local fout = io.open(fname, "w"); fout:write(txt); fout:close()
end
local function _rc(fname)
  local fout = io.open(fname, "r");local txt=fout:read("*a"); fout:close(); return txt:gsub("'", "''")
end

local function init(db)
  db:exec[[CREATE VIRTUAL TABLE memo USING fts5(content, date UNINDEXED, tokenize = 'porter ascii');]]
end

local function _ins(db, t, up)
  t = hanzi_sep(t)
  t = t:gsub("'", "''") -- escape ' to ''
  db:exec("insert into memo values('"..t.."',"..up..")")
end

local function addmd(db)
  for i,v in ipairs(dt.lsfile("./tid")) do
    if v:find("20") then
    local fd = io.open("./tid/"..v, "r")
    local txt = fd:read("*a"); fd:close()
    local up = v:sub(3,8)
    --print(up)
    _ins(db, txt, up)
    end
  end
end

local function tfe()
  local db=sqlite3.open("shuw.db")
  init(db)
  addmd(db)
  db:close()
end

local function clientry(arg)
  local db, rc = sqlite3.open(db_name), 0
  local lst, short = nil, ""
  if "rowid"==arg[1] then  -- rowid
    lst = fts_rowid(db, arg[2])
    if #lst >0 then
      _wc(hint_name, lst[1]..": "..(lst[2]:gsub("\n+"," ")) ) -- TODO
      _wc(full_name, lst[3])
    else rc = 1
    end
  elseif "like"==arg[1] then  -- like
    lst = fts_like(db, arg[2])
    for i,v in ipairs(lst) do
      short = short..v[1]..": "..v[2]:gsub("\n+"," ").."\n"
    end
    _wc(hint_name, short:sub(1,-2))
  elseif "ramble"==arg[1] then  -- ramble
    math.randomseed(os.time())
    lst = fts_ramble(db)
    for i,v in ipairs(lst) do
      short = short..v[1]..": "..(v[2]:gsub("\n+","")).."\n"
    end
    _wc(hint_name, short:sub(1,-2))
  elseif "match"==arg[1] then -- match
    lst = fts_match(db, arg[2])
    for i,v in ipairs(lst) do
      short = short..v[1]..": "..v[2]:gsub("\n+"," ").."\n"
    end
    _wc(hint_name, short:sub(1,-2))
  elseif "mod_m"==arg[1] then -- modify memo
    local can_hanzi = ""
    local dml = arg[2]:sub(1,1)
    if "d"~=dml then
      can_hanzi = hanzi_sep(_rc(full_name))
    end
    _wc(hint_name, fts_modify(db, "memo", dml, arg[3], can_hanzi) )
  elseif "mod_bt"==arg[1] then -- modify blog/tmrec
    local ctx, attr, tbl = "", "", ""
    if "b"==arg[2]:sub(1,1) then tbl = "blog"
    elseif "t"==arg[2]:sub(1,1) then tbl = "tmrec" end
    local ctx, attr = "", ""
    local dml = arg[3]:sub(1,1)
    ctx = _rc(full_name)
    attr = ctx:match(" #(%a*)$") --after " #" is tag
    if attr then ctx = ctx:sub(1, -3-#attr) end
    _wc(hint_name, fts_modify(db, tbl, dml, arg[4], ctx, attr) )
  else
    print([[rowid 12[b/t]
like "a b -c"
ramble
mod_m ins/up/del [rowid]
mod_bt blog/tmrec ins/up/del rowid]])
    rc = 1
  end
  os.exit(rc)
end

-- mimic python __main__
if "dbop.lua"==arg[0] then
  clientry(arg)
else
  return {fts_match=fts_match, fts_rowid=fts_rowid, fts_like=fts_like, fts_modify=fts_modify, fts_ramble=fts_ramble, hanzi_sep=hanzi_sep}
end
