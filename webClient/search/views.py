# -*- encoding: utf-8 -*-
# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.http import HttpResponse
from search.models import *
import urllib
from search.Webservice.webservice import *
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from search.Diversity.diversity import Diversity
from search.Metasearcher.rankSymMetasearcher import RankSymMetasearcher
import numpy as np

####CONSTANTS#####
sizeILD = 10




#################### VIEWS ########################################

def index(request):
    return render(request, 'search/index.html')


def search(request):
    if request.GET['search'] is None:
        return HttpResponse(status=404)

    filtering = False
    if request.GET.get('filter') is None:
        filtering = False
    else:
        filtering = (request.GET['filter'] == 'True')

    search = request.GET['search']

    ws = Webservice()
    list_result = ws.call_ws_search(search, filtering, request.META['REMOTE_ADDR'], request.META['HTTP_USER_AGENT'])

    saveL = False
    previous = Search.objects.filter(query__exact = search)
    if previous is None or previous.__len__() == 0:
        srch = Search()
        srch.query = search
        srch.numResults = list_result['search'].__len__()
        srch.save()
        saveL = True

    listLinks = list()
    i = 1
    for result in list_result['search']:
        lnk = Link()
        lnk.url = result['url']
        lnk.title = result['title']
        lnk.descr = result['snippet']
        lnk.query = search
        lnk.rank = result['rank']
        lnk.saved = result['saved']
        if filtering is False or lnk.saved is False:
            listLinks.append((lnk, result['source']))
        if saveL is True:
            lnkres = SearchResult()
            lnkres.url = lnk.url
            lnkres.snippet = lnk.descr
            lnkres.searchID = srch
            lnkres.rank = lnk.rank
            lnkres.title = lnk.title
            lnkres.value = result['value']
            lnkres.saved = result['saved']
            lnkres.save()

    clickedLinksList = list()
    for result in list_result['clicked']:
        lnk = Link()
        lnk.url = result['url']
        lnk.title = result['title']
        lnk.descr = result['snippet']
        lnk.query = search
        lnk.rank = 1

        clickedLinksList.append(lnk)

    savedLinksList = list()
    for result in list_result['saved']:
        lnk = Link()
        lnk.url = result['url']
        lnk.title = result['title']
        lnk.descr = result['snippet']
        lnk.query = result['query']
        lnk.rank = result['rank']


        savedLinksList.append(lnk)

    context = {'searchid': -1, 'linkList': listLinks, 'serverName': request.META['SERVER_NAME'], 'serverPort': request.META['SERVER_PORT'],'query2': search,  'query': urllib.quote(request.GET['search'].encode("UTF-8")), 'clickedList': clickedLinksList, 'savedList':savedLinksList}
    return render(request, 'search/indexTemp.html', context)


def clicked(request):
    if len(request.GET.keys()) > 0:
		if request.GET['query'] is None or request.GET['rank'] is None:
			return HttpResponse(status=404)
    else:
        return HttpResponse(status=404)
    query = urllib.quote(request.GET['query'].encode("UTF-8"))
    url = 'http://localhost:10000/clicked?query='+query+'&clientIP='+request.META['REMOTE_ADDR']+'&rank='+request.GET['rank']
    ws = Webservice()
    list_result = ws.call_ws(url, request.META['HTTP_USER_AGENT'])
    listLinks = list()
    for result in list_result:
		lnk = Link()
		lnk.url = result['url']
		lnk.title = result['title']
		lnk.descr = result['snippet']
		lnk.rank = 1

		listLinks.append(lnk)

    context = {'clickedList': listLinks}
    return render(request, 'search/clicked.html', context)

def savelink(request):
    if len(request.GET.keys()) > 0:
        if request.GET['query'] is None or request.GET['rank'] is None:
			return HttpResponse(status=404)
    else:
        return HttpResponse(status=404)
    query = urllib.quote(request.GET['query'].encode("UTF-8"))
    # create credential for authentication
    url = 'http://localhost:10000/metases/lnk/save/?query='+query+'&clientIP='+request.META['REMOTE_ADDR']+'&rank='+request.GET['rank']
    ws = Webservice()
    list_result = ws.call_ws(url, request.META['HTTP_USER_AGENT'])

    listLinks = list()
    for result in list_result:
        lnk = Link()
        lnk.url = result['url']
        lnk.title = result['title']
        lnk.descr = result['snippet']
        lnk.query = result['query']
        lnk.rank = result['rank']

        listLinks.append(lnk)
    context = {'serverName' : request.META['SERVER_NAME'], 'serverPort' : request.META['SERVER_PORT'], 'linkList': listLinks}
    return render(request, 'search/saved.html', context)

