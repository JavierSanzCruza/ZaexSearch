# -*- encoding: utf-8 -*-
# -*- coding: utf-8 -*-
## @package ZaexEvaluation.views
# Webservice's API for evaluation

#Bibliotecas de DjangoRestFramework
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
#Modelos y serializadores para el webService
from TFGSearch.serializers import *
#Bibliotecas para realizar la metabusqueda
from TFGSearch.Metasearch.googleSearcher import *
from TFGSearch.Metasearch.bingSearcher import *
from TFGSearch.Metasearch.carrot2Searcher import *
from TFGSearch.Metasearch.farooSearcher import *
from TFGSearch.SessionDetection.searchPatternDetector import *
from ZaexEvaluation.Evaluation.probabilityABTest import *
from ZaexEvaluation.Metrics.ild import *
from ZaexEvaluation.Metrics.recallAtK import *
from ZaexEvaluation.Metrics.map import *
from ZaexEvaluation.Metrics.nDCGAtK import *
from ZaexEvaluation.Metrics.mrr import *
from TFGSearch.Metasearch.docSource import *


###
# Retrieves results from different search engines for evaluation
# @param request GET HTTP Request
# @return the search data
@api_view(['GET'])
def evaluate_search(request):

    #STEP 1: Check if search, client IP and filter are not none
    if request.GET.get('query') is None or request.GET.get('query') == '':
        return Response(status=status.HTTP_400_BAD_REQUEST)
    elif request.GET.get('clientIP') is None or request.GET['clientIP'] == '':
        return Response(status=status.HTTP_400_BAD_REQUEST)

    busqueda = request.GET['query'].encode("UTF-8")

    #STEP 2: Check if the client exists in database
    cli = Client().get_or_create(request.GET['clientIP'], request.META['HTTP_USER_AGENT'])
    if cli is None:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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

    if ses is None:
        ses2.save()
        ses = ses2
    elif ses == ses2:
        ses.save()
    else:
        ses.active = False
        ses.save()
        ses = ses2
        ses2.save()

    #STEP 5: Create an entry for the search in database
    search = Search().create(ses, busqueda)

    #STEP 6: Do the metasearch
    meta = ProbabilisticInterleaving()
    eval = ProbabilityABTest()

    meta.addSearcher(GoogleSearcher())
    meta.addSearcher(BingSearcher())
    meta.addSearcher(Carrot2Searcher())
    meta.addSearcher(FarooSearcher())

    dataLists = meta.doSearch(busqueda, search)
    resultLinks = eval.interleaveResults(dataLists, search)

    googleRanker = EvaluatedRanker.objects.filter(name__exact='Google').first()
    bingRanker = EvaluatedRanker.objects.filter(name__exact='Bing').first()
    farooRanker = EvaluatedRanker.objects.filter(name__exact='Faroo').first()
    carrot2Ranker = EvaluatedRanker.objects.filter(name__exact = 'Carrot2').first()
    asciibusqueda = ''.join(e for e in busqueda if e.isalnum())

    #Calculate ILD for each searcher
    thread.start_new_thread(ILD.calculateILD, (dataLists['Google'], 'res/eval/index/' + cli.clientIP + '/' + asciibusqueda + '/google', googleRanker))
    thread.start_new_thread(ILD.calculateILD, (dataLists['Bing'], 'res/eval/index/' + cli.clientIP + '/' + asciibusqueda + '/bing', bingRanker))
    thread.start_new_thread(ILD.calculateILD, (dataLists['Faroo'], 'res/eval/index/' + cli.clientIP + '/' + asciibusqueda + '/faroo', farooRanker))
    thread.start_new_thread(ILD.calculateILD, (dataLists['Carrot2'], 'res/eval/index/' + cli.clientIP + '/' + asciibusqueda + '/carrot', carrot2Ranker))


    # Return the search results
    if resultLinks is not None:
        search.numResults = resultLinks.__len__()
        search.save()
    else:
        resultLinks = list()


    data = resultLinks



    FoundSerializer = LinkSerializer(data, many=True)

    dataDef = { 'search' : FoundSerializer.data}
    return Response(dataDef)


