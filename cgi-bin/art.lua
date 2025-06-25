--pb lua cgi for /cgi-bin/lude.cgi/art/ar
local mod = {}
mod.ar = function(qs, ctx)
  for _, txt in ipairs(dt.lsfile("../ar")) do
    print(txt)
  end
  print("<br>qs is:");var_dump(qs)
  print("<br>body:");var_dump(ctx)
end

return mod