def deleteSavedlink(request):
    if len(request.GET.keys()) > 0:
        if request.GET.get('query') is None:
            return HttpResponse(status=404)
        if request.GET.get('rank') is None:
            return HttpResponse(status=404)
    else:
        return HttpResponse(status=404)
    originQuery = urllib.quote(request.GET['query'].encode("UTF-8"))
    rank = urllib.quote(request.GET['rank'].encode("UTF-8"))
    url = 'http://localhost:10000/metases/lnk/delete?clientIP='+request.META['REMOTE_ADDR']+'&query='+originQuery+'&rank='+rank
    ws = Webservice()
    list_result = ws.call_ws(url, request.META['HTTP_USER_AGENT'])
    listLinks = list()
    for result in list_result:
        lnk = Link()
        lnk.url = result['url']
        lnk.title = result['title']
        lnk.descr = result['snippet']
        lnk.query = result['query']
        lnk.rank = result['rank']

        listLinks.append(lnk)
    context = {'serverName' : request.META['SERVER_NAME'], 'serverPort' : request.META['SERVER_PORT'], 'linkList': listLinks}
    return render(request, 'search/saved.html', context)

def closeMetases(request):
    url = 'http://localhost:10000/metases/close?clientIP='+request.META['REMOTE_ADDR']
    ws = Webservice()
    ws.call_ws(url, request.META['HTTP_USER_AGENT'])
    linkLists = list()
    context = {'linkList': linkLists}
    return render(request, 'search/saved.html', context)

def openMetases(request):
    if len(request.GET.keys()) == 0:
        return HttpResponse(status=404)
    if request.GET.get('metaName') is None:
        metaName = ''
    else:
        metaName = urllib.quote(request.GET['metaName'].encode("UTF-8"))
    url = 'http://localhost:10000/metases/open?clientIP='+request.META['REMOTE_ADDR']+'&metaName='+ metaName
    ws = Webservice()
    list_result = ws.call_ws(url, request.META['HTTP_USER_AGENT'])
    listLinks = list()
    if list_result is not None:
        for result in list_result:
            lnk = Link()
            lnk.url = result['url']
            lnk.title = result['title']
            lnk.descr = result['snippet']
            lnk.query = result['query']
            lnk.rank = result['rank']

            listLinks.append(lnk)

    context = {'serverName' : request.META['SERVER_NAME'], 'serverPort' : request.META['SERVER_PORT'], 'linkList': listLinks}
    return render(request, 'search/saved.html', context)


def saveAndCloseMeta(request):
    if len(request.GET.keys()) == 0:
        return HttpResponse(status=404)
    if request.GET.get('metaName') is None or request.GET.get('metaName') == '' or request.GET.get('overwrite') is None:
        return HttpResponse("Name not available")
    ws = Webservice()
    overwrite = (request.GET['overwrite'] == "True")
    metaName = urllib.quote(request.GET['metaName'].encode("UTF-8"))
    if(overwrite == False):
        url = 'http://localhost:10000/metases/available?clientIP='+request.META['REMOTE_ADDR']+'&metaName='+metaName
        res = ws.call_ws(url , request.META['HTTP_USER_AGENT'])
        if res['available'] == False:
            return HttpResponse("Name not available")
    url = 'http://localhost:10000/metases/save?clientIP='+request.META['REMOTE_ADDR']+'&metaName='+metaName
    ws.call_ws(url, request.META['HTTP_USER_AGENT'])
    return HttpResponse("")


