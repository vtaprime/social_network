from django.conf.urls import url
import views

urlpatterns = [
    url(r'^$', views.index, name='index'),

    #API
    url(r'^api/login$', views.login, name='login'),
    # url(r'^api/logout/', views.logout(), name='logout'),
    url(r'^api/events_list$', views.get_events_list, name='events_list'),
    url(r'^api/search_event/?$', views.search_event, name='search_event'),
    url(r'^api/admin/upload$', views.admin_upload, name='admin_upload')
]
