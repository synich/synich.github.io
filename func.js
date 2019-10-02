function http_req(method, url) {
    return new Promise(function (resolve, reject) {
        var xhr = new XMLHttpRequest();
        xhr.open(method, url);
        xhr.onload = resolve;
        xhr.onerror = reject;
        xhr.send();
    });
}

function fixcall(id) {
  var eid = document.getElementById(id);
  var url = eid.value;
  console.log(url)
  http_req('GET', 'http://waer.f3322.net:55555/rest.php/digest/'+url)
    .then(function (e) {
        console.log(e.target.response);
    }, function (e) {
        // handle errors
    });
}
