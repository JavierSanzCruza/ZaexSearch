##
# @package ZaexEvaluation.Metrics.map
# Definition for class that calculates MAP metric
# @author Javier Sanz-Cruzado Puig

from ZaexEvaluation.Metrics.precissionAtK import *

###
# Class that calculates Mean Average Precission (MAP) metric
class MAP(Metric):

    def calculate(self, results, dictClicks):
        if results is None or results.__len__() == 0 or dictClicks is None or dictClicks.__len__() == 0:
            return 0

        map = 0.0
        for res in results:
            if (res in dictClicks):
                patK = PrecissionAtK(res.rank)
                map = map + patK.calculate(results, dictClicks)
        return map/(dictClicks.__len__() + 0.0)
