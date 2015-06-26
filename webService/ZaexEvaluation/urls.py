from django.conf.urls import patterns, url

urlpatterns = patterns('ZaexEvaluation.views',
    url(r'^search/$', 'evaluate_search'),
    url(r'^click/$', 'clickedEvaluation_list'),
    url(r'^evaluate/clicks$', 'evaluateClick'),
    url(r'^evaluate/queries$', 'evaluateQuery'),
    url(r'^evaluate/patk$', 'evaluatePAtK'),
    url(r'^evaluate/ratk$', 'evaluateRAtK'),
    url(r'^evaluate/ndcg$', 'evaluateNDCGAtK'),
    url(r'^evaluate/mrr$', 'evaluateMRR'),
    url(r'^evaluate/map$', 'evaluateMAP'),
    url(r'^evaluate/ild$', 'evaluateILD'),
    url(r'^evaluate/report', 'evaluationReport'),
)