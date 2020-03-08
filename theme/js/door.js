g_xip = returnCitySN['cip']+'_'+encodeURI(returnCitySN['cname']);
function getHttp (pth, arg, cb) {
    $.ajax({
        type : 'GET',
        url : 'http://waer.f3322.net:55555/r.php'+pth,
        data : arg,
        //beforeSend: function(xhr) {xhr.setRequestHeader("XIP", g_xip)},
        headers : {'XIP':g_xip}
    }).done(cb)
}
function postHttp(pth, arg, cb) {
    $.post('http://waer.f3322.net:55555/r.php'+pth, arg, cb)
}
function getElemValue(e) {
  var elem =  document.getElementById(e);
  return elem.value
}
function getElemInner(e) {
  var elem =  document.getElementById(e);
  return elem.innerHTML
}
function bindInner2Elem(d, e) {
  var elem = document.getElementById(e);
  elem.innerHTML = d;
}
function bindValue2Elem(d, e) {
  var elem = document.getElementById(e);
  elem.value = d;
}

/////////////// various style content //////////////////////
var g_prepage = 0;
function showPreview(elem) {
  getHttp('/blog/preview', {page : g_prepage}, function(data) {
    var pd = eval('('+data+')');
    var oput = '';
    for (var i=0; i<pd.length; i++) {
      oput = oput + pd[i]['content'] + '-&gt<span onclick="onBlogTimeline('+pd[i]['date']+')">阅读'+pd[i]['date'] + '完整内容</span><hr />';
    }
    bindInner2Elem(oput, elem )
  } );
  g_prepage++;
}

