##
# @package TFGSearch.Metasearch.googleSearcher
# Definition of the class that calls Google API
# @author Javier Sanz-Cruzado Puig

__author__ = 'javier'
import urllib
import urllib2
import json

from TFGSearch.Metasearch.searcher import Searcher
from TFGSearch.models import SearchResult


##
# Calls Google Custom Search API
class GoogleSearcher(Searcher):

    def __init__(self):
        Searcher.__init__(self, "Google");


    ##
    # Calls Google search engine
    # @param query query
    # @param search Search to associate the results
    # @returns a ranking of searchResults
    def doSearch(self, query, search):
        try:
            key = ''
            cx = ''
            query = urllib.quote(query)

            try:
                user_agent = 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; FDM; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 1.1.4322)'
                url = 'https://www.googleapis.com/customsearch/v1?key='+key+'&cx='+cx+'&q='+query
                request = urllib2.Request(url)
                request.add_header('User-Agent', user_agent)
                request_opener = urllib2.build_opener()
                response = request_opener.open(request)
                response_data = response.read()
                json_result = json.loads(response_data)
                result_list = json_result.get('items')

                if result_list is None:
                    return None
            except urllib2.HTTPError:
                return None
            googleResults = list()

            i= 0
            for result in result_list:
                i = i+1
                lnk = SearchResult()
                lnk.searchID = search
                lnk.title = result['title']
                lnk.url = result['link']
                lnk.snippet = result['snippet']

                lnk.rank = i

                googleResults.append(lnk)

            return googleResults
        except:
            return None
