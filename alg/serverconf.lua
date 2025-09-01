-- change admin/user default prefix
--ClearPermissions()
--AddUserPrefix("/priv")
DenyHandler(function()
  print([[
  <script src="/static/mel.min.js?v=2" type="text/javascript"></script>
  <meta content="width=device-width, initial-scale=1" name="viewport">
  <input type="text" id="ei1" name="token">
  <script>function val_t(){return W.jq("ei1")()}
  function login(rsp){location.reload()}</script>
  <button onclick='W.ajax("POST", "/cgi-bin/lude.cgi/user", {"token":val_t()}, login)'>Login</button>
  ]])
end)

-- Provide a lua function that will be run once, when the server is ready to start serving.
-- OnReady(function() print(1357) end)

-- reverse to another server(only IP&port), drop the matched path, transfer rest path and querystring
AddReverseProxy("/cgi-bin/node.cgi", "http://localhost:3080/")
AddReverseProxy("/node", "http://localhost:3080/")

-- use custom route
ServerFile("./route.lua")
