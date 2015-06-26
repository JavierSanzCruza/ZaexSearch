from TFGSearch.models import ClickedLink, EvaluatedRanker, SearchResult, InterleavingSources
from ZaexEvaluation.Metrics.metric import Metric

__author__ = 'javier'
##
# @package ZaexEvaluation.Metrics.precissionAtK
# Definition for class that calculates P At K metric
# @author Javier Sanz-Cruzado Puig

##
# Class that calculates Precission at K metric
class PrecissionAtK(Metric):

    ## Constructor
    # @param k Number of results to study
    def __init__(self, k):
        self.k = k

    def calculate(self, results, dictClicks):
        if results is None or results.__len__() == 0 or dictClicks is None or dictClicks.__len__() == 0:
            return 0
        if self.k <= 0:
            return 0

        prec = 0
        counter = 0
        for res in results:
            if counter >= self.k:
                break
            counter = counter + 1
            if (res in dictClicks):
                prec = prec + 1

        return (prec + 0.0)/(self.k + 0.0)
