local mod = {}
mod.ar = function(qs, ctx)
  for _, txt in ipairs(dt.lsfile("../ar")) do
    print(txt)
  end
end

return mod

