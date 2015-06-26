##
# @package ZaexEvaluation.Interleaving.balancedInterleaving
# Definition for a interleaver that implements the balanced method.
# @author Javier Sanz-Cruzado Puig

from TFGSearch.Metasearch.metasearcher import *
from ZaexEvaluation.Interleaving.evaluationInterleaver import *
from operator import attrgetter
import re
import random

##
# Interleaver that uses the balanced method (For Evaluation)
class BalancedInterleaving(EvaluationInterleaver):

    ##
    # Constructor
    def __init__(self):
        super(Metasearcher, self).__init__()
        self.searcherList = list()

    ## Given several lists of links, fuses them into a unique list, by using balanced interleaving
    # @param self The interleaver
    # @param linkLists List of MetaSearchLinks
    # @returns Ordered SearchResult list if OK, None si ERROR or there are no results
    def doMetaSearch(self, linkLists, search, values={}):
        if(linkLists is None):
            return None

        numBuscadores = linkLists.__len__()
        if(numBuscadores == 0):
            return None

        #Selecting the order of the entries A/B/C/D
        defLinkLists = []
        for list in linkLists:
            ls = []
            for res in list:
                if res.searchID == search:
                    ls.append(res)
            defLinkLists.append(ls)

        linkLists = defLinkLists
        initial = linkLists.keys()
        orden = list()
        listaLongs = list()

        for i in range(numBuscadores):
            rnd = random.randint(0, initial.__len__()-1)
            orden.append(initial[rnd])
            initial.remove(initial[rnd])


        for i in range(numBuscadores):
            listaLongs.append(linkLists[orden[i]].__len__())

        #Now, we have an ordered list of searchers, and listaLongs contains the length of the lists for those searchers
        results = list()

        for i in range(max(listaLongs)):
            for j in range(numBuscadores):
                val = linkLists[orden[j]]

                if(val.__len__() < i):
                    continue

                lnk = val[i]
                filtro = [x for x in results if x.url == lnk.url]
                if filtro.__len__() > 0:
                    existentLink = filtro[0]
                    existentLink.addSource(orden[j], i+1)
                    existentLink.addInterleavingSource(orden[j], i+1)
                else:
                    lnk.value = 2 ##VALUE 2 => EVALUATION
                    cad = []
                    if lnk.snippet is not None:
                        cad = lnk.snippet.split()
                    lnk.snippet = ''
                    for c in cad:
                        lnk.snippet += re.sub(r'[^\w,",","."]', '', c) + ' '
                    lnk.save()
                    lnk.addSource(orden[j], i+1)
                    lnk.addInterleavingSource(orden[j], i+1)
                    results.append(lnk)

        #ordenamos
        if results.__len__() == 0:
            return None

        i = 0
        for metaLnk in results:
            i += 1
            metaLnk.rank = i
            metaLnk.save()
        return results

    ## Given several lists of links, fuses them into a unique list, by using balanced interleaving. Assumes
    # that the evaluated systems are not the origin systems, so it does not save sources (only interleaving ones)
    # @param self The interleaver
    # @param linkLists List of MetaSearchLinks
    # @returns Ordered SearchResult list if OK, None si ERROR or there are no results
    def doMetaSearchNotSaveSource(self, linkLists):
        if(linkLists is None):
            return None

        numBuscadores = linkLists.__len__()
        if(numBuscadores == 0):
            return None

        #Selecting the order of the entries A/B/C/D

        initial = linkLists.keys()
        orden = list()
        listaLongs = list()

        for i in range(numBuscadores):
            rnd = random.randint(0, initial.__len__()-1)
            orden.append(initial[rnd])
            initial.remove(initial[rnd])


        for i in range(numBuscadores):
            listaLongs.append(linkLists[orden[i]].__len__())

        #Now, we have an ordered list of searchers, and listaLongs contains the length of the lists for those searchers
        results = list()

        for i in range(max(listaLongs)):
            for j in range(numBuscadores):
                val = linkLists[orden[j]]

                if(val.__len__() < i):
                    continue

                lnk = val[i]
                filtro = [x for x in results if x.url == lnk.url]
                if filtro.__len__() > 0:
                    existentLink = filtro[0]
                    existentLink.addInterleavingSource(orden[j], i+1)
                else:
                    lnk.value = 2 ##VALUE 2 => EVALUATION
                    cad = []
                    if lnk.snippet is not None:
                        cad = lnk.snippet.split()
                    lnk.snippet = ''
                    for c in cad:
                        lnk.snippet += re.sub(r'[^\w,",","."]', '', c) + ' '
                    lnk.save()
                    lnk.addInterleavingSource(orden[j], i+1)
                    results.append(lnk)

        #ordenamos
        if results.__len__() == 0:
            return None

        i = 0
        for metaLnk in results:
            i += 1
            metaLnk.rank = i
            metaLnk.save()
        return results