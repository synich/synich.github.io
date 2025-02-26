function push_memo() {
  function _cb(txt, st){
    W.jq("hnt")(txt)
  }
  var kwd = W.jq("txt")()
  var idx = W.jq("sel")()
  W.ajax("post", '/cgi-bin/memo.cgi', {'k':kwd,'i':idx}, _cb)
}

async function do_blog(tid,tarea) {
  let e = W.jq(tid)()
  let txt = W.jq(tarea)
  if (e) {
	if (txt().length<30) {
	  let r = await W.awax("get", "/cgi-bin/blog.cgi", {"tid":e})
      txt(r)
	} else {
	  let r = await W.awax("post", "/cgi-bin/blog.cgi", {"tid":e,"txt":txt()})
	  alert(r)
	}
  } else {
	W.hxdom("get", "/cgi-bin/blog.cgi", tid, "#hnt")
  }
}

function clear_txt(id){
  let e = W.jq(id)
  e('')
}

function showpanel(id){
  if (location.hostname.match(/158370.xyz|\d{1,3}.\d{1,3}.\d{1,3}/)) {
  let e = W.jq(id)
  e.disp("block")
  }
}

function get_stock(){
  W.hxdom("get", "/cgi-bin/stock.cgi", null, "#hnt")
}

function main(){
  //sync textarea to span and expand height
  W.ko("#u_aht").sync = (v,m)=>{m.s(v)}
  var act = W.ko("u_act")
  act.show = (v,m)=>{if (v=="blog") {m.b.disp("inline");m.m.disp("none");m.t.disp("none")}
    else {m.m.disp("inline");m.b.disp("none");m.t.disp("none")}
    // else if (v=="t"){m.m.disp("none");m.b.disp("none");m.t.disp("inline")}
  }
  act["bpll"].on("click", ()=>{W.hxdom("get", "/cgi-bin/memo.cgi", "sel", "#hnt")})
  act["bpsh"].on("click", push_memo)
  act["bblg"].on("click", ()=>{do_blog("tid","txt")})
  act["bcls"].on("click", ()=>{clear_txt("txt")})
  act["bstk"].on("click", get_stock)
  showpanel('selfhost')
}

main()