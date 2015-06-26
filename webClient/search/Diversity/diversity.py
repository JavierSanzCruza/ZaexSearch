__author__ = 'javier'

class Diversity:

    @staticmethod
    def diversityRanking(distanceMatrix, linkLists, lamb):
        definitiveRanking = []

        definitiveRanking.append(1)

        for i in range(linkLists.__len__() - 1):
            max = -1000
            rank = -1
            for j in range(linkLists.__len__()):
                if(definitiveRanking.__contains__(j+1)):
                    continue
                value = (1-lamb)*linkLists[j].value
                sum = 0.0
                for k in definitiveRanking:
                    sum += distanceMatrix[j][k-1]
                value -= lamb*sum/(definitiveRanking.__len__() + 0.0)
                if value > max:
                    max = value
                    rank = j+1

            definitiveRanking.append(rank)

        return definitiveRanking


    @staticmethod
    def calculateILD(distanceMatrix):
        ild = 0.0

        length = distanceMatrix.__len__()

        for i in range(length):
            for j in range(i):
                ild += 1-distanceMatrix[i][j]

        ild = 2*ild/(length*(length - 1))
        return ild