def retrieveSearch(request):
    if len(request.GET.keys()) == 0:
        return HttpResponse(status=404)
    if request.GET.get('search') is None or request.GET.get('filter') is None:
        return HttpResponse(status=404)
    if request.GET.get('searchid') is None:
        return HttpResponse(status=404)

    diversified = False
    if(request.GET['searchid'] != '-1'):
        diversified = True
    filtering = False
    if request.GET['filter'] is None:
        filtering = False
    else:
        filtering = (request.GET['filter'] == 'False')


    listFilter = []
    for r in Ranker.objects.all():
        filter = request.GET.get(r.name)
        if filter is not None and filter == 'False':
            listFilter.append(r.rankerID)

    query = urllib.quote(request.GET['search'].encode("UTF-8"))
    if diversified is False:

        url = 'http://localhost:10000/filter/save?query='+query+'&clientIP='+request.META['REMOTE_ADDR']+'&filter='
        if filtering is True:
            url = url + 'True'
        else:
            url = url + 'False'

        rankers = Ranker.objects.all()
        listFilter = []
        for r in rankers:
            filter = request.GET.get(r.name)
            if filter is not None:
                url += '&' + r.name + '=' + filter

        ws = Webservice()
        list_result = ws.call_ws(url, request.META['HTTP_USER_AGENT'])

        listLinks = list()
        for result in list_result:
            i = 0
            lnk = Link()
            lnk.url = result['url']
            lnk.title = result['title']
            lnk.descr = result['snippet']
            lnk.rank = result['rank']
            lnk.saved = result['saved']

            listLinks.append((lnk, result['source']))

        context = {'searchid': -1, 'serverName' : request.META['SERVER_NAME'], 'serverPort' : request.META['SERVER_PORT'], 'query2': request.GET['search'], 'query': urllib.quote(request.GET['search'].encode("UTF-8")), 'linkList': listLinks}
        return render(request, 'search/searched.html', context)
    else:
        search = Search.objects.filter(searchID__exact = int(request.GET['searchid'])).first()

        results = SearchResult.objects.filter(searchID__exact = search).order_by('rank')

        ##Obtener de la base de datos la matriz de diversidad
        firstRes = results.first().resultID
        lastRes = results.last().resultID
        distQ = Distances.objects.filter(firstDoc__resultID__gte = firstRes, firstDoc__resultID__lte = lastRes).order_by('firstDoc', 'secondDoc')
        if distQ is None or distQ.__len__() == 0:
            return HttpResponse(status=404)

        matrix = [[0 for x in range(results.__len__())] for y in range(results.__len__())]
        for dist in distQ:
            matrix[dist.firstDoc.resultID-firstRes][dist.secondDoc.resultID-firstRes] = dist.distance
            matrix[dist.secondDoc.resultID-firstRes][dist.firstDoc.resultID-firstRes] = dist.distance

        ranking = Diversity.diversityRanking(matrix, results, 0.5)

        url = 'http://localhost:10000/filter/save?query='+query+'&clientIP='+request.META['REMOTE_ADDR']+'&filter=False'

        rankers = Ranker.objects.all()
        listFilter = []
        for r in rankers:
            filter = request.GET.get(r.name)
            if filter is not None:
                url += '&' + r.name + '=True'

        ws = Webservice()
        list_result = ws.call_ws(url, request.META['HTTP_USER_AGENT'])



        lnkList = []
        for i in range(results.__len__()):
            result = list_result[ranking[i]-1]
            lnk = Link()
            lnk.url = result['url']
            lnk.title = result['title']
            lnk.descr = result['snippet']
            lnk.query = search.query
            lnk.rank = result['rank']
            lnk.saved = result['saved']

            introduce = True
            if lnk.saved is True and filtering is True:
                introduce = False

            sourceslist=[]
            numCoinc = 0
            for source in result['source']:
                if listFilter.__contains__(source):
                    numCoinc += 1
            if numCoinc == result['source'].__len__():
                introduce = False

            if introduce is True:
                lnkList.append((lnk, result['source']))
        context = {'searchid' : request.GET['searchid'], 'serverName' : request.META['SERVER_NAME'], 'serverPort' : request.META['SERVER_PORT'], 'query2': request.GET['search'], 'query': urllib.quote(request.GET['search'].encode("UTF-8")), 'linkList': lnkList}
        return render(request, 'search/searched.html', context)

def doRelevanceFeedback(request):

    if len(request.GET.keys()) == 0:
        return HttpResponse(status=404)
    if request.GET['search'] is None or request.GET['filter'] is None:
        return HttpResponse(status=404)

    search = urllib.unquote(request.GET['search']).encode("UTF-8")
    query = urllib.quote(search)
    filtering = False
    if request.GET['filter'] is None:
        filtering = False
    else:
        filtering = (request.GET['filter'] == 'True')


    # create credential for authentication
    url = 'http://localhost:10000/relevance?query='+query+'&clientIP='+request.META['REMOTE_ADDR']+'&filter=False'
    ws = Webservice()
    list_result = ws.call_ws(url, request.META['HTTP_USER_AGENT'])


    saveL = False
    search = list_result['query']
    previous = Search.objects.filter(query__exact = search)
    if previous is None or previous.__len__() == 0:
        srch = Search()
        srch.query = search
        srch.numResults = list_result['linkList'].__len__()
        srch.save()
        saveL = True

    listLinks = list()
    for result in list_result['linkList']:
        i = 0
        lnk = Link()
        lnk.url = result['url']
        lnk.title = result['title']
        lnk.descr = result['snippet']
        lnk.rank = result['rank']
        lnk.saved = result['saved']
        if filtering is False or lnk.save is False:
            listLinks.append((lnk, result['source']))
        if saveL is True:
            lnkres = SearchResult()
            lnkres.url = lnk.url
            lnkres.snippet = lnk.descr
            lnkres.searchID = srch
            lnkres.rank = lnk.rank
            lnkres.title = lnk.title
            lnkres.value = result['value']
            lnkres.saved = result['saved']
            lnkres.save()

    clickedLinksList = list()
    for result in list_result['clicked']:
        lnk = Link()
        lnk.url = result['url']
        lnk.title = result['title']
        lnk.descr = result['snippet']
        lnk.query = search
        lnk.rank = 1

        clickedLinksList.append(lnk)

    savedLinksList = list()
    for result in list_result['saved']:
        lnk = Link()
        lnk.url = result['url']
        lnk.title = result['title']
        lnk.descr = result['snippet']
        lnk.query = result['query']
        lnk.rank = result['rank']


        savedLinksList.append(lnk)

    context = {'searchid' : -1, 'serverName' : request.META['SERVER_NAME'], 'serverPort' : request.META['SERVER_PORT'], 'query2': search, 'query': urllib.quote(list_result['query'].encode("UTF-8")), 'linkList': listLinks, 'clickedList': clickedLinksList, 'savedList': savedLinksList}
    return render(request, 'search/results.html', context)

