# -*- encoding: utf-8 -*-
# -*- coding: utf-8 -*-
## @package TFGSearch.views
# WebService API for search

#Bibliotecas de DjangoRestFramework
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
#Modelos y serializadores para el webService
from TFGSearch.Metasearch.docSource import DocSource
from TFGSearch.serializers import *
#Bibliotecas para realizar la metabusqueda
from TFGSearch.Metasearch.rankSimMetasearcher import *
from TFGSearch.Metasearch.googleSearcher import *
from TFGSearch.Metasearch.bingSearcher import *
from TFGSearch.Metasearch.carrot2Searcher import *
from TFGSearch.Metasearch.farooSearcher import *
from TFGSearch.SessionDetection.searchPatternDetector import *
from TFGSearch.Diversity.diversityMatrix import *
from TFGSearch.Indexing.indexer import *

import thread


## Retrieves a list of documents from several search engines
# @param request Client's request. Includes three arguments: query, that corresponds with the query, clientIP, which represents clients IP direction
#       and filter, which indicates if saved results are or not excluded from the ranking
# @returns Error code if a problem occurs or a JSON ranking with search results, clicked links and saved links
@api_view(['GET'])
def link_list(request):
    #i = 0
    #STEP 1: Check that the query, the client IP and the filter are not null
    if request.GET.get('query') is None or request.GET.get('query') == '':
        return Response(status=status.HTTP_404_NOT_FOUND)
    elif request.GET.get('clientIP') is None or request.GET['clientIP'] == '':
        return Response(status=status.HTTP_404_NOT_FOUND)
    elif request.GET.get('filter') is None or ((request.GET['filter'] == 'True') == False and (request.GET['filter'] == 'False') == False):
        return Response(status=status.HTTP_400_BAD_REQUEST)
    time0 = timezone.now()
    busqueda = request.GET['query'].encode("UTF-8")
    filtering = (request.GET['filter'] == 'True')
    #STEP 2: Check if the client exists
    cli = Client().get_or_create(request.GET['clientIP'], request.META['HTTP_USER_AGENT'])
    if cli is None:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    #STEP 3: Check the session to use
    sesList = Session().get_active(cli)
    if sesList is None:
        ses = None
    elif sesList.__len__() > 1:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    elif sesList.__len__() == 0:
        ses = None
    else:
        ses = sesList.first()

    det = SearchPatternDetector()
    ses2 = det.detectSession(cli, busqueda, ses)
    rebuild = False
    if ses is None:
        ses2.save()
        ses = ses2
    elif ses == ses2:
        ses.save()
    else:
        rebuild = True
        ses.active = False
        ses.save()
        ses = ses2
        ses2.save()

    #STEP 4: Look for the metasession to use

    metaSes = MetaSession.get_or_create(cli)

    #PASO 5: Create an entry for the search in the database
    search = Search().create(ses, busqueda)

    #PASO 6: Do the metasearch
    meta = RankSimMetasearcher()

    # while(meta.searcherList.__len__() is not 0):
    #     for searcher in meta.searcherList:
    #         meta.searcherList.remove(searcher)

    meta.addSearcher(GoogleSearcher())
    meta.addSearcher(BingSearcher())
    meta.addSearcher(Carrot2Searcher())
    meta.addSearcher(FarooSearcher())

    dataLists = meta.doSearch(busqueda, search)
    resultLinks = meta.doMetaSearch(dataLists, search)


    if resultLinks is not None:
        search.numResults = resultLinks.__len__()
        search.save()
    else:
        resultLinks = list()

    data = list()
    thread.start_new_thread(Indexer.createIndexFromSnippets, (resultLinks, ses, rebuild))

    if filtering == True:
        for lnk in resultLinks:
            if not SavedLink.objects.filter(metaSessionID__exact = metaSes).filter(url__exact = lnk.url):
                data.append(lnk)
    else:
        data = resultLinks



    FoundSerializer = LinkSerializer(data, many=True)
    for lnk in FoundSerializer.data:
        if not SavedLink.objects.filter(metaSessionID__exact = metaSes).filter(url__exact = lnk['url']):
            lnk['saved'] = False
        else:
            lnk['saved'] = True
    dataClicked = ClickedLink.objects.filter(sessionID__exact = ses)
    ClickSerializer = ClickedLinkSerializer(dataClicked, many=True)
    dataSaved = SavedLink.objects.filter(metaSessionID__exact = metaSes)
    SavedSerializer = SavedLinkSerializer(dataSaved, many=True)
    time1 = timezone.now()
    dataDef = { 'search' : FoundSerializer.data, 'clicked' : ClickSerializer.data, 'saved' : SavedSerializer.data, 'new' : meta.newSearch, 'time0' : time0, 'time1':time1}
    return Response(dataDef)


