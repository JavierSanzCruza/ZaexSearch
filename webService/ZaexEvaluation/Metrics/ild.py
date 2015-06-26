##
# @package ZaexEvaluation.Metrics.ild
# Definition for class that calculates EILD metric
# @author Javier Sanz-Cruzado Puig
from ZaexEvaluation.Metrics.metric import Metric

__author__ = 'javier'

from TFGSearch.Diversity.diversityMatrix import *

###
# Class to calculate Expected Intra List Dissimilarity (EILD)
class ILD(Metric):
    ###
    # Calculates and stores in the database the mean ILD of a evaluation ranker
    # @param documents List of documents
    # @param ranker Evaluation ranker
    # @param indexroute Route of the index to be created
    @staticmethod
    def calculateILD(documents, indexroute, evalranker):
        if documents is None or documents.__len__() < 2:
            result = 0.0
        else:
            #DIVERSITY
            matrix = DiversityMatrix.diversityMatrix(documents, indexroute)
            result = 0.0
            for doc in matrix:
                result += 1.0 - doc.distance
            result = result / matrix.__len__()

        result = (evalranker.ild * evalranker.numSearches + result)/(evalranker.numSearches + 1.0)
        evalranker.ild = result
        evalranker.numSearches += 1
        evalranker.save()

    ###
    # Do not use
    def calculate(self, results, dictClicks):
        return 0.0