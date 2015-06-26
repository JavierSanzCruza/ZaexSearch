
var save = false;
var del = false;


window.onhashchange = function () {
  document.getElementById("messageDiv").innerHTML="";
};

function updateDiv(time)
{
    document.getElementById("messageDiv").innerHTML="The results will appear in about " + time + " seconds."
}

function onBlurUpdate()
{
    document.getElementById("messageDiv").innerHTML="";
}

function dragSave(ev)
{
    ev.dataTransfer.setData("text/html", ev.target.id);
    save = true;
    del = false;
}
function resClickUpdate(text)
{
    document.getElementById("ResClicked").innerHTML=xmlhttp.responseText;
}
function onResultClick(serverURL, searchURL, query, rank)
{

	var cadena = serverURL + "?query=" + query + "&rank="+rank;
    	callAJAX(cadena, resClickUpdate);

	window.open(searchURL, '_blank');
}
function updateSaved()
{
    document.getElementById("ResSaved").innerHTML=xmlhttp.responseText;
}


function updateSavedInOpen()
{
    document.getElementById("ResSaved").innerHTML=xmlhttp.responseText;
    if(xmlhttp.readyState == 4)
    {
        var url = 'http://localhost:11000/filter/save'
        var actualQuery = document.getElementById("queryText").innerHTML;
	var actualSearchID = document.getElementById("searchid").innerHTML;
        onRetrieve(url, actualQuery)
    }   
}

function updateSavedText(text)
{
  document.getElementById("ResSaved").innerHTML = text;
}
function updateSaveAndClose()
{
    document.getElementById("errorSave").innerHTML=xmlhttp.responseText;
    if(xmlhttp.readyState == 4 && xmlhttp.responseText == "")
    {
        updateSavedText("<h4>Results saved</h4>");
        var url = 'http://localhost:11000/filter/save'
        var actualQuery = document.getElementById("queryText").innerHTML;
        onRetrieve(url, actualQuery)
    }   
}

function updateSearched(text)
{
    document.getElementById("ResSearch").innerHTML=xmlhttp.responseText;
    if(xmlhttp.readyState == 4)
    {
        onBlurUpdate()
        document.getElementById("retrieve").disabled= false
        var filters = document.getElementById("filterSearcher").getElementsByTagName("input");
    var i = 1;
    var searchFilters = [];
    var f;
    for(i = 1; i < filters.length; ++i)
    {
	filters[i].disabled = false;
    }
    }
}

function updateOnRetrieve()
{
  document.getElementById("ResSearch").innerHTML = xmlhttp2.responseText;
  if(xmlhttp2.readyState == 4)
  {
	document.getElementById("retrieve").disabled = false;
	var filters = document.getElementById("filterSearcher").getElementsByTagName("input");
	    var i = 1;
	    var searchFilters = [];
	    var f;
	    for(i = 1; i < filters.length; ++i)
	    {
		filters[i].disabled = false;
	    }
  }
}
function updateDiversity(text)
{
    document.getElementById("ResDiversity").innerHTML=xmlhttp.responseText;
}
function dragDelete(ev)
{
    ev.dataTransfer.setData("text/html", ev.target.id);
    save = false;
    del = true;
}
function allowDropSave(ev)
{
    if (save == true)
    {
        ev.preventDefault();
    }
}

function allowDropDelete(ev)
{
    if (del == true)
    {
        ev.preventDefault();
    }
}

function dropSave(ev, actualQuery)
{
    ev.preventDefault();
    var data = ev.dataTransfer.getData("text/html");
    var query = document.getElementById(data).getElementsByClassName("siteQuery")[0].innerHTML;
    var rank = document.getElementById(data).getElementsByClassName("siteRank")[0].innerHTML;
    var cadena = "http://localhost:11000/metases/lnk/save?query=" + query + "&rank="+rank;

    callAJAX(cadena, updateSaved);
    var url = 'http://localhost:11000/filter/save'

    onRetrieve(url, actualQuery)


    return false;

}

function onDelete(query, rank)
{
    var cadena = "http://localhost:11000/metases/lnk/delete?query=" + query + "&rank="+rank;
    callAJAX(cadena, updateSaved);
    return false;

}

function dropDelete(ev, actualQuery) {
    ev.preventDefault();
    var data = ev.dataTransfer.getData("text/html");
    var url = document.getElementById(data).getElementsByClassName("siteURL")[0].innerHTML;
    var query = document.getElementById(data).getElementsByClassName("siteQuery")[0].innerHTML;
    var rank = document.getElementById(data).getElementsByClassName("siteRank")[0].innerHTML;
    var cadena;

    onDelete(query, rank)
    var url = 'http://localhost:11000/filter/save'

    onRetrieve(url, actualQuery)
}

