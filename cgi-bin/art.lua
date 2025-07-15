--pb lua cgi for /cgi-bin/lude.cgi/art/ar
local mod = {}
mod.ar = function(qs, ctx, m)
  local a = dt.lsfile("../ar")
  if a then
    for _, txt in ipairs(a) do print(txt) end
  end
  print(m.."<br>qs is:");var_dump(qs)
  print("<br>body:");var_dump(ctx)
end

return mod

