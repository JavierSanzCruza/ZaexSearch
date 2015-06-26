from django.test import TestCase

# Create your tests here.
from TFGSearch.models import *
from TFGSearch.Metasearch.rankSimMetasearcher import RankSimMetasearcher
from TFGSearch.SessionDetection.searchPatternDetector import *

# Tests de metabusqueda
class RankSimMetaSearchTests(TestCase):

    ####### FUNCIONES AUXILIARES #######
    def createClientSession(self):
        cliente = Client()
        cliente.clientIP = '1.1.1.1.'
        cliente.userAgent = 'Firefox'
        cliente.save()

        sesion = Session()
        sesion.clientID = cliente
        sesion.save()

        search = Search()
        search.sessionID = sesion
        search.query = 'bocata'
        search.numResults = 1
        search.save()

        return search

    def createLinkOne(self, search):

        lnk = SearchResult()
        lnk.url = 'as.com'
        lnk.rank = 1
        lnk.descr = 'descr'
        lnk.title = 'AS'
        lnk.searchID = search

        return lnk

    def createLinkTwo(self, search):

            lnk = SearchResult()
            lnk.url = 'elpais.com'
            lnk.rank = 2
            lnk.descr = 'descr'
            lnk.title = 'EL PAIS'
            lnk.searchID = search

            return lnk

    ####### TESTS #######################
    def test_metaSearchNone(self):
        lista = None

        res = RankSimMetasearcher().doMetaSearch(lista)
        self.assertIsNone(res)

    def test_metaSearchEmptyList(self):
        lista = list()

        res = RankSimMetasearcher().doMetaSearch(lista)
        self.assertIsNone(res)


    def test_metaSearchEmptyLists(self):

        lista = [[],[],[]]
        res = RankSimMetasearcher().doMetaSearch(lista)

        self.assertIsNone(res)

    def test_metaSearchOneLinkOneList(self):
        search = self.createClientSession()

        lnk = self.createLinkOne(search)

        lista = [[lnk]]

        res = RankSimMetasearcher().doMetaSearch(lista)

        self.assertEqual(res.__len__(), 1)

        self.assertEqual(res[0].value, 1.0)

    def test_metaSearchTwoLinksOneList(self):

        search = self.createClientSession()
        lnk = self.createLinkOne(search)

        lnk2 = self.createLinkTwo(search)

        lista = [[lnk, lnk2]]

        res = RankSimMetasearcher().doMetaSearch(lista)

        self.assertEqual(res[0], lnk)
        self.assertEqual(res[1], lnk2)

    def test_metaSearchTwoLinksTwoLists(self):

        search = self.createClientSession()
        lnk = self.createLinkOne(search)

        lnk2 = self.createLinkTwo(search)
        lnk2.rank = 1
        lista = [[lnk], [lnk2]]

        res = RankSimMetasearcher().doMetaSearch(lista)

        self.assertEqual(res[0].value, 0.5)
        self.assertEqual(res[1].value, 0.5)

    def test_metaSearchOneLinkTwoLists(self):
        search = self.createClientSession()

        lnk = self.createLinkOne(search)

        lista = [[lnk],[lnk]]

        res = RankSimMetasearcher().doMetaSearch(lista)

        self.assertEqual(res.__len__(), 1)

        self.assertEqual(res[0].value, 1.0)

    def test_metaSearchTwoLinkTwoListsOneRepeated(self):
        search = self.createClientSession()
        lnk = self.createLinkOne(search)

        lnk2 = self.createLinkTwo(search)
        lnk2.rank = 1
        lista = [[lnk], [lnk2, lnk]]

        res = RankSimMetasearcher().doMetaSearch(lista)

        self.assertEqual(res[0], lnk)
        self.assertEqual(res[1], lnk2)

class SearchPatternDetectorTest (TestCase):
    def test_repetition1(self):
        query1 = "Kingdom Hearts"
        res = SearchPatternDetector.searchPatternDetection(query1, query1)
        self.assertEqual(SearchPattern.get("REPETITION"), res)

    def test_repetition2(self):
        query1 = "Kingdom  Hearts       "
        query2 = "Kingdom Hearts"
        res = SearchPatternDetector.searchPatternDetection(query1, query2)
        self.assertEqual(SearchPattern.get("REPETITION"), res)

    def test_repetition3(self):
        query1 = "Kingdom  Hearts       "
        query2 = "kingdom hearts"
        res = SearchPatternDetector.searchPatternDetection(query1, query2)
        self.assertEqual(SearchPattern.get("REPETITION"), res)

    def test_specialisation1(self):
        query1 = "Kingdom Hearts"
        query2 = "Kingdom Hearts Birth By Sleep"
        res = SearchPatternDetector.searchPatternDetection(query1, query2)
        self.assertEqual(SearchPattern.get("SPECIALISATION"), res)

    def test_specialisation2(self):
        query1 = "Kingdom Hearts"
        query2 = "Birth By Sleep Kingdom Hearts"
        res = SearchPatternDetector.searchPatternDetection(query1, query2)
        self.assertEqual(SearchPattern.get("SPECIALISATION"), res)

    def test_generalisation1(self):
        query1 = "The Amazing Spiderman"
        query2 = "Spiderman"
        res = SearchPatternDetector.searchPatternDetection(query1, query2)
        self.assertEqual(SearchPattern.get("GENERALISATION"), res)

    def test_reformulation1(self):
        query1 = "The Avengers vs XMen"
        query2 = "The Avengers vs Spiderman"
        res = SearchPatternDetector.searchPatternDetection(query1, query2)
        self.assertEqual(SearchPattern.get("REFORMULATION"), res)

    def test_reformulation2(self):
        query1 = "The Avengers vs the XMen"
        query2 = "The Avengers fight the XMen"
        res = SearchPatternDetector.searchPatternDetection(query1, query2)
        self.assertEqual(SearchPattern.get("REFORMULATION"), res)

    def test_reformulation3(self):
        query1 = "The Avengers vs the XMen"
        query2 = "Fortunately, the Avengers Fightthe XMen in Mars"
        res = SearchPatternDetector.searchPatternDetection(query1, query2)
        self.assertEqual(SearchPattern.get("REFORMULATION"), res)

    def test_reordering(self):
        query1 = "Jim Carrey Saturday Night Live"
        query2 = "Saturday Night Live Jim Carrey"
        res = SearchPatternDetector.searchPatternDetection(query1, query2)
        self.assertEqual(SearchPattern.get("REORDERING"), res)

    def test_new1(self):
        query1 = "Football"
        query2 = "Basketball"
        res = SearchPatternDetector.searchPatternDetection(query1, query2)
        self.assertEqual(SearchPattern.get("NEW"), res)

    def test_new2(self):
        query1 = "Monte Ro"
        query2 = "Montero"
        res = SearchPatternDetector.searchPatternDetection(query1, query2)
        self.assertEqual(SearchPattern.get("NEW"), res)