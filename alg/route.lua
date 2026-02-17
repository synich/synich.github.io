----------------- tool ----------------
require 'pb'
-- fix in algernon which pb is not enough
local function _wc(fname, txt)
  os.execute("echo >"..fname) -- open with w sometimes not work, so use echo force purge
  local fout = io.open(fname, "w"); fout:write(txt); fout:close() --txt=txt:gsub("[\n%s]*$","");
end

----------------- user ----------------
USER = "shuw"

local function init_user()
  AddUser(USER, "swan@163", "shu_wang@163.com")
end

local function cgi_user()
  if "GET"==method() then
    local d=formdata()
    if d["init"] then
      init_user()
    end
    pprint("all users", AllUsernames())
    --print(UsernameCookie(), Username(), CookieTimeout("shuw"), CookieSecret(), PasswordAlgo())
    --print("user", UserRights(), "admin", AdminRights(), "login", IsLoggedIn("shuw"))
  else
    local t = formdata()
    if t["token"] == USER then
      Login(USER)
      SetCookieTimeout(86400*7)
      --SetAdminStatus(USER)
      print("login")
    else
      print("fail")
    end
  end
end

local function check_user()
  if UsernameCookie() == USER then return true
  else print("not allow") return false end
end
----------------- memo ------------------
local function KV(name)
  local t = {}
  t.s = Set(name.."_s")
  t.k = KeyValue(name.."_k")
  t.getall = function(self) return self.s:getall() end
  t.get = function(self, k) return self.k:get(k) end
  t.set = function(self, k, v) self.s:add(k);return self.k:set(k,v) end
  t.inc = function(self, k) return self.k:inc(k) end
  t.del = function(self, k) self.s:del(k);return self.k:del(k) end
  t.clear = function(self) self.s:clear(); self.k:clear() end
  t.remove = function(self) self.s:remove(); self.k:remove() end
  t.json = function(self) local j = {};
    for _,v in ipairs(self.s:getall()) do j[v]=self.k:get(v) end
    return JSON(j)
  end
  t.compact = function(self) local j = "";
    for _,v in ipairs(self:getall()) do j=j..self.k:get(v).."\n" end
    self:clear(); self:set(self:inc("primary_id"), j)
  end
  t.find = function(self, word) local ans = ""
    for _,v in ipairs(self:getall()) do
      if self.k:get(v):find(word) then ans = ans..v..". "..self.k:get(v).."\n" end
    end
    return #ans==0 and "not found "..word or ans
  end
  return t
end

local function sub_utf8(u_str, need_n)
  local epos = 1
  for i = 1, need_n do
    if epos > #u_str then break end
    if u_str:byte(epos) < 128 then
      epos = epos + 1
    else
      epos = epos + 3
    end
  end
  return epos
end

local function cgi_memo()
  local d = formdata()
  local i = tonumber(d["i"])
  if i then
    local l = KV("memo"..d["i"])
    if "POST"==method() then
      if d["k"]:sub(1,5)=="clear" then
        local nk = d["k"]:match("clear%s*(%d*)")
        if ""==nk then l:clear()
        else l:del(nk) end
      elseif d["k"]=="compact" then
        l:compact(); print("compact")
      elseif d["k"]:sub(1,1)=="*" then
        print(l:find(d["k"]:sub(2)))
      else
        local nk = l:inc("primary_id")
        l:set(nk, d["k"])
      end
      pprint(string.sub(d["k"], 1, sub_utf8(d["k"], 8)-1), #d["k"], "bytes OK")
    else -- GET
      for i,v in ipairs(l:getall()) do
        local c = l:get(v):gsub("<", "&lt;"):gsub(">", "&gt;")
        print(v..". "..c.."<br>")
      end
    end
  end
end

----------------- fts ------------------
--- match/rowid/ins/up kw=12&txt=...
local hint_name = "flk_hint.txt"
local full_name = "flk_full.md"
local dbop_cmd = "~/.shuw/bin/pb lu dbop.lua "
local function cgi_fts()
  local d = formdata()
  local cmd, txt
  if "POST"==method() then -- ins or up
    _wc(full_name, d["txt"])
    if d["kw"]=="" then
      cmd = fmt("{} mod_m ins", dbop_cmd)
    else
      cmd = fmt("{} mod_m up {}", dbop_cmd, d["kw"])
    end
    os.execute(cmd)
    txt = _rc(hint_name)
    print(cmd, txt)
  else -- match/like or rowid or ramble
    if d["kw"]:sub(1,1) == "#" then
      cmd = fmt("{} rowid {}", dbop_cmd, d["kw"]:sub(2))
      os.execute(cmd)
      txt = _rc(full_name)
    elseif d["kw"] == "?" then
      cmd = fmt("{} ramble", dbop_cmd)
      os.execute(cmd)
      txt = _rc(hint_name)
    elseif d["kw"]:sub(1,1) == "*" then
      cmd = fmt("{} like '{}'", dbop_cmd, d["kw"]:sub(2))
      os.execute(cmd)
      txt = _rc(hint_name)
    else
      cmd = fmt("{} match '{}'", dbop_cmd, d["kw"])
      os.execute(cmd)
      txt = _rc(hint_name)
    end
    print(txt)
  end
end

----------------- blog ------------------
local function cgi_blog()
  local d = formdata()
  local tid, l = d['tid'], KV("blog")
  if "POST"==method() then
    local txt = d['txt']
    l:set(tid, txt)
    print(fmt("{} '{}' {}{}", tid, string.sub(txt, 1, sub_utf8(txt, 6)-1), #txt, "bytes saved"))
  else
    if 0==#tid then
      print("title:")
      for i,v in ipairs(l:getall()) do print(v) end
    elseif "dump"==tid then
	  local a = l:getall()
      local b_nam = ""
	  for i,v in ipairs(a) do
	    local fd = io.open(v, "w"); fd:write(l:get(v)); fd:close()
        b_nam = b_nam..fmt("\n{}", v)
        os.execute("md2repo "..v)
	  end
	  print(fmt("dump blog in alg:{}", b_nam))
	elseif "clear"==tid then
	  l:remove();os.execute("rm *.md") print("clear *.md")
	else print(l:get(tid))
    end
  end
end

----------------- stock ------------------
local function cgi_stock()
  pprint(os.date("%Y-%m-%d %H:%M:%S"))
  pprint("名字", "现价", "波动", "percent")
  local r = string.split(GET("http://qt.gtimg.cn/q=s_sz002236"), "~")
  pprint('大华', r[4], r[5], r[6])
  r = string.split(GET("http://qt.gtimg.cn/q=s_sz159919"), "~")
  pprint('300ETF', r[4], r[5], r[6])
  r = string.split(GET("http://qt.gtimg.cn/q=s_sz159915"), "~")
  pprint('创业ETF', r[4], r[5], r[6])
  r = string.split(GET("http://qt.gtimg.cn/q=s_sh512880"), "~")
  pprint('证券ETF', r[4], r[5], r[6])
end

----------- define route ---------------
servedir("/", "..")
handle("/cgi-bin/lude.cgi/user", cgi_user)
handle("/cgi-bin/lude.cgi/memo", cgi_memo)
handle("/cgi-bin/lude.cgi/fts",  cgi_fts)
handle("/cgi-bin/lude.cgi/blog", cgi_blog)
handle("/cgi-bin/lude.cgi/stock",cgi_stock)