## Returns a list of previously clicked links
# @param request Client's request. Includes the following parameters: query (query string), clientIP (client's IP) y rank (clicked document rank)
# @returns Error code if there is a problem, or a JSON list of clicked links if not
@api_view(['GET'])
def clicked_list(request):

    #STEP 1: Check that the query, the client IP and the filter are not null
    if len(request.GET.keys()) > 0:
        if request.GET.get('query') is None or request.GET['query'] == '':
            return Response(status=status.HTTP_400_BAD_REQUEST)
        elif request.GET.get('clientIP') is None or request.GET['clientIP'] == '':
            return Response(status=status.HTTP_400_BAD_REQUEST)
        elif request.GET.get('rank') is None or request.GET['rank'] == '':
            return Response(status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    #STEP 2: Look for the client
    clientes = Client.objects.filter(clientIP__exact = request.GET['clientIP']).filter(userAgent__exact = request.META['HTTP_USER_AGENT'])
    cli = None
    if(not clientes):
        return Response('Not client')
    elif clientes.count() > 1:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        cli = clientes.first() #El cliente es unico


    #STEP 3: Look for the active session
    sesiones = Session.objects.filter(clientID__exact = cli.clientID).filter(active = True)
    ses = None
    if(not sesiones):
        return Response(status=status.HTTP_400_BAD_REQUEST)
    elif sesiones.count() > 1:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        ses = sesiones.first()

    #STEP 4: Obtain the search
    busquedas = Search.objects.filter(query__exact = request.GET['query'])
    if(not busquedas):
        return Response(status=status.HTTP_400_BAD_REQUEST)
    else:
        busqueda = busquedas.last()

    #STEP 5: Obtai the clicked link
    resultList = SearchResult.objects.filter(searchID__exact = busqueda ).filter(rank__exact = request.GET['rank'])
    if(not resultList):
        return Response(status=status.HTTP_400_BAD_REQUEST)
    else:
        res = resultList.first()

    #PASO 6: Create an entry for the clicked link in the database

    clicked = ClickedLink.objects.filter(searchResult__exact = res)
    if(not clicked):
        click = ClickedLink()
        click.sessionID = ses
        click.searchResult = res
        click.url = res.url
        click.snippet = res.snippet
        click.title = res.title
        click.evaluation = False

        click.save()


    #PASO 7: Return the clicked link list

    data = ClickedLink.objects.filter(sessionID__exact = ses)


    #Serialize and send results
    serializer = ClickedLinkSerializer(data, many=True)
    return Response(serializer.data)

#___________________________________________WEBSERVICE METASESSION_________________________________________________#

###
# Saves a document in a metasession
# @param request HTTP Request.Includes the parameters query (query), clientIP (client's IP) and rank (rank of the document to save)
# @returns a list of saved documents
@api_view(['GET'])
def saved_list(request):
    #STEP 1: Check that the query, the client IP and the rank are not null
    if len(request.GET.keys()) > 0:
        if request.GET.get('query') is None or request.GET['query'] == '':
            return Response(status=status.HTTP_400_BAD_REQUEST)
        elif request.GET.get('clientIP') is None or request.GET['clientIP'] == '':
            return Response(status=status.HTTP_400_BAD_REQUEST)
        elif request.GET.get('rank') is None or request.GET['rank'] == '':
            return Response(status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


    #STEP 2: Get the client
    clientes = Client.objects.filter(clientIP__exact = request.GET['clientIP']).filter(userAgent__exact = request.META['HTTP_USER_AGENT'])
    cli = None
    if(not clientes):
        return Response('Not client')
    elif clientes.count() > 1:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        cli = clientes.first() #El cliente es unico


    #PASO 3: Get the session
    sesiones = Session.objects.filter(clientID__exact = cli.clientID).filter(active = True)
    ses = None
    if(not sesiones):
        return Response(status=status.HTTP_400_BAD_REQUEST)
    elif sesiones.count() > 1:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        ses = sesiones.first()


    #STEP 4: Get the metasession
    metaSes = MetaSession.get_or_create(cli)

    #STEP 5: Get the search
    busquedas = Search.objects.filter(query__exact = request.GET['query'])
    if(not busquedas):
        return Response(status=status.HTTP_400_BAD_REQUEST)
    else:
        busqueda = busquedas.last()

    #STEP 6: Get the result to save
    resultList = SearchResult.objects.filter(searchID__exact = busqueda ).filter(rank__exact = request.GET['rank'])
    if(not resultList):
        return Response(status=status.HTTP_400_BAD_REQUEST)
    else:
        res = resultList.first()


    #STEP 7: If the result has not been saved before, save the link
    metaSes.addResult(res, busqueda)


    #STEP 9: Return the saved list
    dataSaved = SavedLink.objects.filter(metaSessionID__exact = metaSes)
    ser = list()
    for lnk in dataSaved :
        ser.append({ "title" : lnk.title, "url" : lnk.url, "snippet" : lnk.snippet, "query" : lnk.query, "rank": lnk.rank})
   # serializer = SavedLinkSerializer(dataSaved, many=True)
    return Response(ser)



###
# Deletes a document of a metasession
# @param request HTTP Request.Includes the parameters url (url of the doc), clientIP (client's IP) and rank (rank of the document to save)
# @returns a list of saved documents
@api_view(['GET'])
def delete_list(request):
    #STEP 1: Check the parameters
    if len(request.GET.keys()) > 0:
        if request.GET.get('query') is None or request.GET.get('query') == '':
            return Response(status=status.HTTP_400_BAD_REQUEST)
        elif request.GET.get('rank') is None or request.GET['rank'] == '':
            return Response(status=status.HTTP_400_BAD_REQUEST)
        elif request.GET.get('clientIP') is None or request.GET.get('clientIP') == '':
            return Response(status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    #PASO 2: Get the client
    clientes = Client.objects.filter(clientIP__exact = request.GET['clientIP']).filter(userAgent__exact = request.META['HTTP_USER_AGENT'])
    cli = None
    if(not clientes):
        return Response('Not client')
    elif clientes.count() > 1:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        cli = clientes.first() #El cliente es unico

    #PASO 4: Get the metasession
    metaSes = MetaSession.get_or_create(cli)

    #PASO 7: Check that the result exists
    metaSes.deleteResult(request.GET.get('query'), request.GET.get('rank'))

    #PASO 9: Return the saved link list
    dataSaved = SavedLink.objects.filter(metaSessionID__exact = metaSes)
    ser = list();
    for lnk in dataSaved :
        ser.append({ "title" : lnk.title, "url" : lnk.url, "snippet" : lnk.snippet, "query" : lnk.query, "rank" : lnk.rank})
   # serializer = SavedLinkSerializer(dataSaved, many=True)
    return Response(ser)


###
# Closes a metasession
# @param request HTTP Request.Includes the parameter clientIP (client's IP)
# @returns an empty response
@api_view(['GET'])
def close_list(request):
    #STEP 1: Check parameters
    if len(request.GET.keys()) > 0:
        if request.GET.get('clientIP') is None or request.GET['clientIP'] == '':
            return Response(status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    #PASO 2: Get the client
    clientes = Client.objects.filter(clientIP__exact = request.GET['clientIP']).filter(userAgent__exact = request.META['HTTP_USER_AGENT'])
    cli = None
    if(not clientes):
        return Response('Not client')
    elif clientes.count() > 1:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        cli = clientes.first() #The client is unique

    #PASO 4: Obtaining the metasession
    metaSesList = MetaSession.objects.filter(clientID__exact = cli).filter(closed__exact = False)
    if metaSesList.__len__() > 0:
        for meta in metaSesList:
            meta.close()
   # serializer = SavedLinkSerializer(dataSaved, many=True)
    return Response("")

###
# Opens a metasession
# @param request HTTP request. Includes clientIP (client's IP) and metaName (name of the saved metasession)
# @returns a list of saved links if the session exists, a message if not
@api_view(['GET'])
def open_list(request):
    retrieveActual = False
    #STEP 1: Check parameters
    if len(request.GET.keys()) > 0:
        if request.GET.get('clientIP') is None or request.GET['clientIP'] == '':
            return Response(status=status.HTTP_400_BAD_REQUEST)
        elif request.GET.get('metaName') is None or request.GET['metaName'] == '':
            retrieveActual = True
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    metaName = request.GET['metaName'].encode('UTF-8')
    #STEP 2: Obtenemos el cliente
    clientes = Client.objects.filter(clientIP__exact = request.GET['clientIP']).filter(userAgent__exact = request.META['HTTP_USER_AGENT'])
    cli = None
    if(not clientes):
        return Response('Not client')
    elif clientes.count() > 1:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        cli = clientes.first() #El cliente es unico

    #PASO 3: Buscamos la actual sesion, y la cerramos

    openMeta = MetaSession.objects.filter(clientID__exact = cli).filter(closed__exact = False)

    metaSes2 = None
    if openMeta is None or openMeta.__len__() == 0:
        metaSes2 = MetaSession()
        metaSes2.clientID = cli
        metaSes2.closed = False
    else:
        metaSes2 = openMeta.first()

    metaSes = metaSes2
    if retrieveActual is False:
        metaSes = MetaSession.open(metaName, cli)
        if(metaSes is None):
            metaSes = metaSes2

    if openMeta.__len__() > 0:
            for meta in openMeta:
                meta.close()

    metaSes.closed = False
    metaSes.save()
    dataSaved = SavedLink.objects.filter(metaSessionID__exact = metaSes)
    ser = list();
    for lnk in dataSaved :
        ser.append({ "title" : lnk.title, "url" : lnk.url, "snippet" : lnk.snippet, "query" : lnk.query, "rank" : lnk.rank})
    return Response(ser)


###
# Opens a metasession
# @param request HTTP request. Includes clientIP (client's IP) and metaName (name of the saved metasession)
# @returns a list of saved links if the session exists, a message if not
@api_view(['GET'])
def isAvailableName(request):

    #PASO 1: Obtenemos del request los campos IP, query, rank y userAgent
    if len(request.GET.keys()) > 0:
        if request.GET.get('clientIP') is None or request.GET['clientIP'] == '':
            return Response(status=status.HTTP_400_BAD_REQUEST)
        elif request.GET.get('metaName') is None or request.GET['metaName'] == '':
            return Response({'available': False})
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    metaName = request.GET['metaName'].encode('UTF-8')
    #PASO 2: Obtenemos el cliente
    clientes = Client.objects.filter(clientIP__exact = request.GET['clientIP']).filter(userAgent__exact = request.META['HTTP_USER_AGENT'])
    cli = None
    if(not clientes):
        return Response('Not client')
    elif clientes.count() > 1:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        cli = clientes.first() #El cliente es unico

    #PASO 3: Buscamos la actual sesion, y la cerramos
    openMeta = MetaSession.get_or_create(cli)
    if openMeta.name == metaName:
        return Response({'available' : True})



    metaSes = MetaSession.objects.filter(clientID__exact = cli).filter(name__exact = metaName)
    if(not metaSes):
        return Response({'available' : True})

    return Response({'available' : False})


###
# Saves a metasession and closes it
# @param request HTTP request. Includes clientIP (client's IP) and metaName (name of the saved metasession)
# @returns a list of saved links if the session exists, a message if not
@api_view(['GET'])
def saveAndCloseMeta(request):
    #STEP 1: Check parameters
    if len(request.GET.keys()) > 0:
        if request.GET.get('clientIP') is None or request.GET['clientIP'] == '':
            return Response(status=status.HTTP_400_BAD_REQUEST)
        elif request.GET.get('metaName') is None or request.GET['metaName'] == '':
            return Response(status = status.HTTP_400_BAD_REQUEST)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    metaName = request.GET['metaName'].encode('UTF-8')
    #STEP 2: Get the client
    clientes = Client.objects.filter(clientIP__exact = request.GET['clientIP']).filter(userAgent__exact = request.META['HTTP_USER_AGENT'])
    cli = None
    if(not clientes):
        return Response('Not client')
    elif clientes.count() > 1:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        cli = clientes.first() #El cliente es unico

    #PASO 3: Get the current metasession
    openMeta = MetaSession.objects.filter(clientID__exact = cli).filter(closed__exact = False)

    if not openMeta:
        meta = MetaSession()
        meta.name=""
        meta.clientID=cli
        meta.save()

    sameNameMeta = MetaSession.objects.filter(clientID__exact = cli).filter(name__exact = metaName)

    for meta in sameNameMeta:
        meta.saveSession("")

    for meta in openMeta:
        meta.saveSession(metaName)
        meta.close()


    return Response("")


###
# Retrieves the results of a previous search, filtered
# @param request Client's request. Includes three arguments: query, that corresponds with the query, clientIP, which represents clients IP direction
#       and filter, which indicates if saved results are or not excluded from the ranking# @returns a list of saved links if the session exists, a message if not
# @return a list of searchResults if OK, error code if not
@api_view(['GET'])
def retrieve_list(request):
     #PASO 1: Comprobar que no es nula la busqueda, la IP del cliente o el agente
    if len(request.GET.keys()) > 0:
        if request.GET.get('query') is None or request.GET['query'] == '':
            return Response(status=status.HTTP_400_BAD_REQUEST)
        elif request.GET.get('clientIP') is None or request.GET['clientIP'] == '':
            return Response(status=status.HTTP_400_BAD_REQUEST)
        elif request.GET.get('filter') is None or ((request.GET['filter'] == 'True') == False and (request.GET['filter'] == 'False') == False):
            return Response(status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    query = request.GET['query'].encode('UTF-8')
    filtering = (request.GET['filter'] == 'True')
    #PASO 2:Buscamos el cliente
    clientes = Client.objects.filter(clientIP__exact = request.GET['clientIP']).filter(userAgent__exact = request.META['HTTP_USER_AGENT'])
    cli = None
    if(not clientes):
        return Response('Not client')
    elif clientes.count() > 1:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        cli = clientes.first() #El cliente es unico

    metaSes = MetaSession.get_or_create(cli)


    #PASO 3: Buscamos la sesion activa
    sesiones = Session.objects.filter(clientID__exact = cli.clientID).filter(active = True)
    ses = None
    if(not sesiones):
        return Response(status=status.HTTP_400_BAD_REQUEST)
    elif sesiones.count() > 1:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        ses = sesiones.first()


    rankers = Ranker.objects.all()
    lsRankersToFilter = []
    for ranker in rankers:
        if request.GET.get(ranker.name) is not None and request.GET[ranker.name] == 'False':
            lsRankersToFilter.append(ranker)

    #PASO 4: Obtenemos la busqueda
    busquedas = Search.objects.filter(query__exact = query)
    if(not busquedas):
        return Response(status=status.HTTP_400_BAD_REQUEST)
    else:
        busqueda = busquedas.last()

    #PASO 5: Obtenemos el resultado de la busqueda
    resultList = SearchResult.objects.filter(searchID__exact = busqueda ).order_by('rank')

    #PASO 6: Filtramos los resultados guardados
    data = list()
    if filtering == True:
        for lnk in resultList:
            if not SavedLink.objects.filter(metaSessionID__exact = metaSes).filter(url__exact = lnk.url):
                data.append(lnk)
    else:
        data = resultList

    #PASO 7: Filtramos los resultados por buscadores
    defData = list()
    if lsRankersToFilter.__len__() == 0:
        defData = data
    else:
        for lnk in data:
            sources = Sources.objects.filter(result__exact = lnk)
            numCoinc = 0
            for source in sources:
                if lsRankersToFilter.__contains__(source.ranker):
                    numCoinc += 1
            if not(numCoinc == sources.__len__()):
                defData.append(lnk)
    #Serializamos y enviamos los resultados
    serializer = LinkSerializer(defData, many=True)
    for lnk in serializer.data:
        if not SavedLink.objects.filter(metaSessionID__exact = metaSes).filter(url__exact = lnk['url']):
            lnk['saved'] = False
        else:
            lnk['saved'] = True

    return Response(serializer.data)


#____RELEVANCE FEEDBACK

###
# Adds a word to a query and searches results for the new query
# @param request Client's request. Includes three arguments: query, that corresponds with the query, clientIP, which represents clients IP direction
#       and filter, which indicates if saved results are or not excluded from the ranking# @returns a list of saved links if the session exists, a message if not
# @return a list of searchResults if OK, error code if not
@api_view(['GET'])
def do_relevance_feedback(request):

    numWords = 1
     #PASO 1: Comprobar que no es nula la busqueda, la IP del cliente o el agente
    if len(request.GET.keys()) > 0:
        if request.GET.get('query') is None or request.GET['query'] == '':
            return Response(status=status.HTTP_400_BAD_REQUEST)
        elif request.GET.get('clientIP') is None or request.GET['clientIP'] == '':
            return Response(status=status.HTTP_400_BAD_REQUEST)
        elif request.GET.get('filter') is None or ((request.GET['filter'] == 'True') == False and (request.GET['filter'] == 'False') == False):
            return Response(status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    query = request.GET['query'].encode('UTF-8')
    filtering = (request.GET['filter'] == 'True')
    #PASO 2:Buscamos el cliente
    clientes = Client.objects.filter(clientIP__exact = request.GET['clientIP']).filter(userAgent__exact = request.META['HTTP_USER_AGENT'])
    cli = None
    if(not clientes):
        return Response('Not client')
    elif clientes.count() > 1:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        cli = clientes.first() #El cliente es unico

    metaSes = MetaSession.get_or_create(cli)


    #PASO 3: Buscamos la sesion activa

    sesiones = Session.objects.filter(clientID__exact = cli.clientID)
    search = Search.objects.filter(query__exact = query).filter(sessionID__in = sesiones).order_by('-timestamp')

    ses = None
    if(not sesiones or not search):
        return Response(status=status.HTTP_400_BAD_REQUEST)
    else:
        ses = search.first().sessionID;


    #PASO 4: Una vez que tenemos la sesion y la query, hacemos relevance feedback
    word = Indexer.getWord(query, ses)
    query += " " + word


    #PASO 5: Creamos una entrada para la busqueda en la base de datos
    search = Search().create(ses, query)

    #PASO 6: Realizamos la metabusqueda
    meta = RankSimMetasearcher()

    # while(meta.searcherList.__len__() is not 0):
    #     for searcher in meta.searcherList:
    #         meta.searcherList.remove(searcher)

    meta.addSearcher(GoogleSearcher())
    meta.addSearcher(BingSearcher())
    meta.addSearcher(Carrot2Searcher())
    meta.addSearcher(FarooSearcher())

    dataLists = meta.doSearch(query, search)
    resultLinks = meta.doMetaSearch(dataLists, search)


    if resultLinks is not None:
        search.numResults = resultLinks.__len__()
        search.save()
    else:
        resultLinks = list()

    data = list()
    if filtering == True:
        for lnk in resultLinks:
            if not SavedLink.objects.filter(metaSessionID__exact = metaSes).filter(url__exact = lnk.url):
                data.append(lnk)
    else:
        data = resultLinks

    serializer = LinkSerializer(data, many=True)
    for lnk in serializer.data:
        if not SavedLink.objects.filter(metaSessionID__exact = metaSes).filter(url__exact = lnk['url']):
            lnk['saved'] = False
        else:
            lnk['saved'] = True

    dataClicked = ClickedLink.objects.filter(sessionID__exact = ses)
    ClickSerializer = ClickedLinkSerializer(dataClicked, many=True)
    dataSaved = SavedLink.objects.filter(metaSessionID__exact = metaSes)
    SavedSerializer = SavedLinkSerializer(dataSaved, many=True)

    resp = {'query' : query, 'linkList' : serializer.data, 'clicked': ClickSerializer.data, 'saved' : SavedSerializer.data}
    return Response(resp)

#_____DIVERSITY
###
# Gets the diversity matrix for a ranking
# @param request Client's request. Includes two arguments: query, that corresponds with the query, clientIP, which represents clients IP direction
# @return the diversity matrix if OK, error code if not
@api_view(['GET'])
def doDiversity(request):

    numWords = 1
     #PASO 1: Comprobar que no es nula la busqueda, la IP del cliente o el agente
    if len(request.GET.keys()) > 0:
        if request.GET.get('query') is None or request.GET['query'] == '':
            return Response(status=status.HTTP_400_BAD_REQUEST)
        elif request.GET.get('clientIP') is None or request.GET['clientIP'] == '':
            return Response(status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    query = request.GET['query'].encode('UTF-8')
    #PASO 2:Buscamos el cliente
    clientes = Client.objects.filter(clientIP__exact = request.GET['clientIP']).filter(userAgent__exact = request.META['HTTP_USER_AGENT'])
    cli = None
    if(not clientes):
        return Response('Not client')
    elif clientes.count() > 1:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        cli = clientes.first() #El cliente es unico

    metaSes = MetaSession.get_or_create(cli)


    #PASO 3: Buscamos la sesion activa
    sesiones = Session.objects.filter(clientID__exact = cli.clientID).filter(active = True)
    ses = None
    if(not sesiones):
        return Response(status=status.HTTP_400_BAD_REQUEST)
    elif sesiones.count() > 1:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        ses = sesiones.first()

    busquedas = Search.objects.filter(query__exact = query).order_by('-timestamp')
    if(not busquedas):
        return Response(status=status.HTTP_400_BAD_REQUEST)
    else:
        search = busquedas.first()

    #PASO 5: Obtenemos el resultado de la busqueda
    resultList = SearchResult.objects.filter(searchID__exact = search)

    #DIVERSITY
    matrix = DiversityMatrix.diversityMatrix(resultList, 'res/index/diversity/' + query)
    listaResp = []
    for doc in matrix:
        listaResp.append({'rank1' : doc.doc1rank, 'rank2' : doc.doc2rank , 'distance' : doc.distance})


    resp = {'query' : query, 'matrix' : listaResp}
    return Response(resp)

## Gets the sources of each result for a certain query
# @param request User's request. Includes the submitted query and the user's IP
# @return A list of search results with their sources
#
@api_view(['GET'])
def getSources(request):
    #STEP 1: Check if query and client IP are not null
    if len(request.GET.keys()) > 0:
        if request.GET.get('query') is None or request.GET['query'] == '':
            return Response(status=status.HTTP_400_BAD_REQUEST)
        elif request.GET.get('clientIP') is None or request.GET['clientIP'] == '':
            return Response(status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    query = request.GET['query'].encode('UTF-8')


    #STEP 2: Search for the client
    clientes = Client.objects.filter(clientIP__exact = request.GET['clientIP']).filter(userAgent__exact = request.META['HTTP_USER_AGENT'])
    cli = None
    if(not clientes):
        return Response('Not client')
    elif clientes.count() > 1:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        cli = clientes.first() #The client is unique

    metaSes = MetaSession.get_or_create(cli)


    # #STEP 3: Look for the active session
    sesiones = Session.objects.filter(clientID__exact = cli.clientID).filter(active = True)
    ses = None
    if(not sesiones):
        return Response(status=status.HTTP_400_BAD_REQUEST)
    elif sesiones.count() > 1:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        ses = sesiones.first()

    busquedas = Search.objects.filter(sessionID__exact = sesiones).filter(query__exact = query).order_by('-timestamp')
    if(not busquedas):
        return Response(status=status.HTTP_400_BAD_REQUEST)
    else:
        search = busquedas.first()

    #STEP 2: Look for the search results
    resultList = SearchResult.objects.filter(searchID__exact = search).order_by('rank')

    listDocs = []
    for res in resultList:
        sources = Sources.objects.filter(result__exact=res)
        listSources = []
        listRanks = []
        for source in sources:
            listSources.append(source.ranker.rankerID)
            listRanks.append(source.rank)
        listDocs.append(DocSource(res.rank, listSources, listRanks))

    listaResp=[]
    for doc in listDocs:
        listaResp.append({'rank' : doc.docRank, 'sources' : doc.sourcesList, 'ranks' : doc.sourcesRanks})

    resp = {'query' : query, 'sources' : listaResp}
    return Response(resp)


