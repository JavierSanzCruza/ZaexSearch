##
# @package TFGSearch.Diversity
# Package that contains methods and classes for diversifying results


##
# @package TFGSearch.Diversity.diversityMatrix
# Class that calculates the distances between documents in a ranking
# @author Javier Sanz-Cruzado Puig

from TFGSearch.Indexing.freqVector import FreqVector

__author__ = 'javier'


from TFGSearch.Indexing.indexer import Indexer
from TFGSearch.Diversity.docDistance import DocDistance

###
# Class for calculating the distance between several documents
class DiversityMatrix:

    @staticmethod
    ##
    # Obtains the distance matrix
    # @param previousRanking old Ranking
    # @param lambd Coefficient for the diversity formula
    # @return the matrix
    def diversityMatrix(previousRanking, route):
        if previousRanking is None or previousRanking.__len__() == 0:
            return None

        freqDict = {}
        ls = []
        exclude = 0
        dictText = {}
        for lnk in previousRanking:
            try:
                text = Indexer.readURLText(lnk.url)
            except Exception:
                text = ""

            dictText[lnk.resultID] = text

        #Index documents
        Indexer.createIndexStopwords(dictText, route, True)
        listVectors = Indexer.getTermVectors(route)

        numDocs = listVectors.__len__()
        matrix = []

        for i in range(numDocs):
            for j in range(i+1, numDocs):
                if listVectors[i][1] != 0 and listVectors[j][1] != 0 :
                    sym = listVectors[i][0].innerProduct(listVectors[j][0]) / (listVectors[i][1]*listVectors[j][1])
                else:
                    sym = 0.0
                d = DocDistance(i+1, j+1, sym)
                matrix.append(d)

        return matrix