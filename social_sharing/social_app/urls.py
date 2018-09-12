from django.conf.urls import url
import views

urlpatterns = [
    url(r'^$', views.index, name='index'),

    #API
    url(r'^api/login$', views.login, name='login'),
    url(r'^api/logout$', views.logout, name='logout'),
    url(r'^api/events_list/?$', views.get_events_list, name='events_list'),
    url(r'^api/search_event/?$', views.search_event, name='search_event'),
    url(r'^api/join_event$', views.join_event, name='join_event'),
    url(r'^api/reaction$', views.reaction, name='reaction'),
    url(r'^api/comment$', views.comment, name='comment'),
    url(r'^api/get_participant/?$', views.get_participant, name='get_participant'),
    url(r'^api/get_reaction/?$', views.get_reaction, name='get_reaction'),
    url(r'^api/get_comment/?$', views.get_comment, name='get_comment'),

    #API admin
    url(r'^api/admin/login$', views.admin_login, name='admin_login'),
    url(r'^api/admin/upload$', views.admin_upload, name='admin_upload')
]
