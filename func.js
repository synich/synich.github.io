/// only used for FORM element
function getElemValue(elemId) {
  var elem = document.getElementById(elemId);
  return elem.value
}

function http_req(mth, url, content) {
    return new Promise(function (resolve, reject) {
        var xhr = new XMLHttpRequest();
        xhr.open(mth, url);
        xhr.onload = resolve;
        xhr.onerror = reject;
        if (mth === 'POST') {
			xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded;");
			xhr.send(content);
		} else {
			xhr.send();
		}
    });
}

var g_waer_url = 'http://waer.f3322.net:55555/rest.php/'

function fixcall(id, rsp, mth, param) {
  var url = getElemValue(id);
  var erep = document.getElementById(rsp);
  var epm = param ? document.getElementById(param) : null;
  var pam = epm ? epm.value : '';
  http_req(mth, g_waer_url+'digest/'+ url, pam)
    .then(function (e) {
        console.log(e);
		erep.innerHTML = e.target.response
    }, function (e) {
        // handle errors
    });
}

function goosearch(id, rsp, token, act) {
  var kwd = getElemValue(id);
  var tkt = getElemValue(token);
  var erep = document.getElementById(rsp);
  var action = getElemValue(act);
  var targeturl = g_waer_url+'pgext/goosearch/'+kwd+'?t='+tkt;
  if (action== 'in' ) {
  http_req('GET', targeturl+ '&act=i', '')
    .then( function(e) {
        erep.innerHTML = e.target.response
      }
    )
  } else {
    window.open(targeturl+ '&act=o', '_blank');
  }
}

function crosswall(id, rsp, token, act) {
  var url = getElemValue(id);
  url = url.replace(/ +/g, '+');
  var b64 = btoa(url);
  var tkt = getElemValue(token);
  var erep = document.getElementById(rsp);
  var action = getElemValue(act);
  var targeturl = g_waer_url+'pgext/crosswall/'+b64+'?t='+tkt;
  if (action== 'in' ) {
  http_req('GET', targeturl+ '&act=i' , '' )
    .then( function(e) {
        erep.innerHTML = e.target.response
      }
    )
  } else {
    window.open(targeturl+ '&act=o', '_blank');
  }
}
