## @package ZaexEvaluation.Evaluation.probBranch
# Auxiliar classes for probability multileaved test evaluation

__author__ = 'javier'

###
# @brief Auxiliar class for probability multileaved test evaluation
class ProbBranch:

    clicks = {}
    data = {}
    p = 1.0
    ###
    # @brief Constructor for the class
    def __init__(self):
        clicks = {}
        data = {}
        p = 1.0

    ###
    # @brief Returns a list with the softmax evaluation for a list of results
    # @param ls list of search results
    # @returns A list with the evaluation of the softmax function for each result
    @staticmethod
    def softmax(ls, tau):
        sum = 0.0
        auxList = []
        for res in ls:
            sm = 1.0/(pow(res.rank, tau) + 0.0)
            sum += sm
            auxList.append(sm)

        softmaxList = [soft/ (sum + 0.0) for soft in auxList]
        return softmaxList

    ###
    # @brief clones the ProbBranch
    # @returns the cloned ProbBranch
    def clone(self):
        pb = ProbBranch()
        pb.clicks = self.clicks.copy()
        pb.data = self.data.copy()
        pb.p = self.p

        return pb

    ###
    # @brief Given a list of searchResults ordered by source and rank, initializes the dictionary data
    # @param data Dictionary of search results. The key is the ranker and the values are lists of search results
    def initData(self, data):
        for key in data.keys():
            aux = []
            for el in data[key]:
                aux.append(el)
            self.data[key] = aux

    ###
    # @brief Given a list of rankers, this function initializes the dictionary
    # @param rankers List of rankers. They will be the keys for the clicks dictionary
    def initClicks(self, rankers):
        for ranker in rankers:
            self.clicks[ranker] = 0



    ###
    # @brief Removes a searchResult for each list in data
    # @param searchResult search result to be removed
    def reduceData(self, searchResult):
        for key in self.data:
            self.data[key] = [res for res in self.data[key] if not res.resultID == searchResult.resultID]

    ###
    # @brief Recalculates the probability of the branch by multiplying the actual one by a factor
    # @param probability Factor to multiply by the probability
    def multiply(self, searchResult, ranker):
        ls = self.data[ranker]

        softm = ProbBranch.softmax(ls, 3)
        for i in range(ls.__len__()):
            if(ls[i].resultID == searchResult.resultID):
                self.p *= softm[i]
                break



    ###
    # @brief Adds a click to a ranker
    # @param index ID of the ranker
    def addClick(self, ranker):
        self.clicks[ranker] += 1

