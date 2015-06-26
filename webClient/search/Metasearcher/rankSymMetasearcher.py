from operator import attrgetter
import re

__author__ = 'javier'

class RankSymMetasearcher:
    def doMetaSearch(self, linkLists, values):
            if(linkLists is None):
                return None

            if values is not None and values.__len__() == linkLists.__len__():
                numBuscadores = sum(values.values())
            else:
                numBuscadores = linkLists.__len__()
                values = {}
                for key in linkLists:
                    values[key] = 1
            if(numBuscadores == 0):
                return None

            results = list()

            i=0
            dictList = {}
            #Calculamos los valores para cada link (Solo permitimos una URL)
            for key in linkLists:
                val = linkLists[key]
                numResults = val.__len__()
                if(numResults == 0):
                    continue
                for lnk in val:
                    i = i + 1
                    filtro = [x for x in results if x.resultID == lnk.resultID]
                    if filtro.__len__() > 0 :
                        existentLink = filtro[0]
                        existentLink.value += (numResults - lnk.rank + 1.0)/(numResults)*values[key]/numBuscadores

                    else:
                        lnk.value = (numResults - lnk.rank + 1.0)/(numResults)
                        lnk.value *= values[key]/numBuscadores
                        cad =[]
                        if lnk.snippet is not None:
                            cad = lnk.snippet.split()
                        lnk.snippet = ''
                        for c in cad:
                            lnk.snippet += re.sub(r'[^\w]', '', c) + ' '
                        results.append(lnk)
            #ordenamos
            if results.__len__() == 0:
                return None

            results = sorted(results, key=attrgetter('value'), reverse=True)
            i = 0
            for metaLnk in results:
                i += 1
                metaLnk.rank = i
            return results