def doDiversity(request):
    if len(request.GET.keys()) == 0:
        return HttpResponse(status=404)
    if request.GET.get('search') is None or request.GET.get('filter') is None:
        return HttpResponse(status=404)



    srch = request.GET['search'].encode("UTF-8")
    query = urllib.quote(srch)
    filtering = False
    if request.GET['filter'] is None:
        filtering = False
    else:
        filtering = (request.GET['filter'] == 'True')
    ws = Webservice()

    filteredSearchers = []
    rankers = Ranker.objects.all()
    for r in rankers:
        filter = request.GET.get(r.name)
        if filter is not None:
            if filter != "True":
                filteredSearchers.append(r.rankerID)

   # if filtering is True:
   #     url = url + "True"
   # else:
   #     url = url + "False"

    #Recuperamos los resultados


    url = 'http://localhost:10000/filter/save?query='+query+'&clientIP='+request.META['REMOTE_ADDR']+'&filter=False'
    list_result = ws.call_ws(url, request.META['HTTP_USER_AGENT'])

    search = Search()
    search.query = query
    search.numResults = list_result.__len__()
    search.save()

    results = []
    for res in list_result:
        sr = SearchResult()
        sr.searchID = search
        sr.rank = res['rank']
        sr.snippet = res['snippet']
        sr.title = res['title']
        sr.value = res['value']
        sr.url = res['url']
        sr.saved = res['saved']
        sr.save()
        for source in res['source']:
            ranker = Ranker.objects.filter(rankerID__exact = source).first()
            src = Sources(ranker = ranker, result = sr, rank = 1)
            src.save()
        results.append(sr)
    matrix = [[0 for x in range(list_result.__len__())] for y in range(list_result.__len__())]
    url = 'http://localhost:10000/diversity/?query='+query+'&clientIP='+request.META['REMOTE_ADDR']+'&filter=False'
    list_matrix = ws.call_ws(url, request.META['HTTP_USER_AGENT'])


    for dist in list_matrix['matrix']:
        d = Distances()
        d.firstDoc = results[dist['rank1'] - 1]
        d.secondDoc = results[dist['rank2'] - 1]
        d.distance = dist['distance']
        d.save()
        matrix[dist['rank1'] - 1][dist['rank2'] - 1] = d.distance
        matrix[dist['rank2'] - 1][dist['rank1'] - 1] = d.distance

    ranking = Diversity.diversityRanking(matrix, results, 0.5)


    listLinks = []
    for i in range(list_result.__len__()):
        result = list_result[ranking[i]-1]
        lnk = Link()
        lnk.url = result['url']
        lnk.title = result['title']
        lnk.descr = result['snippet']
        lnk.query = search
        lnk.rank = result['rank']
        lnk.saved = result['saved']

        introduce = True
        if lnk.saved is True and filtering is True:
            introduce = False

        sourceslist=[]
        numCoinc = 0
        for source in result['source']:
            if filteredSearchers.__contains__(source):
                numCoinc += 1
        if numCoinc == result['source'].__len__():
            introduce = False

        if introduce is True:
            listLinks.append((lnk, result['source']))


    context = {'searchid': search.searchID ,'serverName' : request.META['SERVER_NAME'], 'serverPort' : request.META['SERVER_PORT'],'query2': srch, 'query': query, 'linkList': listLinks}
    return render(request, 'search/searched.html', context)

####################EVALUATION################
def evaluationIndex(request):
    return render(request, 'evaluation/evalindex.html')

def evaluationSearch(request):
    if request.GET['search'] is None:
        return HttpResponse(status=404)

    search = request.GET['search']
    #search_type: Web, Image, News, Video
    search = urllib.quote(search.encode("UTF-8"))
    # create credential for authentication
    ws = Webservice()
    url = 'http://localhost:10000/evaluation/search?query='+search+'&clientIP='+request.META['REMOTE_ADDR']
    list_result = ws.call_ws(url , request.META['HTTP_USER_AGENT'])
    listLinks = list()
    i = 1
    for result in list_result['search']:
        lnk = Link()
        lnk.url = result['url']
        lnk.title = result['title']
        lnk.descr = result['snippet']
        lnk.query = search
        lnk.rank = result['rank']
        lnk.save = False
        listLinks.append(lnk)

    context = {'linkList': listLinks, 'serverName': request.META['SERVER_NAME'], 'serverPort': request.META['SERVER_PORT'], 'query2': request.GET['search'], 'query': urllib.quote(request.GET['search'].encode("UTF-8"))}
    return render(request, 'evaluation/evalresults.html', context)

def evaluateClicks(request):
    ws = Webservice()
    url = 'http://localhost:10000/evaluation/evaluate/clicks'
    list_result = ws.call_ws(url, request.META['HTTP_USER_AGENT'])

    labels = []
    sizes = []
    for elem in  list_result:
        labels.append(elem['name'])
        sizes.append(elem['evaluation'])

    fig = Figure(facecolor='white')

    ax = fig.add_subplot(111, aspect='equal')
    ax.pie(sizes,
            labels=labels,
            autopct='%1.1f%%'
            )
    ax.set_title('ZaexSearch Evaluation - Clicks')
    canvas=FigureCanvas(fig)
    response=HttpResponse(content_type="image/png")
    canvas.print_png(response)
    return response

