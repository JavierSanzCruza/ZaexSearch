##
# @package TFGSearch.Metasearch.bingSearcher
# Definition of the class that calls Bing API
# @author Javier Sanz-Cruzado Puig


__author__ = 'javier'

import urllib
import urllib2
import json

from TFGSearch.Metasearch.searcher import Searcher
from TFGSearch.models import SearchResult


##
# Class that calls Bing API
class BingSearcher(Searcher):

    def __init__(self):
        Searcher.__init__(self, "Bing");


    ##
    # Calls a Bing search engine
    # @param query query
    # @param search Search to associate the results
    # @returns a ranking of searchResults
    def doSearch(self, query, search):

        try:
            #search_type: Web, Image, News, Video

	    ##INSERT BING KEY HERE
            key= ''
            query = urllib.quote(query)
            # create credential for authentication
            user_agent = 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; FDM; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 1.1.4322)'
            credentials = (':%s' % key).encode('base64')[:-1]
            auth = 'Basic %s' % credentials
            url = 'https://api.datamarket.azure.com/Data.ashx/Bing/Search/Web?Query=%27'+query+'%27&$top=10&$format=json'
            request = urllib2.Request(url)
            request.add_header('Authorization', auth)
            request.add_header('User-Agent', user_agent)
            request_opener = urllib2.build_opener()
            response = request_opener.open(request)
            response_data = response.read()
            json_result = json.loads(response_data)

            result_d = json_result.get('d')
            if result_d is None:
                return None

            result_list = result_d.get('results')

            # Creamos la lista de resultados
            bingResults = list()

            i = 0
            for result in result_list:
                i = i + 1

                lnk = SearchResult()
                lnk.searchID = search
                lnk.title = result['Title']
                lnk.url = result['Url']
                lnk.snippet = result['Description']
                lnk.rank = i

                bingResults.append(lnk)

            return bingResults
        except:
            return None
