#!/root/.shuw/bin/pb lua
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
  s = s and s or "/"
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

-- js send with encodeURI, restore it
local function decodeURI(s)
  return s:gsub('%%(%x%x)', function(hex)
    return string.char(tonumber(hex, 16))
  end)
end

local function errlog(msg)
  os.execute("echo "..'"`date` '..msg..'">>cgi-err.log')
end

local function cgi_entry(method)
  -- part after r.cgi, e.g r.cgi/foo/bar, path_info is /foo/bar
  local path_info = os.getenv("PATH_INFO")
  -- part after ?(exclude ?), e.g r.cgi/foo?arg=3, query is arg=3
  local query_str = os.getenv("QUERY_STRING")
  local urlencoded_content = io.read("*a")
  -- cal module's cgi function, urlencoded will make +/ to %2B%2F, restore them
  if nil then errlog(method.." pi:"..path_info.." qs:"..query_str.." ctx:"..urlencoded_content) end
  cgi(_path_tbl(path_info),
      _url_str_tbl( decodeURI(query_str) ),
      _url_str_tbl( decodeURI(urlencoded_content) ),
      method)
end

function main()
  local method = os.getenv("REQUEST_METHOD")
  if method then
    -- ensure html render
    print("Content-Type: text/html; charset=UTF-8\n")
    cgi_entry(method)
  else
    unittest()
  end
end

---------------------------------------
-- cgi entry, register bussness into fn
-- fn has 3 args: qs & ctx(both table), method(GET/POST)
---------------------------------------
cgi = function(p,q,c,m)
  local mod = p[1]
  local ent = p[2] and p[2] or 'main'
  local ptf = require(mod)
  local isok, msg = pcall(ptf[ent], q, c, m:upper())
  if not isok then
    local em = msg..", by "..mod.."/"..ent
    errlog(em);print(em)
  end
  if mod.close then mod.close() end
end

local ok,msg = pcall(main) -- must be global function
if not ok then print(msg) end

