#!/usr/bin/env lua5.1
-- USAGE: provide xx.lua, must has cgi method as entry
-- cgi will get 3 table, first `p: {do}` is router
-- when query /xx.cgi/sth?arg=1, sth will get 2 table
-- q: {arg=1}(exclude ?)
-- c: {a=1,b=2}(urlencoed)


-------------------------------
-- handy function for write cgi
-------------------------------
-- format/template string
local function format(body, hole, ...)
  local lst = {...}
  if hole == "$" then hole = "%$" end
  for i=1,#lst do
    body = body:gsub(hole, lst[i], 1)
  end
  return body
end

-- easy wrap for io.popen
local function popen(cmd)
  cmd = cmd:gsub("`", "\\`") -- avoid ` work in shell
  local fd = io.popen(cmd)
  local txt = fd:read("*a")
  fd:close()
  return txt:sub(1, -2)  -- last is \n, drop it
end

local function str_split(s, delim)
  local t = {}
  local p_start, p_next = 1, 1
  local s_sec, p_eq = "", 1
  repeat
    p_next = s:find(delim, p_start, true)
    if p_next then
      s_sec = s:sub(p_start, p_next-1)
      p_start = p_next + 1
    else
      s_sec = s:sub(p_start)
    end
    table.insert(t, s_sec)
  until not p_next
  return t
end

local function sql_exec(db, sql_stmt)
  -- make write SQL literal, ugly but only this way
  sql_stmt = sql_stmt:gsub("%%", "%%%%")
  local cmd = format([[sqlite3 $.db "$"]], "$", db, sql_stmt)
  return popen(cmd)
end

local function errlog(msg)
  os.execute("echo "..'"`date` '..msg..'">>cgi-err.log')
end

-- character table string
local b='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'

-- encoding
local function b64enc(data)
    return ((data:gsub('.', function(x) 
        local r,b='',x:byte()
        for i=8,1,-1 do r=r..(b%2^i-b%2^(i-1)>0 and '1' or '0') end
        return r;
    end)..'0000'):gsub('%d%d%d?%d?%d?%d?', function(x)
        if (#x < 6) then return '' end
        local c=0
        for i=1,6 do c=c+(x:sub(i,i)=='1' and 2^(6-i) or 0) end
        return b:sub(c+1,c+1)
    end)..({ '', '==', '=' })[#data%3+1])
end

-- decoding
local function b64dec(data)
    data = string.gsub(data, '[^'..b..'=]', '')
    return (data:gsub('.', function(x)
        if (x == '=') then return '' end
        local r,f='',(b:find(x)-1)
        for i=6,1,-1 do r=r..(f%2^i-f%2^(i-1)>0 and '1' or '0') end
        return r;
    end):gsub('%d%d%d?%d?%d?%d?%d?%d?', function(x)
        if (#x ~= 8) then return '' end
        local c=0
        for i=1,8 do c=c+(x:sub(i,i)=='1' and 2^(8-i) or 0) end
        return string.char(c)
    end))
end


---------------------------
-- construct for http parse
---------------------------
local function _url_str_tbl(s)
  -- split urlencoed into table
  local t = {}
  local p_start, p_next = 1, 1
  local s_sec, p_eq = "", 1
  repeat
    p_next = s:find("&", p_start, true)
    if p_next then
      s_sec = s:sub(p_start, p_next-1)
      p_start = p_next + 1
    else
      s_sec = s:sub(p_start)
    end
    p_eq = s_sec:find("=", 1, true)
    if p_eq then
      t[s_sec:sub(1, p_eq-1)] = s_sec:sub(p_eq+1)
    end
  until not p_next
  return t
end

local function _path_tbl(s)
  local t = {}
  local p_start, p_next = 2, 1
  repeat
    p_next = s:find("/", p_start, true)
    if p_next then
      table.insert(t, s:sub(p_start, p_next-1))
      p_start = p_next + 1
    else
      table.insert(t, s:sub(p_start))
    end
  until not p_next
  return t
end

-- base64 in body will change by urlencoded, restore it
local function _res_urlenc(str)
  str = str:gsub("%%2B", "+")
  str = str:gsub("%%2F", "/")
  return str
end

local function cgi_entry()
  local method = os.getenv("REQUEST_METHOD")
  -- part after r.cgi, e.g r.cgi/foo/bar, path_info is /foo/bar
  local path_info = os.getenv("PATH_INFO")
  -- part after ?(exclude ?), e.g r.cgi/foo?arg=3, query is arg=3
  local query_str = os.getenv("QUERY_STRING")
  local urlencoded_content = io.read("*a")
  -- cal module's cgi function, urlencoded will make +/ to %2B%2F, restore them
  if nil then errlog(method.." pi:"..path_info.." qs:"..query_str.." ctx:"..urlencoded_content) end
  cgi(_path_tbl(path_info),
      _url_str_tbl( _res_urlenc(query_str) ),
      _url_str_tbl( _res_urlenc(urlencoded_content) ))
end

function main()
  if os.getenv("REQUEST_METHOD") then
    -- ensure html render
    print("Content-Type: text/html; charset=UTF-8\n")
    cgi_entry()
  else
    unittest()
  end
end

---------------------------------------
-- cgi entry, register bussness into fn
-- fn has 2 args: qs & ctx
---------------------------------------
local fn = {}
cgi = function(p,q,c)
    local ptf = fn[p[1]]
    if ptf then
      isok, msg = pcall(ptf, q, c)
      if not isok then errlog(p[1]..": "..msg) end
    else
      errlog("not found ["..p[1].."] request")
    end
end


-- blog.cgi/read?dt=220204
local function blread(dummy, q)
  local dt = q["dt"]
  local fname = popen(format("find ../pub/ -name $*.md", "$", dt))
  local attr = fname:match("_(.-)%.") or "" -- 220204_lang.md, lang is attr
  local fd = io.open(fname, "r")
  if fd then
    local txt = fd:read("*a")
    io.write(attr.."|"..txt)
  else
    io.write(fname)
  end
end

-- blog edit
local function bledit(q, c)
  local dt = q["dt"]
  local belong = dt:sub(1,1)
  local ctx = b64dec(c["ctx"])
  local tag = c["tag"] or ""
  local fd = io.open("../pub/b"..belong.."/"..dt.."_"..tag..".md", "w")
  fd:write(ctx)
  fd:close()
  os.execute(format("echo $ >>../pub/blog_up", "$", dt))
  print("len:"..#ctx)
end

-- registry func entry
fn["blread"]=blread
fn["bledit"]=bledit

function unittest()
  blread({},{dt="230112"})
end


local ok,msg = pcall(main) -- must be global function
if not ok then print(msg) end

