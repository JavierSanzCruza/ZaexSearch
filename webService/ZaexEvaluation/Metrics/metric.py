##
# @package ZaexEvaluation.Metrics
# Package that contains definitions for classes and methods for evaluation of different rankers by using different
# metrics
# @author Javier Sanz-Cruzado Puig

##
# @package ZaexEvaluation.Metrics.metric
# Definition for a metric abstract class
# @author Javier Sanz-Cruzado Puig
from TFGSearch.models import ClickedLink, EvaluatedRanker, SearchResult, InterleavingSources

__author__ = 'javier'




from abc import ABCMeta, abstractmethod

###
# Abstract class definition for a metric
class Metric:
    __metaclass__ = ABCMeta

    ###
    # Evaluates the different sources by using the corresponding metric
    # @returns the evaluated rankers
    def evaluateMetric(self):
        ## We take the clicks marked for evaluation
        clicks = ClickedLink.objects.filter(evaluation__exact = True)
        searchResults = [click.searchResult for click in clicks]

        for ranker in EvaluatedRanker.objects.all():
            ranker.evaluation = 0
            ranker.save()

        #Initializing the structures for the evaluation
        rankers = EvaluatedRanker.objects.all()
        metric = {}
        for ranker in rankers:
            metric[ranker] = 0

        # We classify them by search
        searchIDs = [result.searchID for result in searchResults]
        dict = {}
        for search in searchIDs:
            dict[search]=[]

        for result in searchResults:
            dict[result.searchID].append(result)

        # Now, we have the different searches apart from each other in dict
        for search in dict:
            if dict[search] is None or dict[search].__len__() == 0:
                continue

            clickList = dict[search]
            metricDict = self.calculateSearch(search, clickList)

            for ranker in metric:
                metric[ranker] += metricDict[ranker]

        evaldict = {}
        for ranker in EvaluatedRanker.objects.all():
            if ranker.numSearches > 0:
                evaldict[ranker.name] = metric[ranker]/(ranker.numSearches + 0.0)
                ranker.evaluation = metric[ranker]/(ranker.numSearches + 0.0)
            else:
                evaldict[ranker.name] = 0
                ranker.evaluation = 0
            ranker.save()


        return evaldict

    ###
    # Calculates the values for the metric for a given search
    # @param self the metric
    # @param search the search to evaluate
    # @param clickList List of relevant documents for the given search
    # @returns a dictionary containing the metric value for each ranker
    def calculateSearch(self, search, clickList):
        metric = {}

        for ranker in EvaluatedRanker.objects.all():
            metric[ranker] = 0

        #STEP 1: We obtain the several lists of links coming from each source
        results = SearchResult.objects.filter(searchID__exact = search).order_by('rank')
        sources = InterleavingSources.objects.filter(result__in = results).order_by('ranker', 'rank')
        data = {}
        for i in range(EvaluatedRanker.objects.all().__len__()):
            ls = []
            rankers = EvaluatedRanker.objects.filter(rankerID__exact = (i+1))
            name = rankers.first().name
            for source in sources:
                if source.ranker.rankerID == (i+1):
                    result = SearchResult.objects.filter(resultID__exact = source.result.resultID).first()
                    result.rank = source.rank
                    ls.append(result)
            data[name] = ls

        #STEP 2: For each ranker, we calculate P@K
        for ranker in EvaluatedRanker.objects.all():
            metric[ranker] = metric[ranker] + self.calculate(data[ranker.name], clickList)

        return metric;

    ###
    # Calculates the metric value for a ranking
    # @param self the metric
    # @param results the results of the search engine
    # @param clickList List of relevant documents
    # @returns the metric value
    @abstractmethod
    def calculate(self, results, dictClicks): pass
