/*250108;choose entry with SEP*/!(function(top){"use strict";const SEP="W";var _G;top[SEP]||(_G=top[SEP]={});function _get_el(elemId){var el = elemId;if (typeof elemId == "string"){let eid = elemId[0]==='#' ? elemId.slice(1) : elemId;el = document.getElementById(eid);if (el === null) {alert(`id[${elemId}] not exist`)}}return el}function jq(elemId){var el = _get_el(elemId);var st = new Set(["INPUT","TEXTAREA","SELECT"]);var ndCh = st.has(el.nodeName)?'v':'i';var ret = function(val){if (val===undefined){return ndCh=='v'?el.value:el.innerHTML}else {ndCh=='v'?el.value=val:el.innerHTML=val; return ret}};ret.o = el;ret.on = (ev, fn)=>{el.addEventListener(ev, fn)};ret.tog = (n)=>{el.classList.toggle(n)};ret.disp = (s)=>{el.style.display=s};ret.vis = (b)=>{el.style.visibility = b?"visible":"hidden"};return ret}function _attr_bind(node, vm){Array.from(node.childNodes).forEach(_n => {if (1==_n.nodeType){let _a = _n.getAttribute("db");if (_a) {_a.split(',').forEach(function(_db){let _b = _db.split(':');if ("el"==_b[0]) {vm[_b[1]]=jq(_n)}else if ("fn"==_b[0]) {let ev = _n.nodeName=="SELECT"?'change':'input';let tmout;function _smooth(e) {clearTimeout(tmout);tmout=setTimeout((e)=>{vm[_b[1]](e.target.value, vm)}, 250, e)}_n.addEventListener(ev, _smooth)}})}if (_n.childNodes) {_attr_bind(_n, vm)}}})} function ko(elemId){var elem=_get_el(elemId);var vm = {};_attr_bind(elem, vm);return vm}function ajax(method, url, data, cb_func, timeout=10000) {function encodeParams(p) {let _c= (key)=>`${encodeURIComponent(key)}=${encodeURIComponent(p[key])}`;return Object.keys(p).map(_c).join("&")}method = method.toUpperCase();if (data) { data = encodeParams(data) }if (method === "GET" && data) { url=`${url}?${data}`; data = null }var xhr = new XMLHttpRequest();xhr.open(method, url, true);xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");var timer = setTimeout(function() {xhr.abort();cb_func(`ERROR: Request timeout ${timeout}ms`, 408)}, timeout);xhr.onreadystatechange = function() {if (xhr.readyState === 4) {clearTimeout(timer);cb_func(xhr.responseText, xhr.status)}};if (data) { xhr.send(data) }else      { xhr.send()  }}function awax(method, url, data, timeout=10000, isrej=false) {return new Promise( (resolve,reject)=>{ajax(method, url, data, (resp, st)=>{let ok= (st>=200 && st<300)? true: false;if(ok){resolve(resp)}else{if(isrej){reject(resp)} else{resolve(`E${st}: ${resp}`)}}}, timeout)})}function _s2el(s){let t=document.createElement("div");t.innerHTML=s;return t.firstChild}function hxdom(method, url, id_elem, target, opt={}, timeout=10000) {function _subdom(resp, code){if (code >=300 || code <200) {alert(resp)}var swap = opt["swap"];if (swap){let ori = jq(target).o;if ("b"==swap[0]){ori.insertBefore(_s2el(resp), ori.firstChild)}else if("a"==swap[0]){ori.appendChild(_s2el(resp))}else {jq(target)("")}}else {jq(target)(resp)}}var data={};if (id_elem) {if (typeof id_elem =="string") {var a_in=id_elem.replace(/\s+/g, "").split(",");for (let k of a_in){let e = jq(k), n=e.o.getAttribute("name");n=n?n:k;data[n]=e()}} else {data=id_elem}}ajax(method, url, data, _subdom, timeout)}_G.jq=jq;_G.ko=ko;_G.ajax=ajax;_G.awax=awax;_G.hxdom=hxdom})(this)


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

  //sync textarea to span and expand height
W.ko("#u_aht").sync = (v,m)=>{m.s(v)}
var act = W.ko("u_act")
act.show = (v,m)=>{if (v=="blog") {m.b.disp("inline");m.m.disp("none");m.t.disp("none")}
  else {m.m.disp("inline");m.b.disp("none");m.t.disp("none")}
  // else if (v=="t"){m.m.disp("none");m.b.disp("none");m.t.disp("inline")}
}
  }
}

