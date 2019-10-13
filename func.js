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

function goosearch(id) {
  var kwd = getElemValue(id);
  window.open(g_waer_url+'pgext/goosearch/'+kwd, '_blank' )
}

function crosswall(id) {
  var url = getElemValue(id);
  var b64 = btoa(url)
  window.open(g_waer_url+'pgext/crosswall/'+b64, '_blank' )
}
