from django.db import models
from django.utils import timezone

# Create your models here.


## Stores information about the searches of each client
class Search(models.Model):
    ## Primary key
    searchID = models.AutoField(primary_key=True)
    ## query
    query = models.TextField()
    ## number of results
    numResults = models.PositiveIntegerField(default = 0)

    ## Indica como se muestra la clase Search en una cadena
    def __unicode__(self):
        return u'%d' %(self.searchID)

    ## Restricciones y propiedades de la clase
    class Meta:
        ## Nombre de la tabla en la base de datos
        db_table = 'search'

class Ranker(models.Model):
    ## Primary key
    rankerID = models.AutoField(primary_key=True)
    ## Name
    name = models.TextField()

    def __unicode__(self):
        return u'%s'%(self.name)

    class Meta:
        db_table = 'ranker'

class SearchResult(models.Model):
    ## Primary key
    resultID = models.AutoField(primary_key=True)
    ## Search
    searchID = models.ForeignKey(Search)
    ## Title
    title = models.TextField()
    ## Rank
    rank = models.PositiveIntegerField()
    ## Url
    url = models.TextField()
    ## Snippet
    snippet = models.TextField()
    ## Value
    value = models.FloatField()
    ## Source
    source = models.ManyToManyField(Ranker, through='Sources', symmetrical=False, related_name='searchSource')

class Sources(models.Model):
    ranker = models.ForeignKey(Ranker)
    result = models.ForeignKey(SearchResult)
    rank = models.PositiveIntegerField()

    class Meta:
        ##Nombre de la tabla en la base de datos
        db_table = 'source'

class Distances(models.Model):
    firstDoc = models.ForeignKey(SearchResult, related_name='firstDoc')
    secondDoc = models.ForeignKey(SearchResult, related_name='secondDoc')
    distance = models.FloatField()

    class Meta:
        db_table = 'distances'

## Class to show results
class Link(models.Model):
    url = models.TextField()
    descr = models.TextField()
    title = models.TextField()
    rank = models.PositiveIntegerField()
    query = models.TextField()
    value = models.FloatField()
    saved = models.BooleanField()