## Returns to the client a series of links the client has clicked previously
# @param request Client's request. Includes parameters query (search string), clientIP (client's IP) and rank (rank of the link on result list)
# @returns Error code if a problem has ocurred, or a list of JSON links with the clicked links
@api_view(['GET'])
def clickedEvaluation_list(request):

    #STEP 1: Check that query, client IP and rank are not null
    if len(request.GET.keys()) > 0:
        if request.GET.get('query') is None or request.GET['query'] == '':
            return Response(status=status.HTTP_400_BAD_REQUEST)
        elif request.GET.get('clientIP') is None or request.GET['clientIP'] == '':
            return Response(status=status.HTTP_400_BAD_REQUEST)
        elif request.GET.get('rank') is None or request.GET['rank'] == '':
            return Response(status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    #STEP 2: Search for the client
    clientes = Client.objects.filter(clientIP__exact = request.GET['clientIP']).filter(userAgent__exact = request.META['HTTP_USER_AGENT'])
    cli = None
    if(not clientes):
        return Response('Not client')
    elif clientes.count() > 1:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        cli = clientes.first() #The client is unique


    #STEP 3: Search for the active session
    sesiones = Session.objects.filter(clientID__exact = cli.clientID).filter(active = True)
    ses = None
    if(not sesiones):
        return Response(status=status.HTTP_400_BAD_REQUEST)
    elif sesiones.count() > 1:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        ses = sesiones.first()

    #STEP 4: Obtaining the search
    busquedas = Search.objects.filter(query__exact = request.GET['query'])
    if(not busquedas):
        return Response(status=status.HTTP_400_BAD_REQUEST)
    else:
        busqueda = busquedas.last()

    #STEP 5: Get the search results
    resultList = SearchResult.objects.filter(searchID__exact = busqueda ).filter(rank__exact = request.GET['rank'])
    if(not resultList):
        return Response(status=status.HTTP_400_BAD_REQUEST)
    else:
        res = resultList.first()

    #STEP 6: Create an entry for the clicked link in database

    clicked = ClickedLink.objects.filter(searchResult__exact = res)
    if(not clicked):
        click = ClickedLink()
        click.sessionID = ses
        click.searchResult = res
        click.url = res.url
        click.snippet = res.snippet
        click.title = res.title
        click.evaluation = True

        click.save()


    #STEP 7: Return the clicked links list

    data = ClickedLink.objects.filter(sessionID__exact = ses)


    #Serialize and send the results
    serializer = ClickedLinkSerializer(data, many=True)
    return Response(serializer.data)


## Evaluates several search engines by the data collected by clicks
# @param request User's request
# @returns A list of search engines with the expected number of clicks obtained by each system
@api_view(['GET'])
def evaluateClick(request):

    evMethod = ProbabilityABTest()

    data = evMethod.evaluateClicks()

    ls = []
    for ranker in data:
        ls.append({'name' : ranker, 'evaluation' : data[ranker]})
    #Serialize and sent results
    return Response(ls)

## Evaluates several search engines by the data collected by clicks
# @param request User's request
# @returns A list of search engines with the expected number of queries won by each system
@api_view(['GET'])
def evaluateQuery(request):

    evMethod = ProbabilityABTest()

    #PASO 7: Devolvemos la lista de links clickados

    data = evMethod.evaluateQueries()


    ls = []
    for ranker in data:
        ls.append({'name' : ranker, 'evaluation' : data[ranker]})
    #Serialize and sent results
    return Response(ls)


## Evaluates several search engines by the data collected by clicks
# @param request User's request
# @returns A list of search engines with the precission at k metric results for each engine
@api_view(['GET'])
def evaluatePAtK(request):
    if len(request.GET.keys()) > 0:
        if request.GET.get('k') is None or request.GET['k'] == '':
            return Response(status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)



    k = int(request.GET['k'])
    evMethod = PrecissionAtK(k)

    data = evMethod.evaluateMetric()
    ls = []
    for ranker in data:
        ls.append({'name' : ranker, 'evaluation' : data[ranker]})
    #Serialize and sent results
    return Response(ls)

## Evaluates several search engines by the data collected by clicks
# @param request User's request
# @returns A list of search engines with the recall at k metric results for each engine
@api_view(['GET'])
def evaluateRAtK(request):
    if len(request.GET.keys()) > 0:
        if request.GET.get('k') is None or request.GET['k'] == '':
            return Response(status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)



    k = int(request.GET['k'])
    evMethod = RecallAtK(k)
    #PASO 7: Devolvemos la lista de links clickados

    data = evMethod.evaluateMetric()


    ls = []
    for ranker in data:
        ls.append({'name' : ranker, 'evaluation' : data[ranker]})
    #Serialize and sent results
    return Response(ls)

## Evaluates several search engines by the data collected by clicks
# @param request User's request
# @returns A list of search engines with the negative cumulative discount at k metric results for each engine
@api_view(['GET'])
def evaluateNDCGAtK(request):
    if len(request.GET.keys()) > 0:
        if request.GET.get('k') is None or request.GET['k'] == '':
            return Response(status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)



    k = int(request.GET['k'])
    evMethod = NDCGAtK(k)
    #PASO 7: Devolvemos la lista de links clickados

    data = evMethod.evaluateMetric()


    ls = []
    for ranker in data:
        ls.append({'name' : ranker, 'evaluation' : data[ranker]})
    #Serialize and sent results
    return Response(ls)

## Evaluates several search engines by the data collected by clicks
# @param request User's request
# @returns A list of search engines with the meaen average precission metric results for each engine
@api_view(['GET'])
def evaluateMAP(request):
    evMethod = MAP()

    #PASO 7: Devolvemos la lista de links clickados

    data = evMethod.evaluateMetric()


    ls = []
    for ranker in data:
        ls.append({'name' : ranker, 'evaluation' : data[ranker]})
    #Serialize and sent results
    return Response(ls)

## Evaluates several search engines by the data collected by clicks
# @param request User's request
# @returns A list of search engines with the mean reciprocal rank metric results for each engine
@api_view(['GET'])
def evaluateMRR(request):

    evMethod = MRR()

    #PASO 7: Devolvemos la lista de links clickados

    data = evMethod.evaluateMetric()


    ls = []
    for ranker in data:
        ls.append({'name' : ranker, 'evaluation' : data[ranker]})
    #Serialize and sent results
    return Response(ls)

## Evaluates several search engines by the data collected by clicks
# @param request User's request
# @returns A list of search engines with the expected intra list dissimilarity metric results for each engine
@api_view(['GET'])
def evaluateILD(request):
    ls = []
    for ranker in EvaluatedRanker.objects.all():
        ranker.evaluation = ranker.ild
        ranker.save()
        ls.append({'name' : ranker.name, 'evaluation' : ranker.ild})

    #Serialize and sent results
    return Response(ls)

@api_view(['GET'])
def evaluationReport(request):
    #EvaluateQueries
    evMethod = ProbabilityABTest()

    data = evMethod.evaluateClicks()


    #Serialize and sent results
    clickserializer = {}
    for ranker in data:
        clickserializer[ranker] = data[ranker]

    #PASO 7: Devolvemos la lista de links clickados

    data = evMethod.evaluateQueries()


    #Serializamos y enviamos los resultados
    queryserializer = {}
    for ranker in data:
        queryserializer[ranker] = data[ranker]



    #P At 5
    evMethod = PrecissionAtK(5)

    data = evMethod.evaluateMetric()

    pat5serializer = {}
    for ranker in data:
        pat5serializer[ranker] = data[ranker]


    #P At 10
    evMethod = PrecissionAtK(10)

    data = evMethod.evaluateMetric()

    pat10serializer = {}
    for ranker in data:
        pat10serializer[ranker] = data[ranker]


    #P At 5
    evMethod = RecallAtK(5)

    data = evMethod.evaluateMetric()

    rat5serializer = {}
    for ranker in data:
        rat5serializer[ranker] = data[ranker]


    #P At 10
    evMethod = RecallAtK(10)

    data = evMethod.evaluateMetric()

    rat10serializer = {}
    for ranker in data:
        rat10serializer[ranker] = data[ranker]

    #nDCG At 5
    evMethod = NDCGAtK(5)

    data = evMethod.evaluateMetric()

    ndcgat5serializer = {}
    for ranker in data:
        ndcgat5serializer[ranker] = data[ranker]


    #nDCG At 10
    evMethod = NDCGAtK(10)

    data = evMethod.evaluateMetric()

    ndcgat10serializer = {}
    for ranker in data:
        ndcgat10serializer[ranker] = data[ranker]

    #MRR
    #P At 5
    evMethod = RecallAtK(5)

    data = evMethod.evaluateMetric()

    rat5serializer = {}
    for ranker in data:
        rat5serializer[ranker] = data[ranker]


    #MRR
    evMethod = MRR()

    data = evMethod.evaluateMetric()

    mrrserializer = {}
    for ranker in data:
        mrrserializer[ranker] = data[ranker]

    #MAP
    evMethod = MAP()

    data = evMethod.evaluateMetric()

    mapserializer = {}
    for ranker in data:
        mapserializer[ranker] = data[ranker]


    #ILD
    ildserializer = {}
    for ranker in EvaluatedRanker.objects.all():
        ildserializer[ranker.name] = ranker.ild
    report = {'clicks': clickserializer, 'queries':queryserializer, 'PAt5' : pat5serializer, 'PAt10' : pat10serializer, 'RAt5' : rat5serializer, 'RAt10' : rat10serializer, 'nDCGAt5' : ndcgat5serializer, 'nDCGAt10' : ndcgat10serializer, 'MRR' : mrrserializer, 'MAP': mapserializer, 'ILD' : ildserializer}
    return Response(report)