def evaluateQueries(request):
    ws = Webservice()
    url = 'http://localhost:10000/evaluation/evaluate/queries'
    list_result = ws.call_ws(url, request.META['HTTP_USER_AGENT'])

    labels = []
    sizes = []
    for elem in  list_result:
        labels.append(elem['name'])
        sizes.append(elem['evaluation'])

    fig = Figure(facecolor='white')

    ax = fig.add_subplot(111, aspect='equal')
    ax.pie(sizes,
            labels=labels,
            autopct='%1.1f%%'
            )
    ax.set_title('ZaexSearch Evaluation - Queries')
    canvas=FigureCanvas(fig)
    response=HttpResponse(content_type="image/png")
    canvas.print_png(response)
    return response

def evaluatePATK(request):
    if request.GET.get('k') is None:
        return HttpResponse(status=404)
    ws = Webservice()
    url = 'http://localhost:10000/evaluation/evaluate/patk?k=' + request.GET['k']
    list_result = ws.call_ws(url, request.META['HTTP_USER_AGENT'])


    data = [res['evaluation'] for res in list_result]
    names = [res['name'] for res in list_result]

    cols = ['red','orange','yellow','green','blue','purple','indigo']*10
    cols = cols[0:len(data)]
    fig = Figure(facecolor = 'white')
    ax = fig.add_subplot(1,1,1)
    ind = np.arange(data.__len__())
    ax.bar(ind, data, color=cols)

    ax.set_xticks(ind + 0.4)
    ax.set_xticklabels(names)
    ax.set_yticklabels([])
    ax.set_title('Precission At ' + request.GET['k'])
    #chart = plt.bar(np.arange(3), data, 0.35)
    canvas = FigureCanvas(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response)
    return response

def evaluateRATK(request):
    if request.GET.get('k') is None:
        return HttpResponse(status=404)
    ws = Webservice()
    url = 'http://localhost:10000/evaluation/evaluate/ratk?k=' + request.GET['k']
    list_result = ws.call_ws(url, request.META['HTTP_USER_AGENT'])


    data = [res['evaluation'] for res in list_result]
    names = [res['name'] for res in list_result]

    cols = ['red','orange','yellow','green','blue','purple','indigo']*10
    cols = cols[0:len(data)]
    fig = Figure(facecolor = 'white')
    ax = fig.add_subplot(1,1,1)
    ind = np.arange(data.__len__())
    ax.bar(ind, data, color=cols)

    ax.set_xticks(ind + 0.4)
    ax.set_xticklabels(names)
    ax.set_yticklabels([])
    ax.set_title('Recall At ' + request.GET['k'])
    #chart = plt.bar(np.arange(3), data, 0.35)
    canvas = FigureCanvas(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response)
    return response

def evaluateNDCGATK(request):
    if request.GET.get('k') is None:
        return HttpResponse(status=404)
    ws = Webservice()
    url = 'http://localhost:10000/evaluation/evaluate/ndcg?k=' + request.GET['k']
    list_result = ws.call_ws(url, request.META['HTTP_USER_AGENT'])


    data = [res['evaluation'] for res in list_result]
    names = [res['name'] for res in list_result]

    cols = ['red','orange','yellow','green','blue','purple','indigo']*10
    cols = cols[0:len(data)]
    fig = Figure(facecolor = 'white')
    ax = fig.add_subplot(1,1,1)
    ind = np.arange(data.__len__())
    ax.bar(ind, data, color=cols)

    ax.set_xticks(ind + 0.4)
    ax.set_xticklabels(names)
    ax.set_yticklabels([])
    ax.set_title('nDCG At ' + request.GET['k'])
    #chart = plt.bar(np.arange(3), data, 0.35)
    canvas = FigureCanvas(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response)
    return response

def evaluateMRR(request):

    ws = Webservice()
    url = 'http://localhost:10000/evaluation/evaluate/mrr'
    list_result = ws.call_ws(url, request.META['HTTP_USER_AGENT'])


    data = [res['evaluation'] for res in list_result]
    names = [res['name'] for res in list_result]

    cols = ['red','orange','yellow','green','blue','purple','indigo']*10
    cols = cols[0:len(data)]
    fig = Figure(facecolor = 'white')
    ax = fig.add_subplot(1,1,1)
    ind = np.arange(data.__len__())
    ax.bar(ind, data, color=cols)

    ax.set_xticks(ind + 0.4)
    ax.set_xticklabels(names)
    ax.set_yticklabels([])
    ax.set_title('MRR')
    #chart = plt.bar(np.arange(3), data, 0.35)
    canvas = FigureCanvas(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response)
    return response

