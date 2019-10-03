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

function fixcall(id, rsp, mth, param) {
  var eid = document.getElementById(id);
  var url = eid.value;
  var erep = document.getElementById(rsp);
  var epm = document.getElementById(param);
  var pam = btoa(epm.value)
  http_req(mth, 'http://waer.f3322.net:55555/rest.php/digest/'+url, 'page=1&kwd='+pam)
    .then(function (e) {
        console.log(e);
		erep.innerHTML = e.target.response
    }, function (e) {
        // handle errors
    });
}
