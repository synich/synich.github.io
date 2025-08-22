local mod = {}
local db = sqlite3.open("m.db")

local function fetchone(db, sql) -- always return table and use [1],[2] get col
  for a in db:rows(sql) do return a end
  return {}
end

local function fetchall(db, sql) -- always return table and use [1],[2] get col
  local lst = {}
  for a in db:rows(sql) do table.insert(lst, a) end
  return lst
end

mod.pull = function (q, c)
  local r = fetchall(db, "select rowid, content from memo")
  local out = 'memo<br>'
  for i, v in ipairs(r) do
    out = out..fmt("<p>{}. {}</p>", v[1], v[2])
  end
  print(out)
end

mod.push = function (q, c)
  local ctx, r = q["t"]
  local num = ctx:match("clear(%d+)")
  if num then
    r = db:exec(fmt("delete from memo where rowid={}", num))
  else
    r = db:exec(fmt("insert into memo values('{}')", ctx))
  end
  print("receive "..utf8.len(ctx), r)
end

mod.stock = function()
  print(os.date("%Y-%m-%d %H:%M:%S", os.time()+8*3600).."<br>")
  local lst = {sz002236='大华', sz159919='300ETF:3.11-5.74', sz159922='500ETF:1.73-3.03', sz159915='创业ETF:1.44-3.46', sh512880='证券ETF:0.74-1.40'}
  for k, v in pairs(lst) do
    local cmd = fmt("curl http://qt.gtimg.cn/q=s_{} 2>/dev/null", k)
    local r = os.popen(cmd)
    local a = r:split("~")
    local co = '<p style="color:red;">'
    if tonumber(a[5]) <0 then
      co = '<p style="color:green;">'
    end
    print(co, v, '||', a[4], a[5], a[6], '</p>')
  end
end

mod.close = function ()
  db:close()
end

return mod

--[[ INIT
local function init(dname)
  local db = sqlite3.open(dname)
  db:exec("create virtual table memo using fts5(content, tokenize='porter ascii')")
  db:close()
end

init("m.db")
]]