def evaluateMAP(request):

    ws = Webservice()
    url = 'http://localhost:10000/evaluation/evaluate/map'
    list_result = ws.call_ws(url, request.META['HTTP_USER_AGENT'])


    data = [res['evaluation'] for res in list_result]
    names = [res['name'] for res in list_result]

    cols = ['red','orange','yellow','green','blue','purple','indigo']*10
    cols = cols[0:len(data)]
    fig = Figure(facecolor = 'white')
    ax = fig.add_subplot(1,1,1)
    ind = np.arange(data.__len__())
    ax.bar(ind, data, color=cols)

    ax.set_xticks(ind + 0.4)
    ax.set_xticklabels(names)
    ax.set_yticklabels([])
    ax.set_title('MAP')
    #chart = plt.bar(np.arange(3), data, 0.35)
    canvas = FigureCanvas(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response)
    return response

def evaluateILD(request):

    ws = Webservice()
    url = 'http://localhost:10000/evaluation/evaluate/ild'
    list_result = ws.call_ws(url, request.META['HTTP_USER_AGENT'])


    data = [res['evaluation'] for res in list_result]
    names = [res['name'] for res in list_result]

    cols = ['red','orange','yellow','green','blue','purple','indigo']*10
    cols = cols[0:len(data)]
    fig = Figure(facecolor = 'white')
    ax = fig.add_subplot(1,1,1)
    ind = np.arange(data.__len__())
    ax.bar(ind, data, color=cols)

    ax.set_xticks(ind + 0.4)
    ax.set_xticklabels(names)
    ax.set_yticklabels([])
    ax.set_title('ILD')
    #chart = plt.bar(np.arange(3), data, 0.35)
    canvas = FigureCanvas(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response)
    return response

def evalclicked(request):
    if len(request.GET.keys()) > 0:
		if request.GET['query'] is None or request.GET['rank'] is None:
			return HttpResponse(status=404)
    else:
        return HttpResponse(status=404)

    ws = Webservice()
    query = urllib.quote(request.GET['query'].encode("UTF-8"))
    url = 'http://localhost:10000/evaluation/click?query='+query+'&clientIP='+request.META['REMOTE_ADDR']+'&rank='+request.GET['rank']
    list_result = ws.call_ws(url, request.META['HTTP_USER_AGENT'])
    listLinks = list()
    for result in list_result:
		lnk = Link()
		lnk.url = result['url']
		lnk.title = result['title']
		lnk.descr = result['snippet']
		lnk.rank = 1

		listLinks.append(lnk)

    context = {'linkList': listLinks}
    return render(request, 'evaluation/evalclicked.html', context)

def evalDiversityIndex(request):
    return render(request, 'evaluation/evalindexdiversity.html')

def evaldoDiversity(request):
    if len(request.GET.keys()) == 0:
        return HttpResponse(status=404)
    if request.GET['search'] is None:
        return HttpResponse(status=404)

    search = request.GET['search'].encode("UTF-8")
    ws = Webservice()
    list_result = ws.call_ws_search(search, False, request.META['REMOTE_ADDR'], request.META['HTTP_USER_AGENT'])

    #Obtaining the results
    url = 'http://localhost:10000/search?query='+urllib.quote(search)+'&clientIP='+request.META['REMOTE_ADDR']+'&filter=False'

    srch = Search()
    srch.query = search
    srch.numResults = list_result['search'].__len__()
    srch.save()
    saveL = True

    linkList = list()
    results = list()
    i = 1
    for result in list_result['search']:
        lnk = Link()
        lnk.url = result['url']
        lnk.title = result['title']
        lnk.descr = result['snippet']
        lnk.query = search
        lnk.rank = result['rank']
        linkList.append(lnk)

        lnkres = SearchResult()
        lnkres.url = lnk.url
        lnkres.snippet = lnk.descr
        lnkres.searchID = srch
        lnkres.rank = lnk.rank
        lnkres.title = lnk.title
        lnkres.value = result['value']
        lnkres.save()
        results.append(lnkres)

    matrix = [[0 for x in range(results.__len__())] for y in range(results.__len__())]
    url = 'http://localhost:10000/diversity/?query='+urllib.quote(search)+'&clientIP='+request.META['REMOTE_ADDR']+'&filter=False'
    list_matrix = ws.call_ws(url, request.META['HTTP_USER_AGENT'])


    for dist in list_matrix['matrix']:
        d = Distances()
        leng = results.__len__()
        rank1 = dist['rank1']
        rank2 = dist['rank2']
        d.firstDoc = results[dist['rank1'] - 1]
        d.secondDoc = results[dist['rank2'] - 1]
        d.distance = dist['distance']
        d.save()
        matrix[dist['rank1'] - 1][dist['rank2'] - 1] = d.distance
        matrix[dist['rank2'] - 1][dist['rank1'] - 1] = d.distance

    ILDMatrix = [[0 for x in range(sizeILD)] for y in range(sizeILD)]
    for i in range(sizeILD):
        for j in range(sizeILD):
            ILDMatrix[i][j] = matrix[i][j]
    #Obtaining the ILD result for both lists (it will be the same in first instance
    ild = Diversity.calculateILD(ILDMatrix)

    context = {'serverName' : request.META['SERVER_NAME'], 'serverPort' : request.META['SERVER_PORT'],'query2': search,  'query': urllib.quote(search), 'linkList': linkList, 'diversityList': linkList, 'ildRankSym' : ild, 'ildDiversity' : ild }
    return render(request, 'evaluation/evaldiversity.html', context)


