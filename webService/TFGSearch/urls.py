from django.conf.urls import patterns, url

urlpatterns = patterns('TFGSearch.views',
    url(r'^search/$', 'link_list'),
    url(r'^clicked/$', 'clicked_list'),
    url(r'^metases/lnk/save/$', 'saved_list'),
    url(r'^metases/lnk/delete/$', 'delete_list'),
    url(r'^metases/close/$', 'close_list'),
    url(r'^metases/open/$', 'open_list'),
    url(r'^metases/available/$', 'isAvailableName'),
    url(r'^metases/save/$', 'saveAndCloseMeta'),
    url(r'^filter/save/$', 'retrieve_list'),
    url(r'^diversity/$', 'doDiversity'),
    url(r'^relevance/$', 'do_relevance_feedback'),
    url(r'^sources/$', 'getSources'),
)