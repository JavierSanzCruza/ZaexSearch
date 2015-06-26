from ZaexEvaluation.Metrics.metric import Metric
import math
__author__ = 'javier'

##
# @package ZaexEvaluation.Metrics.nDCGAtK
# Definition for class that calculates nDCG at K metric
# @author Javier Sanz-Cruzado Puig

###
# Class that calculates the Negative Discounted Cumulative Gain At K metric
class NDCGAtK(Metric):

    ## Constructor
    # @param k Number of results to study
    def __init__(self, k):
        self.k = k

    def calculate(self, results, dictClicks):
        if results is None or results.__len__() == 0 or dictClicks is None or dictClicks.__len__() == 0:
            return 0
        if self.k <= 0:
            return 0

        dcg = 0
        counter = 0

        idcg = 0
        m = min(self.k, dictClicks.__len__())
        for i in range(1, m+1):
            idcg += 1.0/math.log(i + 1, 2)

        for res in results:
            if counter >= self.k:
                break
            counter = counter + 1
            if (res in dictClicks):
                dcg += 1.0/math.log(res.rank + 1, 2)

        return (dcg + 0.0)/(idcg + 0.0)