def evalReport(request):
    url = 'http://localhost:10000/evaluation/evaluate/report'
    ws = Webservice()
    list_result = ws.call_ws(url, request.META['HTTP_USER_AGENT'])

    clicksNames = []
    clicksEvals = []
    for result in list_result['clicks']:
        clicksNames.append(result)
        clicksEvals.append(list_result['clicks'][result])

    queriesNames = []
    queriesEvals = []
    for result in list_result['queries']:
        queriesNames.append(result)
        queriesEvals.append(list_result['queries'][result])

    PAt5Names = []
    PAt5Evals = []
    for key in list_result['PAt5']:
        PAt5Names.append(key)
        PAt5Evals.append(list_result['PAt5'][key])

    PAt10Names = []
    PAt10Evals = []
    for key in list_result['PAt10']:
        PAt10Names.append(key)
        PAt10Evals.append(list_result['PAt10'][key])

    RAt5Names = []
    RAt5Evals = []
    for key in list_result['RAt5']:
        RAt5Names.append(key)
        RAt5Evals.append(list_result['RAt5'][key])

    RAt10Names = []
    RAt10Evals = []
    for key in list_result['RAt10']:
        RAt10Names.append(key)
        RAt10Evals.append(list_result['RAt10'][key])

    NDCGAt5Names = []
    NDCGAt5Evals = []
    for key in list_result['nDCGAt5']:
        NDCGAt5Names.append(key)
        NDCGAt5Evals.append(list_result['nDCGAt5'][key])

    NDCGAt10Names = []
    NDCGAt10Evals = []
    for key in list_result['nDCGAt10']:
        NDCGAt10Names.append(key)
        NDCGAt10Evals.append(list_result['nDCGAt10'][key])

    MAPNames = []
    MAPEvals = []
    for key in list_result['MAP']:
        MAPNames.append(key)
        MAPEvals.append(list_result['MAP'][key])

    MRRNames = []
    MRREvals = []
    for key in list_result['MRR']:
        MRRNames.append(key)
        MRREvals.append(list_result['MRR'][key])

    ILDNames = []
    ILDEvals = []
    for key in list_result['ILD']:
        ILDNames.append(key)
        ILDEvals.append(list_result['ILD'][key])

    context = {'clicksNames' : clicksNames, 'clicksEvals' : clicksEvals, 'queriesNames':queriesNames, 'queriesEvals':queriesEvals,
        'PAt5Names':PAt5Names, 'PAt5Evals':PAt5Evals, 'PAt10Names':PAt10Names, 'PAt10Evals': PAt10Evals, 'RAt5Names':RAt5Names,
        'RAt5Evals':RAt5Evals, 'RAt10Names' : RAt10Names, 'RAt10Evals': RAt10Evals, 'NDCGAt5Names': NDCGAt5Names, 'NDCGAt5Evals':NDCGAt5Evals,
        'NDCGAt10Names': NDCGAt10Names, 'NDCGAt10Evals':NDCGAt10Evals, 'MRRNames':MRRNames,'MRREvals':MRREvals, 'MAPNames':MAPNames, 'MAPEvals':MAPEvals,
        'ILDNames':ILDNames, 'ILDEvals':ILDEvals}
    return render(request, 'evaluation/evalReport.html', context)

def evalChangeDiversity(request):
    if len(request.GET.keys()) == 0:
        return HttpResponse(status=404)
    if request.GET['search'] is None:
        return HttpResponse(status=404)

    search = request.GET['search'].encode("UTF-8")

    srch = Search.objects.filter(query__exact = search).order_by('searchID').last()
    results = SearchResult.objects.filter(searchID__exact = srch).order_by('rank')
    matrix = [[0 for x in range(results.__len__())] for y in range(results.__len__())]

    firstRes = results.first().resultID
    lastRes = results.last().resultID
    distQ = Distances.objects.filter(firstDoc__resultID__gte = firstRes, firstDoc__resultID__lte = lastRes).order_by('firstDoc', 'secondDoc')
    if distQ is None or distQ.__len__() == 0:
        return HttpResponse(status=404)

    for dist in distQ:
            matrix[dist.firstDoc.resultID-firstRes][dist.secondDoc.resultID-firstRes] = dist.distance
            matrix[dist.secondDoc.resultID-firstRes][dist.firstDoc.resultID-firstRes] = dist.distance

    if request.GET['lambda'] is None:
        lamb = 0.0
    else:
        lamb = float(request.GET['lambda'])
    ranking = Diversity.diversityRanking(matrix, results, lamb)

    ILDMatrix = [[0 for x in range(sizeILD)] for y in range(sizeILD)]

    for i in range(sizeILD):
        for j in range(sizeILD):
            ILDMatrix[i][j] = matrix[ranking[i]-1][ranking[j]-1]

    ild = Diversity.calculateILD(ILDMatrix)

    lnkList = []
    for i in range(results.__len__()):
        result = results[ranking[i]-1]
        lnk = Link()
        lnk.url = result.url
        lnk.title = result.title
        lnk.descr = result.snippet
        lnk.query = search
        lnk.rank = result.rank
        lnk.save = False

        lnkList.append(lnk)

    context = {'serverName' : request.META['SERVER_NAME'], 'serverPort' : request.META['SERVER_PORT'], 'query2': search, 'query': urllib.quote(request.GET['search'].encode("UTF-8")), 'diversityList': lnkList, 'ildDiversity' : ild }
    return render(request, 'evaluation/evalchangediversity.html', context)

