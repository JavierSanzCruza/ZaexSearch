## @package ZaexEvaluation.Evaluation.probabilityABTest
# Probability multileaved test definition and methods

from ZaexEvaluation.Evaluation.abTest import ABTest
from ZaexEvaluation.Interleaving.probabilisticInterleaving import *
from TFGSearch.models import *
from ZaexEvaluation.Evaluation.probBranch import ProbBranch

### Class that implements multileaved evaluation by a probabilistic approach
class ProbabilityABTest(ABTest):

    ###
    # @brief Interleaves the results. Uses the Probabilistic Interleaving method
    # @param linkLists Lists of links (one for each ranker to evaluate)
    def interleaveResults(self, linkLists, search):
        probabilistic = ProbabilisticInterleaving()
        return probabilistic.doMetaSearch(linkLists, search)

    ###
    # @brief Obtains the expected number of clicks given a result list
    # @param search Search to evaluate
    # @param dictClicks List of clicks for the search
    # @returns A list with the expected list of clicks for each ranker in this search
    def expectedClicks(self, search, dictClicks):
        expectedClicks = {}

        for ranker in EvaluatedRanker.objects.all():
            expectedClicks[ranker] = 0

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

        pb = ProbBranch()
        pb.initClicks(EvaluatedRanker.objects.all())
        pb.initData(data)

        totalClicks = dictClicks.__len__()
        numClicks = 0
        listPB = []
        listPB.append(pb)
        for res in results:
            sources = InterleavingSources.objects.filter(result__exact = res)
            length = sources.__len__()
	    if length == 0:
		continue
            aux = []
            for prb in listPB:

                mustAddClick = (res in dictClicks)
                for i in range(1, length):
                    prb2 = prb.clone()
                    if mustAddClick:
			rnker = EvaluatedRanker.objects.filter(rankerID__exact = sources[i].ranker.rankerID)
                        prb2.addClick(rnker[0])
                    prb2.multiply(res, sources[i].ranker.name)
                    prb2.reduceData(res)
                    aux.append(prb2)

                if mustAddClick:
		    rnker = EvaluatedRanker.objects.filter(rankerID__exact = sources[0].ranker.rankerID)
                    prb.addClick(rnker[0])
                    numClicks += 1
                prb.multiply(res, sources[0].ranker.name)
                prb.reduceData(res)

            for prb in aux:
                listPB.append(prb)

            if numClicks == totalClicks:
                break
        probL = sum([prb.p for prb in listPB])


        #Calculating the expected number of clicks
        for prb in listPB:
            for ranker in EvaluatedRanker.objects.all():
                expectedClicks[ranker] += prb.clicks[ranker]*prb.p/probL
        return expectedClicks;





    ###
    # @brief Evaluates different rankings by counting the total expected number of clicks for a ranker
    # @returns The evaluation of the systems
    def evaluateClicks(self):
        ## We take the clicks marked for evaluation
        clicks = ClickedLink.objects.filter(evaluation__exact = True)
        searchResults = [click.searchResult for click in clicks]

        for ranker in EvaluatedRanker.objects.all():
            ranker.evaluation = 0
            ranker.save()

        #Initializing the structures for the evaluation
        rankers = EvaluatedRanker.objects.all()
        expectedClickDict = {}
        for ranker in rankers:
            expectedClickDict[ranker] = 0

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
            expectedClicksSearch = self.expectedClicks(search, clickList)

            for ranker in expectedClicksSearch:
                expectedClickDict[ranker] += expectedClicksSearch[ranker]

        evaldict = {}
        for ranker in EvaluatedRanker.objects.all():
            ranker.evaluation = expectedClickDict[ranker]
            ranker.save()
            evaldict[ranker.name] = expectedClickDict[ranker]

        return evaldict

    ###
    # @brief Evaluates different rankings by calculating the number of queries won by that ranker
    def evaluateQueries(self):
        ## We take every clicked link marked for evaluation
        clicks = ClickedLink.objects.filter(evaluation__exact = True)
        searchResults = [click.searchResult for click in clicks]

        ## Initializing the temporl dictionary for evaluation
        tempEval = {}

        for ranker in EvaluatedRanker.objects.all():
            ranker.evaluation = 0
            ranker.save()
            tempEval[ranker.rankerID] = 0

        ## Now, we classify each click by search
        searchIDs = [result.searchID for result in searchResults]
        dict = {}
        for search in searchIDs:
            dict[search]=[]

        for result in searchResults:
            dict[result.searchID].append(result)

        ## Una vez hecho esto, en dict, tenemos separadas todas las busquedas
        for search in dict:
            if dict[search] is None or dict[search].__len__() == 0:
                continue

            expectedClicksSearch = self.expectedClicks(search, dict[search])
           
            right = 0
            leadRanker = []
            for ranker in expectedClicksSearch:
                if expectedClicksSearch[ranker] > right:
                    right = expectedClicksSearch[ranker]
                    leadRanker = []
                    leadRanker.append(ranker)
                elif expectedClicksSearch[ranker] == right:
                    leadRanker.append(ranker)
            for rnk in leadRanker:
            #Guardamos el resultado en la base de datos
                tempEval[rnk.rankerID]  += 1

        evaldict = {}
        for ranker in EvaluatedRanker.objects.all():
            ranker.evaluation = tempEval[ranker.rankerID]
            ranker.save()
            evaldict[ranker.name] = tempEval[ranker.rankerID]

        return evaldict




