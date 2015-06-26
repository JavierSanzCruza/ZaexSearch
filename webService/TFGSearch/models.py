## @package TFGSearch.models
# Descriptions for the models in the database

from django.db import models
from django.utils import timezone

## Stores information about client. A client will be stored for each pair IP/User Agent
class Client(models.Model):
    ## Primary key
    clientID = models.AutoField(primary_key=True)
    ## client IP for the client who submits a query
    clientIP = models.CharField(max_length=40)
    ## user Agent of the client who submits a query
    userAgent = models.CharField(max_length=190)

    ## To string
    def __unicode__(self):
        return u'%d' %(self.clientID)

    ## Returns an existent client, or, in case it does not exists, returns a new one
    # @param cls client class
    # @param clientIP client IP
    # @param userAgent client userAgent
    # @returns an existent client, or, in case it does not exists, returns a new one. None if error
    def get_or_create(cls, clientIP, userAgent):
        clientes = Client.objects.filter(clientIP__exact = clientIP).filter(userAgent__exact = userAgent)

        if(not clientes):
            cli = Client()
            cli.clientIP = clientIP
            cli.userAgent = userAgent
            cli.save()
        elif clientes.count() > 1:
            cli = None
        else:
            cli = clientes.first() #The client is unique

        return cli

    ## Class restrictions
    class Meta:
        ## Uniqueness restrictions. Only a client for pair IP/User Agent
        unique_together = (('clientIP', 'userAgent'))
        ## Database table name
        db_table = 'client'

## Stores information about the sessions for each client
class Session(models.Model):
    ## Primary key
    sessionID = models.AutoField(primary_key=True)
    ## Client (Foreign key)
    clientID = models.ForeignKey(Client)
    ## Timestamp of the creation of the session
    timestamp = models.DateTimeField(default=timezone.now())
    ## Indicates if the session is active
    active = models.BooleanField(default = True)

    ## To string
    def __unicode__(self):
        return u'%d' %(self.sessionID)

    ## Gets the active sessions for a client
    # @param client Session client
    # @param userAgent client userAgent
    # @returns A list of active sessions in case they exist, None if not
    def get_active(self, cli):
        sesiones = Session.objects.filter(clientID__exact = cli.clientID).filter(active = True)
        ses = None
        if(not sesiones):
           return None
        return sesiones

    ## Restrictions and properties
    class Meta:
        ## Database name
        db_table = 'session'


## Stores information about the queries submitted
class Search(models.Model):
    ## Primary key
    searchID = models.AutoField(primary_key=True)
    ## Session to which the search belongs
    sessionID = models.ForeignKey(Session)
    ## Creation timestamp
    timestamp = models.DateTimeField(default=timezone.now())
    ## Query text
    query = models.TextField()
    ## Number of results
    numResults = models.PositiveIntegerField(default = 0)

    ## To String
    def __unicode__(self):
        return u'%d' %(self.searchID)

    ## Creation
    def create(self, ses, query):
        self.sessionID = ses
        self.query = query
        self.numResults = 0
        self.timestamp = timezone.now()
        self.save()
        return self

    ## Restrictions and properties
    class Meta:
        ## Database name
        db_table = 'search'

## Stores information about the aggregated search systems
class Ranker(models.Model):
    ## Primary key
    rankerID = models.AutoField(primary_key=True)
    ## Search system name
    name = models.TextField()

    ## To string
    def __unicode__(self):
        return u'%s'%(self.name)

    ## Restrictions and properties
    class Meta:
        ## Database name
        db_table = 'ranker'

## Stores information about the aggregated search systems for evaluation
class EvaluatedRanker(models.Model):
    ## Primary key for the table
    rankerID = models.AutoField(primary_key=True)
    ## Name of the evaluated ranker
    name = models.TextField()
    ## Evaluation
    evaluation = models.FloatField()
    ## ILD Evaluation
    ild = models.FloatField()
    ## Number of queries evaluated
    numSearches = models.PositiveIntegerField(default=0)

    ## To string
    def __unicode__(self):
        return u'%s'%(self.name)

    ## Restrictions and properties
    class Meta:
        ## Database name
        db_table = 'evaluatedRanker'

## Stores information about the retrieved documents
class SearchResult(models.Model):
    ## Primary key
    resultID = models.AutoField(primary_key=True)
    ## Search
    searchID = models.ForeignKey(Search)
    ## Title of the document
    title = models.TextField()
    ## Ranking of the document in the search
    rank = models.PositiveIntegerField()
    ## URL
    url = models.TextField()
    ## Brief description
    snippet = models.TextField()
    ## Metasearch value
    value = models.FloatField()
    ## Document sources
    source = models.ManyToManyField(Ranker, through='Sources', symmetrical=False, related_name='searchSource')
    ## Evaluation document sources
    interleavingSource = models.ManyToManyField(EvaluatedRanker, through='InterleavingSources', symmetrical=False, related_name='interleaveSource')

    ## To String
    def __unicode__(self):
        return u'%d' %(self.resultID)

    ## Adds a source to the result
    # @param rankerName Name of the ranker
    # @param rank Rank of the result in that ranker list
    def addSource(self, rankerName, rank):
        rnks = Ranker.objects.filter(name__exact = rankerName)
        if rnks is None or rnks.__len__() == 0:
            ranker = Ranker()
            ranker.name = rankerName
            ranker.evaluation = 0
            ranker.save()
        else:
            ranker = rnks[0]
        self.save()

        ## Comprobamos si ya existe
        srcs = Sources.objects.filter(result__exact = self).filter(ranker__exact = ranker)
        if srcs is None or srcs.__len__() == 0:
            src = Sources(ranker=ranker, result=self, rank=rank)
            src.save()

    ## Adds an evaluation source to the result
    # @param rankerName Name of the ranker
    # @param rank Rank of the result in that ranker list
    def addInterleavingSource(self, rankerName, rank):
        rnks = EvaluatedRanker.objects.filter(name__exact = rankerName)
        if rnks is None or rnks.__len__() == 0:
            ranker = EvaluatedRanker()
            ranker.name = rankerName
            ranker.evaluation = 0
            ranker.ild = 0
            ranker.save()
        else:
            ranker = rnks[0]
        self.save()
        srcs = InterleavingSources.objects.filter(result__exact=self).filter(ranker__exact = ranker)
        if srcs is None or srcs.__len__() == 0:
            src = InterleavingSources(ranker=ranker, result=self, rank=rank)
            src.save()

    ## Restrictions and properties
    class Meta:
        ## Database Name
        db_table = 'searchResult'

