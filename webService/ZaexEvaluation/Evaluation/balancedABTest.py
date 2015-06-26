## @package ZaexEvaluation.Evaluation.balancedABTest
# Balanced test class definition

from ZaexEvaluation.Evaluation.abTest import ABTest
from ZaexEvaluation.Interleaving.balancedInterleaving import *
from TFGSearch.models import *


###
# Class that executes multileaved tests by using Balanced Method
class BalancedABTest(ABTest):

    def interleaveResults(self, linkLists):
        balanced = BalancedInterleaving()
        return balanced.doMetaSearch(linkLists)

    def evaluateClicks(self):
        ## Take evaluation clicks
        clicks = ClickedLink.objects.filter(evaluation__exact = True)
        searchResults = [click.searchResult for click in clicks]

        for ranker in Ranker.objects.all():
            ranker.evaluation = 0
            ranker.save()
        ## Classify each click in function of the search
        searchIDs = [result.searchID for result in searchResults]
        dict = {}
        for search in searchIDs:
            dict[search]=[]

        for result in searchResults:
            dict[result.searchID].append(result)

        ## In dict, we have each search apart
        for search in dict:
            ## Calculating k
            resMax = None
            max_rank = -1
            for res in dict[search]:
                if res.rank > max_rank:
                    resMax = res
                    max_rank = res.rank

            listSources = InterleavingSources.objects.filter(result__exact = resMax)
            k = min([source.rank for source in listSources])

            ## Evaluating
            for res in dict[search]:
                listSources = Sources.objects.filter(result__exact = res)
                for source in listSources:
                    if source.rank <= k:
                        source.ranker.evaluation += 1
                        source.ranker.save()

        evaluation = EvaluatedRanker.objects.all()
        return evaluation

    def evaluateQueries(self):
    ## Take evaluation clicks
        clicks = ClickedLink.objects.filter(evaluation__exact = True)
        searchResults = [click.searchResult for click in clicks]

        ## Initialize the temporal dictionary for evaluation
        tempEval = {}

        for ranker in EvaluatedRanker.objects.all():
            ranker.evaluation = 0
            ranker.save()
            tempEval[ranker.rankerID] = 0

        ## Classify each clicked Link in function of the search
        searchIDs = [result.searchID for result in searchResults]
        dict = {}
        for search in searchIDs:
            dict[search]=[]

        for result in searchResults:
            dict[result.searchID].append(result)



        ## We have now the searches apart
        for search in dict:
            if dict[search] is None or dict[search].__len__() == 0:
                continue

            for ranker in tempEval:
                tempEval[ranker] = 0
            ## Calculating k
            resMax = None
            max_rank = -1
            for res in dict[search]:
                if res.rank > max_rank:
                    resMax = res
                    max_rank = res.rank

            listSources = InterleavingSources.objects.filter(result__exact = resMax)
            k = min([source.rank for source in listSources])

            ## Evaluating
            for res in dict[search]:
                listSources = Sources.objects.filter(result__exact = res)
                for source in listSources:
                    if source.rank <= k:
                        tempEval[source.ranker.rankerID] += 1

            ## One we have stored in the temporal dictionary every data from the query, we select the
            # searcher with more hits

            right = 0
            leadRanker = -1
            for ranker in tempEval:
                if tempEval[ranker] > right:
                    right = tempEval[ranker]
                    leadRanker = ranker
            #Guardamos el resultado en la base de datos
            rnk = EvaluatedRanker.objects.filter(rankerID__exact = leadRanker).first()
            rnk.evaluation += 1
            rnk.save()


        evaluation = EvaluatedRanker.objects.all()
        return evaluation



