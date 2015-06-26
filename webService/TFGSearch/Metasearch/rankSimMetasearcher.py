# -*- encoding: utf-8 -*-
# -*- coding: utf-8 -*-

##
# @package TFGSearch.Metasearch.rankSimMetasearcher
# Definition of a metasearcher that uses Rank-Sim normalization
# @author Javier Sanz-Cruzado Puig

from TFGSearch.Metasearch.metasearcher import *
from operator import attrgetter
import re

##
# Metasearcher that uses Rank-Sim and Linear combination to generate scores
class RankSimMetasearcher(Metasearcher):

    def __init__(self):
        super(Metasearcher, self).__init__()
        self.searcherList = list()

    ## Given some rankings from several search engines, combines results and orders them
    # @param self Metasearcher
    # @param linkLists Rankings
    # @param values Weights for linear combination
    # @returns Ordered SearchResult list if OK, None if ERROR or there are not results
    def doMetaSearch(self, linkLists, search, values={}):
        if(linkLists is None):
            return None

        if values is not None and values.__len__() == linkLists.__len__():
            numBuscadores = sum(values)
        else:
            numBuscadores = linkLists.__len__()
            values = {}
            for key in linkLists:
                values[key] = 1
        if(numBuscadores == 0):
            return None

        results = list()

        i=0
        #Calculamos los valores para cada link (Solo permitimos una URL)
        for key in linkLists:
            val = linkLists[key]
            numResults = val.__len__()
            if(numResults == 0):
                continue
            for lnk in val:
                if lnk.searchID != search:
                    continue
                i = i + 1
                filtro = [x for x in results if x.url == lnk.url]
                if filtro.__len__() > 0 :
                    existentLink = filtro[0]
                    existentLink.value += (numResults - lnk.rank + 1.0)/(numResults*numBuscadores)*values[key]
                    existentLink.save()
                    existentLink.addSource(key, lnk.rank)
                else:
                    lnk.value = (numResults - lnk.rank + 1.0)/(numResults*numBuscadores)*values[key]
                    cad =[]
                    if lnk.snippet is not None:
                        cad = lnk.snippet.split()
                    lnk.snippet = ''
                    for c in cad:
                        lnk.snippet += re.sub(r'[^\w.,-áéíóúàèìòùñäëïöü]', '', c) + ' '
                    lnk.save()
                    lnk.addSource(key, lnk.rank)
                    results.append(lnk)
        #ordenamos
        if results.__len__() == 0:
            return None

        results = sorted(results, key=attrgetter('value'), reverse=True)
        i = 0
        for metaLnk in results:
            i += 1
            metaLnk.rank = i
            metaLnk.save()
        return results