## Sources for each result
class Sources(models.Model):
    ## Ranker
    ranker = models.ForeignKey(Ranker)
    ## Search result
    result = models.ForeignKey(SearchResult)
    ## Position for the result in the ranker ranking
    rank = models.PositiveIntegerField()

    class Meta:
        ##Nombre de la tabla en la base de datos
        db_table = 'source'

## Sources for each result in a evaluated ranker
class InterleavingSources(models.Model):
    ## Evaluated ranker
    ranker = models.ForeignKey(EvaluatedRanker)
    ## Search result
    result = models.ForeignKey(SearchResult)
    ## Original position of the result
    rank = models.PositiveIntegerField()

    class Meta:
        db_table = 'interleavingSource'

## Stores information about the links clicked during a session
class ClickedLink(models.Model):
    ## Session
    sessionID = models.ForeignKey(Session)
    ## Search result (unique)
    searchResult = models.ForeignKey(SearchResult)
    ## Result Title
    title = models.TextField()
    ## Result URL
    url = models.TextField()
    ## Brief description
    snippet = models.TextField()
    ## Indicates if this item is used or not for evaluation
    evaluation = models.BooleanField()

    ## To String
    def __unicode__(self):
        return u'%s' %(self.url)

    ## Restrictions and properties
    class Meta:
        ## Database name
        db_table = 'clickedLink'
	unique_together = (('sessionID', 'searchResult'))

## Stores information about explicit sessions
class MetaSession(models.Model):
    ## Primary key
    metaSessionID = models.AutoField(primary_key=True)
    ## Client
    clientID = models.ForeignKey(Client)
    ## Creation timestamp
    timestamp = models.DateTimeField(default=timezone.now())
    ## Name of the metasession
    name = models.TextField(blank=True)
    ## Indicates if the session has or not been closed
    closed = models.BooleanField(default=False)

    ## To string
    def __unicode__(self):
        return u'%d' %(self.metaSessionID)

    ## Closes a session
    def close(self):
        self.closed = True
        self.save()

    ## Opens a session
    # @param name Name of the session
    # @param cli Client
    @staticmethod
    def open(name, cli):
        metasessions = MetaSession.objects.filter(clientID__exact = cli).filter(name__exact = name).order_by("timestamp")
        if not metasessions:
            return None
        else:
            metaSes = metasessions.last()
            metaSes.closed = False
            metaSes.save()
            return metaSes

    ## Returns an existent metasession, or, in case it does not exists, returns a new one
    # @param cli client class
    # @returns an existent metasession, or, in case it does not exists, returns a new one
    @staticmethod
    def get_or_create(cli):
        #search for the active metasession (it should be only one)
        metasessions = MetaSession.objects.filter(clientID__exact = cli).filter(closed = False)
        ses = None
        if(not metasessions):
            ses = MetaSession()
            ses.clientID = cli
            ses.closed = False
            ses.name = ""
            ses.timestamp = timezone.now()
            ses.save()
        else:
            ses = metasessions.first()
        return ses

    ## Adds a result to the metasession
    # @param self the metasession
    # @param res Search result to save
    # @param search Search to which res belongs
    def addResult(self, res, search):
        ls = SavedLink.objects.filter(metaSessionID__exact = self).filter(url__exact = res.url).filter(searchResult__exact = res)

        #STEP 8: Save the result
        if(not ls):
            saved = SavedLink()
            saved.metaSessionID = self
            saved.searchResult = res
            saved.title = res.title
            saved.url = res.url
            saved.snippet = res.snippet
            saved.query = search.query
            saved.rank = res.rank

            saved.save()

    ## Deletes a result from the metasession
    # @param self the metasession
    # @param query Query of the result
    # @param rank Rank of the result
    def deleteResult(self,query, rank):
        ls = SavedLink.objects.filter(metaSessionID__exact = self)
        ls = ls.filter(query__exact = query).filter(rank__exact = rank);

        #PASO 8: Delete the result
        if(ls.__len__() > 0):
            for lnk in ls:
                lnk.delete()


    def saveSession(self, metaName):
        self.name = metaName
        self.save()
    ##Properties and restrictions
    class Meta:
        db_table = "metaSession"

##
class SavedLink(models.Model):
    metaSessionID = models.ForeignKey(MetaSession)
    searchResult = models.ForeignKey(SearchResult)
    title = models.TextField()
    url = models.TextField()
    snippet = models.TextField()
    query = models.TextField()
    rank = models.PositiveIntegerField()

    def __unicode__(self):
        return u'%s' %(self.url)

    class Meta:
        db_table = "savedLink"
	unique_together = (("metaSessionID", "searchResult"))




