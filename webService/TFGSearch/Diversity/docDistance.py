##
# @package TFGSearch.Diversity.diversityMatrix
# Definition of a class that represents the distance between a pair of documents
# @author Javier Sanz-Cruzado Puig

__author__ = 'javier'

## Class that represents the distance between a pair documents within a ranking
class DocDistance :
    ## Ranking of the first document
    doc1rank = 0
    ## Ranking of the second document
    doc2rank = 0
    ## Distance
    distance = 0.0

    ## Constructor
    def __init__(self, doc1rank, doc2rank, distance):
        self.doc1rank = doc1rank
        self.doc2rank = doc2rank
        self.distance = distance