def evalRankSymIndex(request):
    return render(request, 'evaluation/evalindexranksym.html')

def evaldoRanksym(request):
    if len(request.GET.keys()) == 0:
        return HttpResponse(status=404)
    if request.GET['search'] is None:
        return HttpResponse(status=404)

    search = request.GET['search'].encode("UTF-8")

    ws = Webservice()
    list_result = ws.call_ws_search(search, False, request.META['REMOTE_ADDR'], request.META['HTTP_USER_AGENT'])

    #Obtaining the resultshttp://localhost:10000/evaluation/evaluate/ranksym?query=space&clientIP=localhost&filter=False
    url = 'http://localhost:10000/sources?query='+urllib.quote(search)+'&clientIP='+request.META['REMOTE_ADDR']+'&filter=False'

    saveL = False
    if(list_result['new'] is True):
        saveL = True



    srch = Search()
    srch.query = search
    srch.numResults = list_result['search'].__len__()
    srch.save()

    listLinks = list()
    i = 1
    for result in list_result['search']:
        lnk = Link()
        lnk.url = result['url']
        lnk.title = result['title']
        lnk.descr = result['snippet']
        lnk.query = search
        lnk.rank = result['rank']
        lnk.saved = result['saved']
        listLinks.append((lnk, result['source']))

        lnkres = SearchResult()
        lnkres.url = lnk.url
        lnkres.snippet = lnk.descr
        lnkres.searchID = srch
        lnkres.rank = lnk.rank
        lnkres.title = lnk.title
        lnkres.value = result['value']
        lnkres.save()

    #Obtaining the diversity matrix
    srch = Search.objects.filter(query__exact = search).last()
    results = SearchResult.objects.filter(searchID__exact = srch).order_by('rank')

    firstRes = results.first().resultID
    lastRes = results.last().resultID

    cached = False
    sources = Sources.objects.filter(result__resultID__gte = firstRes, result__resultID__lte = lastRes)
    list_result = ws.call_ws(url, request.META['HTTP_USER_AGENT'])

    for dist in list_result['sources']:
        i = 0
        for el in dist['sources']:
            ranker = Ranker.objects.filter(rankerID__exact = el).first()
            src = Sources(ranker = ranker, result = results[dist['rank']-1], rank = dist['ranks'][i])
            src.save()
            i = i+1

    context = {'serverName' : request.META['SERVER_NAME'], 'serverPort' : request.META['SERVER_PORT'], 'query2': search, 'query': urllib.quote(request.GET['search'].encode("UTF-8")), 'linkList': listLinks, 'numRankers': Ranker.objects.all().__len__()}
    return render(request, 'evaluation/evalranksym.html', context)

def evalChangeRanksym(request):
    if len(request.GET.keys()) == 0:
        return HttpResponse(status=404)
    if request.GET.get('search') is None:
        return HttpResponse(status=404)

    search = request.GET['search'].encode("UTF-8")

    values = {}

    rankers = Ranker.objects.all()
    for ranker in rankers:
        if(request.GET.get(ranker.name) is None):
            return HttpResponse(status=404)
        values[ranker.name]=float(request.GET.get(ranker.name))

    srch = Search.objects.filter(query__exact = search).last()
    results = SearchResult.objects.filter(searchID__exact = srch).order_by('rank')
    sources = Sources.objects.filter(result__in = results).order_by('ranker', 'rank')
    resultLists = {}
    for i in range(rankers.__len__()):
                ls = []
                rankers = Ranker.objects.filter(rankerID__exact = (i+1))
                name = rankers.first().name
                for source in sources:
                    if source.ranker.rankerID == (i+1):
                        result = SearchResult.objects.filter(resultID__exact = source.result.resultID).first()
                        result.searchID = srch
                        result.title = result.title
                        result.url = result.url
                        result.snippet = result.snippet
                        result.rank = source.rank
                        ls.append(result)
                        resultLists[name] = ls

    metasearcher = RankSymMetasearcher()
    results = metasearcher.doMetaSearch(resultLists, values)
    linkList = []
    for srchRes in results:
        sourceList = []
        sources = Sources.objects.filter(result__exact=srchRes)
        for s in sources:
            sourceList.append(s.ranker.rankerID)
        linkList.append((srchRes, sourceList))
    context = {'serverName' : request.META['SERVER_NAME'], 'serverPort' : request.META['SERVER_PORT'], 'query2': search, 'query': urllib.quote(request.GET['search'].encode("UTF-8")), 'linkList': linkList}
    return render(request, 'evaluation/evalchangeranksym.html', context)
