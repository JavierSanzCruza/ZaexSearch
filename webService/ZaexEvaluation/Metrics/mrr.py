##
# @package ZaexEvaluation.Metrics.mrr
# Definition for class that calculates MRR metric
# @author Javier Sanz-Cruzado Puig

from ZaexEvaluation.Metrics.precissionAtK import *

###
# Class that calculates Mean Reciprocal Rank (MRR) metric
class MRR(Metric):

    def calculate(self, results, dictClicks):
        if results is None or results.__len__() == 0 or dictClicks is None or dictClicks.__len__() == 0:
            return 0

        mrr = 0.0

        for res in results:
            if (res in dictClicks):
                mrr = mrr + 1.0/(res.rank + 0.0)
                break
        return mrr