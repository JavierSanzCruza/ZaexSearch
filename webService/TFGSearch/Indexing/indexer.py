##
# @package TFGSearch.Indexing
# Classes and methods for indexing and manipulating document vectors
# @author Javier Sanz-Cruzado Puig

##
# @package TFGSearch.Indexing.indexer
# Definition of a class that creates indexes and reads them
# @author Javier Sanz-Cruzado Puig

from operator import itemgetter
import sys, jcc, os,lucene, unittest
import cookielib, urllib2
from bs4 import BeautifulSoup
import math

from java.io import *
from org.apache.lucene.analysis import Analyzer
from org.apache.lucene.analysis.core import StopAnalyzer, StopFilter
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import *
from org.apache.lucene.index import *
from org.apache.lucene.index import IndexWriterConfig
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.search import *
from org.apache.lucene.store import *
from org.apache.lucene.util import BytesRef, Version, BytesRefIterator
from TFGSearch.Indexing.freqVector import *

__author__ = 'javier'

## Class that creates indexes and reads them, by using PyLucene
class Indexer:

    ##
    # Reads text from an URL
    # @param url Url to be read
    # @return text contained by the document with the previous url
    @staticmethod
    def readURLText(url):

        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}

        request = urllib2.Request(url, headers=hdr)
        response = opener.open(request)
        html = response.read()
        soup = BeautifulSoup(html)
        for script in soup(["script", "style"]):
            script.extract()
        text = soup.get_text()

        return text

    ##
    # Creates an index. No stopwords
    # @param texts Dictionary indexed by docID. Values are texts to analyze
    # @param route Route to the index
    # @param rebuild True if the index must be created again, false if not
    @staticmethod
    def createIndexNoStopwords(texts, route, rebuild):
        vm_env = lucene.getVMEnv()
        vm_env.attachCurrentThread()

        stopWords = []

        stopWordsSet = StopFilter.makeStopSet(Version.LUCENE_CURRENT, stopWords)
        analyzer = StopAnalyzer(Version.LUCENE_CURRENT, stopWordsSet)
        directory = SimpleFSDirectory(File(route))
        conf = IndexWriterConfig(Version.LUCENE_4_10_1, analyzer)
        if rebuild:
            conf.setOpenMode(IndexWriterConfig.OpenMode.CREATE)
        else:
            conf.setOpenMode(IndexWriterConfig.OpenMode.CREATE_OR_APPEND)

        iwriter = IndexWriter(directory, conf)

        for key in texts:
            doc = Document()
            doc.add(Field("docName", "doc", Field.Store.YES, Field.Index.NOT_ANALYZED))
            doc.add(Field("content", texts[key], Field.Store.YES, Field.Index.ANALYZED, Field.TermVector.YES))
            iwriter.addDocument(doc)

        iwriter.close()

    ##
    # Creates an index.Stopwords
    # @param texts Dictionary indexed by docID. Values are texts to analyze
    # @param route Route to the index
    # @param rebuild True if the index must be created again, false if not
    @staticmethod
    def createIndexStopwords(texts, route, rebuild):
        vm_env = lucene.getVMEnv()
        vm_env.attachCurrentThread()

        stopWords = ["a", "an", "and", "are", "as", "at", "be", "but", "by", "for", "if",
                     "no", "not", "of", "on", "or", "such", "that", "the", "their", "then",
                     "there", "these", "they", "this", "to", "was", "will", "with",
                     "el", "la", "lo","los", "las", "ante", "con", "sin", "que", "es", "de", "en", "por", "y", "los"]
        stopWordsSet = StopFilter.makeStopSet(Version.LUCENE_CURRENT, stopWords)
        analyzer = StopAnalyzer(Version.LUCENE_CURRENT, stopWordsSet)
        directory = SimpleFSDirectory(File(route))
        conf = IndexWriterConfig(Version.LUCENE_4_10_1, analyzer)
        if rebuild:
            conf.setOpenMode(IndexWriterConfig.OpenMode.CREATE)
        else:
            conf.setOpenMode(IndexWriterConfig.OpenMode.CREATE_OR_APPEND)

        iwriter = IndexWriter(directory, conf)

        for key in texts:
            doc = Document()
            doc.add(Field("docName", key.__str__(), Field.Store.YES, Field.Index.NOT_ANALYZED))
            doc.add(Field("content", texts[key], Field.Store.YES, Field.Index.ANALYZED, Field.TermVector.YES))
            iwriter.addDocument(doc)

        iwriter.close()

    ##
    # Gets the most frequent term from an index that does not appear in a given query
    # @param route Route of the index
    @staticmethod
    def getMostFrequentTermNoStopwords(route, query):
        vm_env = lucene.getVMEnv()
        vm_env.attachCurrentThread()
        stopWords = []

        stopWordsSet = StopFilter.makeStopSet(Version.LUCENE_CURRENT, stopWords)
        analyzer = StopAnalyzer(Version.LUCENE_CURRENT, stopWordsSet)
        directory = SimpleFSDirectory(File(route))

        ireader = IndexReader.open(directory)

        currentTerm = ""
        currentTermFreq = 0
        for doc in range(ireader.numDocs()):
            terms = ireader.getTermVector(doc, "content")
            if terms is not None:
                termsEnum = terms.iterator(None)
                for term in BytesRefIterator.cast_(termsEnum):
                    text = term.utf8ToString()
                    t = Term("content", term)
                    freq = ireader.totalTermFreq(t)
                    if freq > currentTermFreq and text not in query:
                        currentTerm = text
                        currentTermFreq = freq
        return currentTerm

    ##
    # Gets the most frequent term from an index that does not appear in a given query
    # @param route Route of the index
    @staticmethod
    def getMostFrequentTermStopwords(route, query):
        vm_env = lucene.getVMEnv()
        vm_env.attachCurrentThread()
        stopWords = ["a", "an", "and", "are", "as", "at", "be", "but", "by", "for", "if",
                     "no", "not", "more", "http", "html", "of", "on", "or", "such", "that", "the", "their", "then",
                     "there", "these", "they", "this", "to", "was", "will", "with",
                     "el", "la", "lo","los", "las", "ante", "con", "sin", "que", "es", "de", "en", "por", "y", "los"]

        stopWordsSet = StopFilter.makeStopSet(Version.LUCENE_CURRENT, stopWords)
        analyzer = StopAnalyzer(Version.LUCENE_CURRENT, stopWordsSet)
        directory = SimpleFSDirectory(File(route))

        ireader = IndexReader.open(directory)

        currentTerm = ""
        currentTermFreq = 0
        for doc in range(ireader.numDocs()):
            terms = ireader.getTermVector(doc, "content")
            if terms is not None:
                termsEnum = terms.iterator(None)
                for term in BytesRefIterator.cast_(termsEnum):
                    text = term.utf8ToString().encode('UTF-8')
                    t = Term("content", term)
                    freq = ireader.totalTermFreq(t)
                    if freq > currentTermFreq and text not in query:
                        currentTerm = text
                        currentTermFreq = freq

        return currentTerm

    ##
    # Reads freqVectors for each document in an index
    # @param route Vector route
    # @return A list of TFIDF frequency vectors (one for each document)
    @staticmethod
    def getTermVectors(route):
        vm_env = lucene.getVMEnv()
        vm_env.attachCurrentThread()
        stopWords = []
        stopWordsSet = StopFilter.makeStopSet(Version.LUCENE_CURRENT, stopWords)
        analyzer = StopAnalyzer(Version.LUCENE_CURRENT, stopWordsSet)
        directory = SimpleFSDirectory(File(route))

        ireader = IndexReader.open(directory)
        ls = []
        for doc in range(ireader.numDocs()):
            vector = FreqVector()
            vector.vector = []
            vector.freqs = []

            norm = 0.0
            terms = ireader.getTermVector(doc, "content")
            if(terms is not None):
                termsEnum = terms.iterator(None)
                for term in BytesRefIterator.cast_(termsEnum):
                    text = term.utf8ToString()
                    tf = 1 + math.log(termsEnum.totalTermFreq(), 2)
                    t = Term("content", term)
                    idf = math.log(ireader.numDocs() / ireader.docFreq(t))
                    vector.vector.append(text)
                    vector.freqs.append(tf*idf)
                    norm += (tf*idf)*(tf*idf)
                ls.append((vector, math.sqrt(norm)))
            else:
                ls.append((vector, 0))
        return ls


    ##
    # Given a list of links, builds an index for a given session using the urls provided
    # @param resultLinks List of results
    # @param session Search session
    # @param rebuild Indicates if the index must or not be rebuilt
    @staticmethod
    def createIndexFromUrls(resultLinks, session, rebuild):
        numFiles = min(10, resultLinks.__len__())

        urltexts = {}
        for i in range(numFiles):
            try:
                text = Indexer.readURLText(resultLinks[i].url)
            except:
                continue
            urltexts[resultLinks[i].resultID] = text

        route = 'res/index/' + session.clientID.clientID.__str__()
        Indexer.createIndexStopwords(urltexts, route, rebuild)

    ##
    # Given a list of links, builds an index for a given session using the provided snippets
    # @param resultLinks List of results
    # @param session Search session
    # @param rebuild Indicates if the index must or not be rebuilt
    @staticmethod
    def createIndexFromSnippets(resultLinks, session, rebuild):
        numFiles = resultLinks.__len__()

        snippettexts = {}
        for i in range(numFiles):
            snippettexts[resultLinks[i].resultID] = resultLinks[i].snippet

	route = 'res/index/' + session.clientID.clientID.__str__()
	d = os.path.dirname(route)
    	if not os.path.exists(d):
        	os.makedirs(d)

        Indexer.createIndexStopwords(snippettexts, route + '/' + session.sessionID.__str__(), rebuild)

    @staticmethod
    def getWord(query, session):

        word = Indexer.getMostFrequentTermStopwords('res/index/' + session.clientID.clientID.__str__() + '/' + session.sessionID.__str__(), query)

        return word
