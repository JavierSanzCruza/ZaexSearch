import urllib2
import urllib
import json
__author__ = 'javier'

class Webservice:
    def call_ws(self, url, userAgent):
        # create credential for authentication
        request = urllib2.Request(url)
        request.add_header('User-Agent', userAgent)
        request_opener = urllib2.build_opener()
        response = request_opener.open(request)
        response_data = response.read()
        json_result = json.loads(response_data)
        return json_result

    ## LLAMADAS AL WEBSERVICE
    def call_ws_search(self, query, filter, ip, userAgent):
        #search_type: Web, Image, News, Video
        query = urllib.quote(query.encode("UTF-8"))
        # create credential for authentication

        url = 'http://150.244.58.41:10000/search?query='+query+'&clientIP='+ip+'&filter=False'
        request = urllib2.Request(url)
        request.add_header('User-Agent', userAgent)
        request_opener = urllib2.build_opener()
        response = request_opener.open(request)
        response_data = response.read()
        json_result = json.loads(response_data)
        return json_result
