function push_memo() {
  function _cb(txt, st){
    W.jq("hnt")(txt)
  }
  var kwd = W.jq("txt")()
  var idx = W.jq("sel")()
  W.ajax("post", '/cgi-bin/lude.cgi/memo', {'k':kwd,'i':idx}, _cb)
}

async function fts_get(tid, tarea) {
  let e = W.jq(tid)()
  let txt = W.jq(tarea)
  let query = txt()
  if (e=="?"){query=e}
  else if (e!=""){query="#"+e}
  let r = await W.awax("get", "/cgi-bin/lude.cgi/fts", {"kw":query})
  txt(r.trim())
}

async function fts_set(tid, tarea) {
  let e = W.jq(tid)()
  let txt = W.jq(tarea)
  let r = await W.awax("post", "/cgi-bin/lude.cgi/fts", {"kw":e, "txt":txt()})
  txt(r.trim())
}

async function do_blog(tid,tarea) {
  let e = W.jq(tid)()
  let txt = W.jq(tarea)
  if (e) {
	if (txt().length<30) {
	  let r = await W.awax("get", "/cgi-bin/lude.cgi/blog", {"tid":e})
      txt(r)
	} else {
	  let r = await W.awax("post", "/cgi-bin/lude.cgi/blog", {"tid":e,"txt":txt()})
	  alert(r)
	}
  } else {
	W.hxdom("get", "/cgi-bin/lude.cgi/blog", tid, "#hnt")
  }
}

function clear_txt(ids){
  for (let i = 0; i<ids.length; i++){
    let e = W.jq(ids[i]); e('')
  }
}

function showpanel(id){
  if (location.hostname.match(/158370.xyz|\d{1,3}.\d{1,3}.\d{1,3}/)) {
  let e = W.jq(id)
  e.disp("block")
  }
}

function get_stock(){
  W.hxdom("get", "/cgi-bin/lude.cgi/stock", null, "#hnt")
}

function main(){
  //sync textarea to span and expand height
  W.ko("u_aht").sync = (v,m)=>{m.s(v)}
  //show/hide blog/memo/txt
  var act = W.ko("u_act")
  act.show = (v,m)=>{
    if (v=="blog") {m.i.disp("inline");m.b.disp("inline");m.m.disp("none");m.t.disp("none")}
    else if (v=="fts"){m.m.disp("none");m.i.disp("inline");m.b.disp("none");m.t.disp("inline")}
    else {m.m.disp("inline");m.i.disp("none");m.b.disp("none");m.t.disp("none")}
  }
  act.bpll = ()=>{W.hxdom("get", "/cgi-bin/lude.cgi/memo", "sel", "#hnt")}
  act.bpsh = push_memo
  act.bfts_get = ()=>{fts_get("tid","txt")}
  act.bfts_set = ()=>{fts_set("tid","txt")}
  act.bblg = ()=>{do_blog("tid","txt")}
  act.bcls = ()=>{clear_txt(["txt", "tid"])}
  act.bstk = get_stock
  showpanel('selfhost')
}

main()