function showTag(elem) {
	getHttp('/blog/title', '', function(data) {
	  var pd = eval('('+data+')');
	  var lst = pd['lst'];
      var oput = '';
	  for (var i=0; i<lst.length; i++) {
        var ma = lst[i].match(/([^>]+>)([^<]+).*/);// split <a>xxx</a>
        var title = ma[2];
        ma = ma[1].match(/.*\/([^"]+)/);// <a href="/xx/xx/tag"> get last word as tag
        var tag = ma[1];
		oput = oput + '<span class="tagList" id="tag'+tag+'" onclick=onBlogTag("'+tag+'")>'+title + '</span><hr/>';
	  }
      bindInner2Elem(oput, elem);
	  bindInner2Elem(pd['recUp'], 'recUp');
	  if (pd['sesame']) {
		bindInner2Elem(pd['sesame'], 'sesame');
	  }
	})
}

function showAbout(elem) {
  getHttp('/blog/about', '', function(data) {
    bindInner2Elem(data, elem )
  } )
}

//default action show by tag
function onDoorBody() {
    displayOne('blog');
    showTag('tagList');
}

function onHashChange() {
  getHttp('/blog/sesame/'+ location.hash.substring(1), '', function(data){
	bindInner2Elem(data, 'sesame');
  })
}

function onKeySearch(k, v) {
	var search_key = getElemValue(k);
	getHttp('/blog/search', {s : search_key}, function(data) {
	  var ctx = eval( '('+data+')' );
	  var oput = '';
	  for (var i=0; i<ctx.length; i++)  {
		  oput = oput + '<h1>'+ctx[i].date+'</h1>'+ctx[i].content+'<hr/>';
	  }
	  if (oput == '') {
		oput = 'No content match input keyword.';
	  }
	  bindInner2Elem(oput, v);
	});
}

function onBlogTag(t) {
  var oritxt = getElemInner('tag'+t);
  var pbr = oritxt.indexOf("<br")
  if (-1 == pbr) { // if exist br, means has content, no need further
    getHttp('/blog/tag/'+t, '', function(data) {
      var lst = eval('('+ data + ')');
      var oput = getElemInner('tag'+t) + '<br/>';
      for (var i=0; i<lst.length; i++) {
        var ma = lst[i].split(',')
        oput = oput + '<span onclick="onBlogTimeline('+ma[0]+')">' +lst[i] + '</span><br/>';
      }
      bindInner2Elem(oput, 'tag'+t)
    } )
  } else {
    var title = oritxt.substring(0, pbr);
    bindInner2Elem(title, 'tag'+t)
  }
}

function onBlogTimeline(d) {
  getHttp('/blog/timeline/'+d, '', function(data) {
    bindInner2Elem('<h1>'+d+'</h1>'+data, 'blog_content')
  } );
  $('html,body').animate({scrollTop: '0px'}, 500);
}

function onLogin(e) {
  var pwd = getElemValue(e);
  if (pwd!='') {
    postHttp('/auth/check', {pwd : pwd}, function(data){
      onDoorBody();
    } );
  } else {
    alert('Must input password')
  }
}

//////////////  switch to other part //////////////////

function toTmrecPage() {
  displayOne('tmrec');
  tm_startup()
}

function toAdminPage() {
  displayOne('admin')
}

function displayOne(e) {
  var arr = ["#e_blog", "#e_tmrec", "#e_admin"];
  var len = arr.length;
  var i = 0;
  for (; i<len; i++) {
    if (0<=arr[i].indexOf(e) ) {
      $(arr[i]).show();
    } else {
      $(arr[i]).hide();
    }
  }
}
//////////////////// admin edit ////////////////////////////

/// get markdown original text
function getBlog(whichDay, editId, tagId){
  var eday = document.getElementById(whichDay);
  var md = document.getElementById(editId);
  var tag = document.getElementById(tagId);
  getHttp("/blog/edit/"+eday.value, '', function(data, status){
    var json = eval('('+data+')');
    md.value = json[0];//.slice(1);//Dont why has a \n before,strip it
    tag.value = json[1];
  });
}

//\param[in] whichDay like 170518, editId blog content, tagId tag
function saveBlog(whichDay, editId, tagId){
  var eday = document.getElementById(whichDay);
  var md = document.getElementById(editId);
  var tag = document.getElementById(tagId);
  var mdText = md.value;
  var tagText = tag.value;
  postHttp("/admin/article/"+eday.value,
    { ctx : mdText, tag : tagText },
    function(data, status){ alert(data); }
  );
}

//////////////////////// tmrec func ////////////////////////////
function curDay(){
  var d = new Date();
  var day = d.getFullYear() - 2000; //save last 2 digit
  var tmp = d.getMonth() + 1;

  if (tmp < 10) {day += '0'
  }else {day += ''}
  day += tmp;
  tmp = d.getDate();
  if (tmp < 10) {
    day += '0';
  }
  day += tmp;
  return day;
}

//\param[in] whichDay like 170518, editId blog content, tagId tag
function saveRec(whichHour, dosth){
  var ehour = document.getElementById(whichHour);
  var rec = document.getElementById(dosth);
  postHttp("/tmrec/rec/"+curDay(),
    { hour: ehour.value , rec : rec.value },
    function(data, status){ alert(data); }
  );
}

/// get markdown original text
function getRec(eYear, eMonth, eTb){
  var eleY = document.getElementById(eYear);
  var eleM = document.getElementById(eMonth);
  var whichMonth = eleY.value + eleM.value;
  var tbcnt = document.getElementById(eTb);
  getHttp("/tmrec/rec/"+whichMonth,
    {hour: eleY.value, rec: eleM.value}, function(data, status){
    tbcnt.innerHTML = data;
  });
}

function searchRec(eSrch, eTb){
  var eleSch = document.getElementById(eSrch);
  var kwd = eleSch.value;
  var tbtm = document.getElementById(eTb);
  postHttp("/tmrec/searchRec/"+kwd, '', function(data, status){
    tbtm.innerHTML = data;
  });
}

function tm_startup(){
  var d = new Date();
  $("#eYear").val(d.getFullYear()-2000);

  var tmp = d.getMonth() + 1;
  var month = '';
  if (tmp < 10) {
    month += '0';
  }
  month += tmp;
  $("#eMonth").val(month);

  tmp = d.getHours();
  tmp = Math.ceil(tmp/6)*6;
  if (tmp<12){ tmp = 12;}
  $("#eHour").val(tmp.toString());

  d = document.getElementById("eDo");
  postHttp("/tmrec/justDo/"+curDay()+"/"+tmp.toString(), '', function(data, status){
    d.value = data.slice(1);//strip first \n
  });
}

