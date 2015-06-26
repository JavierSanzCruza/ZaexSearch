##
# @package TFGSearch.Metasearch.farooSearcher
# Definition of the class that calls Faroo API
# @author Javier Sanz-Cruzado Puig
__author__ = 'javier'
import urllib
import urllib2
import json

from TFGSearch.Metasearch.searcher import Searcher
from TFGSearch.models import SearchResult


##
# Calls Faroo Search Engine API
class FarooSearcher(Searcher):

    def __init__(self):
        Searcher.__init__(self,"Faroo")


    ##
    # Calls Faroo search engine
    # @param query query
    # @param search Search to associate the results
    # @returns a ranking of searchResults
    def doSearch(self, query, search):
        try:
            key = ''
            query = urllib.quote(query)

            user_agent = 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; FDM; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 1.1.4322)'
            url = 'http://www.faroo.com/api?q=' + query + '&start=1&length=10&l=en&src=web&f=json&key=' + key
            request = urllib2.Request(url)
            request.add_header('User-Agent', user_agent)
            request_opener = urllib2.build_opener()
            response = request_opener.open(request)
            response_data = response.read()
            json_result = json.loads(response_data)
            result_list = json_result.get('results')

            if(result_list is None):
                return None

            i = 0
            farooResults = list()
            for result in result_list:
                i = i+1
                lnk = SearchResult()
                lnk.searchID = search
                lnk.title = result['title']
                lnk.url = result['url']
                lnk.snippet = result.get('kwic')

                lnk.rank = i

                farooResults.append(lnk)

            return farooResults
        except:
            return None
