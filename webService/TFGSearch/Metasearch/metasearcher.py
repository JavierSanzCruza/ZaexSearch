## @package TFGSearch.Metasearch
# Package that contains classes and methods for the metasearch. Contains classes that communicate with the
# aggregated search engines and the classes that combine the different rankings using a determined algorithm
# @author Javier Sanz-Cruzado Puig

##
# @package TFGSearch.Metasearch.metasearcher
# Definition of the Metasearcher abstract class
# @file TFGSearch.Metasearch.metasearcher.py
# @author Javier Sanz-Cruzado Puig

from abc import ABCMeta, abstractmethod
from TFGSearch.models import *
import thread

## Abstract class for metasearcher
class Metasearcher:
    __metaclass__ = ABCMeta
    numThreads = 0
    lock = thread.allocate_lock()
    resultLists = {}
    ##
    # Searcher List
    searcherList = list()
    newSearch = False

    ##
    # Makes a searcher call the search engine
    # index Index of the searcher in the searcherList
    # query query to submit
    # search search object
    def doSearchIndex(self, index, query, search):
        lista = self.searcherList[index].doSearch(query, search)
        self.lock.acquire()
        if(lista is not None and lista.__len__() > 0):
            self.resultLists[self.searcherList[index].name] = lista
        self.numThreads -= 1
        self.lock.release()
        return

    ##
    # Constructor
    def __init__(self):
        searcherList = list()

    ##
    # Adds a searcher to the metasearcher
    # @param self Metasearcher
    # @param searcher Searcher to add
    def addSearcher(self, searcher):
        self.searcherList.append(searcher)

    ##
    # Removes a searcher from the metasearcher
    # @param self The metasearcher
    # @param searcher Searcher to delete
    def deleteSearcher(self, searcher):
        self.searcherList.remove(searcher)

    ##
    # Makes a query to each search engine
    # @param self metasearcher
    # @param query String with the query
    # @param search Search to which associate the results
    def doSearch(self, query, search):
        data = {}

        self.resultLists = {}
        #En primer lugar, comprobamos si se ha realizado la busqueda
        previousSearch = Search.objects.filter(query__exact=query).order_by('-timestamp')
        #If the search has not been answered before, or the previous answer was more than an hour ago, ask for new data
        if previousSearch is None or previousSearch.__len__() <= 1 or (timezone.now() - previousSearch[1].timestamp).seconds > 3600 or previousSearch[1].numResults == 0:
            self.newSearch = True
            for i in range(self.searcherList.__len__()):
                thread.start_new_thread(self.doSearchIndex, (i, query, search))
                self.lock.acquire()
                self.numThreads += 1
                self.lock.release()

            while self.numThreads != 0:
                pass

        else: #Si se ha realizado antes, obtenemos los resultados desde la base de datos
            results = SearchResult.objects.filter(searchID__exact = previousSearch[1])
            sources = Sources.objects.filter(result__in = results).order_by('ranker', 'rank')
            for i in range(self.searcherList.__len__()):
                ls = []
                rankers = Ranker.objects.filter(rankerID__exact = (i+1))
                name = rankers.first().name
                for source in sources:
                    if source.ranker.rankerID == (i+1):
                        result = SearchResult.objects.filter(resultID__exact = source.result.resultID).first()
                        lnk = SearchResult()
                        lnk.searchID = search
                        lnk.title = result.title
                        lnk.url = result.url
                        lnk.snippet = result.snippet
                        lnk.rank = source.rank
                        ls.append(lnk)
                self.resultLists[name] = ls

        return self.resultLists


    ###
    # Destroys the metasearcher
    def destroy(self):
        for searcher in self.searcherList:
            self.searcherList.remove(searcher)

    ## Given several lists of links, combines results and orders them in a unified ranking
    # @param self Metasearcher
    # @param linkLists Lists of links
    # @returns ordered SearchResult list if OK, None if there are no results or an ERROR occurs
    @abstractmethod
    def doMetaSearch(self, linkLists, search, values={}): pass

