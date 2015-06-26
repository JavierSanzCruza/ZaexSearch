from TFGSearch.models import ClickedLink, EvaluatedRanker, SearchResult, InterleavingSources
from ZaexEvaluation.Metrics.metric import Metric

__author__ = 'javier'
##
# @package ZaexEvaluation.Metrics.mrr
# Definition for class that calculates R At K metric
# @author Javier Sanz-Cruzado Puig


###
# Calculates Recall at K metric
class RecallAtK(Metric):

    ### Constructor
    # @param k number of results to study
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

        return (prec + 0.0)/(dictClicks.__len__() + 0.0)