function onSaveAndClose(serverURL)
{
    var nombre = document.getElementById("save").getElementsByTagName("input")[0].value;
    var overwrite;
    var check = document.getElementById("save").getElementsByTagName("input")[1];
    if(check.checked == true)
    {
        overwrite = "True";
    }
    else
    {
        overwrite = "False";
    }

    cadena = serverURL + "?metaName="+nombre+"&overwrite="+overwrite;
    callAJAX(cadena, updateSaveAndClose);
    
    

}

function onMetaClose(serverURL)
{
	callAJAX(serverURL, updateSaved);
    return false;
}

function onOpen(serverURL)
{
    var nombre = document.getElementById("open").getElementsByTagName("input")[0].value;
    cadena = serverURL + "?metaName="+nombre;
    callAJAX(cadena, updateSavedInOpen);    
}

function onRetrieve(serverURL, search)
{
    var check = document.getElementById("retrieve");
    var filter;
    var filterNames = ["Faroo", "Google", "Carrot2", "Bing"];
    var faroo;
    var google;
    var carrot2;
    if(check.checked)
    {
        filter = "False";
    }
    else
    {
        filter = "True";
    }

   var searchid = document.getElementById("searchid").innerHTML;
    check.disabled = true;
    if(check.checked)
    {
        filter = "True";
    }
    else
    {
        filter = "False";
    }

    var filters = document.getElementById("filterSearcher").getElementsByTagName("input");
    var i = 1;
    var searchFilters = [];
    var f;
    for(i = 1; i < filters.length; ++i)
    {
	filters[i].disabled = true;
        if(filters[i].checked)
        {
            searchFilters[i] = "True";
        }
        else
        {
            searchFilters[i] = "False";
        }
    }

    cadena = serverURL + "?search="+search+"&filter="+filter;

    i=0;
    for(i = 1; i < filters.length; ++i)
    {
        cadena = cadena + "&" + filterNames[i-1] + "=" + searchFilters[i];
    }

    cadena = cadena + "&searchid=" + searchid
    callAJAX2(cadena, updateOnRetrieve);
}

function onRelevanceFeedback(serverURL, search)
{
    updateDiv('10');
    var check = document.getElementById("retrieve").getElementsByTagName("input")[0];
    var filter;
    if(check.checked)
    {
        filter = "True";
    }
    else
    {
        filter = "False";
    }

    cadena = serverURL + "?search="+search+"&filter="+filter;
    callAJAX(cadena, updateSearched);
}

function onDiversity(serverURL, search)
{
    updateDiv('40');
    var check = document.getElementById("retrieve");
    var filter;
    check.disabled = true;
    var filterNames = ["Faroo", "Google", "Carrot2", "Bing"];
    var filters = document.getElementById("filterSearcher").getElementsByTagName("input");
    var i = 1;
    var searchFilters = [];
    var f;
    if(check.checked)
    {
        filter = "False";
    }
    else
    {
        filter = "True";
    }

    cadena = serverURL + "?search="+search+"&filter="+filter;
    callAJAX(cadena, updateSearched);
}

function onEvalDiversity(serverURL, search)
{
    var lambda = document.getElementById("lambda").value;
    cadena = serverURL + "?search=" + search + "&lambda="+lambda;
    callAJAX(cadena, updateDiversity)
}

var xmlhttp;
function callAJAX(query, callbackFunction)
{
    xmlhttp = new XMLHttpRequest();
    
    if(callbackFunction)
    {
      xmlhttp.onreadystatechange = callbackFunction;
    }
    else
    {
      xmlhttp.onreadystatechange = function()
      {
        
      }
    }
    
    xmlhttp.open("GET", query, true);
    xmlhttp.send();
}

var xmlhttp2;
function callAJAX2(query, callbackFunction)
{
    xmlhttp2 = new XMLHttpRequest();
    
    if(callbackFunction)
    {
      xmlhttp2.onreadystatechange = callbackFunction;
    }
    else
    {
      xmlhttp2.onreadystatechange = function()
      {
        
      }
    }
    
    xmlhttp2.open("GET", query, true);
    xmlhttp2.send();
}

function onEvalRanksym(serverURL, search)
{
    var url = serverURL + '?search='+search
    var sliders = ['Faroo', 'Google', 'Bing', 'Carrot2'];
    for(s=0; s < sliders.length; ++s)
    {
        document.getElementById(sliders[s] + "Text").value = document.getElementById(sliders[s]).value;
        url += "&" + sliders[s] + "=" + document.getElementById(sliders[s]).value;
    }

    callAJAX(url, updateSearched)
}
