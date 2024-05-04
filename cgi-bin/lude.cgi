#!/sdf/arpa/ns/s/synich/.shuw/bin/pb lua
-- USAGE: provide xx.lua, must has cgi method as entry
-- cgi will get 3 table, first `p: {do}` is router
-- when query /xx.cgi/sth?arg=1, sth will get 2 table
-- q: {arg=1}(exclude ?)
-- c: {a=1,b=2}(urlencoed)

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

local function errlog(msg)
  os.execute("echo "..'"`date` '..msg..'">>cgi-err.log')
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
cgi = function(p,q,c)
    local ptf = require(p[1])
    if ptf then
      isok, msg = pcall(ptf[p[2]], q, c)
      if not isok then errlog(p[1]..": "..msg) end
    else
      errlog("not found ["..p[1].."] request")
    end
end

local ok,msg = pcall(main) -- must be global function
if not ok then print(msg) end

