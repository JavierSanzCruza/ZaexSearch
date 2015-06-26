##
# @package TFGSearch.Metasearch.carrot2Searcher
# Definition of the class that calls Carrot2 API
# @author Javier Sanz-Cruzado Puig
__author__ = 'javier'

import urllib
import urllib2
import json

from TFGSearch.Metasearch.searcher import Searcher
from TFGSearch.models import SearchResult


##
# Calls Carrot2 API (Etools)
class Carrot2Searcher(Searcher):

    def __init__(self):
        Searcher.__init__(self, "Carrot2");


    ##
    # Calls a Carrot2 search engine
    # @param query query
    # @param search Search to associate the results
    # @returns a ranking of searchResults
    def doSearch(self, query, search):
        try:
            mydata = [('dcs.source', 'etools'), ('dcs.output.format', 'JSON'), ('results', '10'), ('query', query)]
            url = 'http://localhost:9000/dcs/rest'
            user_agent = 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; FDM; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 1.1.4322)'

            mydata = urllib.urlencode(mydata)
            request = urllib2.Request(url, mydata)
            request.add_header('User-Agent', user_agent)
            request.add_header('Content-type', 'application/x-www-form-urlencoded')
            response_data =urllib2.urlopen(request).read()
            json_result = json.loads(response_data)
            result_list = json_result.get('documents')

            if result_list is None:
                return None

            carrotResults = list()

            i = 0
            for result in result_list:
                i = i+1
                lnk = SearchResult()
                lnk.searchID = search
                lnk.title = result['title']
                lnk.url = result['url']
                lnk.snippet = result.get('snippet')
                lnk.rank = i

                carrotResults.append(lnk)

            return carrotResults
        except:
            return None
