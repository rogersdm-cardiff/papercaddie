from django.conf.urls import include, url

from django.contrib import admin

from data_extraction import views

admin.autodiscover()

urlpatterns = [
    #url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}, name="logout"),
    # url(r'^logout/$', 'django.contrib.auth.views.logout', name="logout"),
    #url(r'password_change/$', 'django.contrib.auth.views.password_change', {'template_name': 'registration/password_change.html'}),
    url('^', include('django.contrib.auth.urls')),
    url(r'^$', views.index, name='index'),
    url(r'^authors$', views.authors, name='authors'),
    url(r'^groups/(?P<pk>[^/.]+)$', views.groups, name='groups'),
    url(r'^groups$', views.groups, name='groups'),
    url(r'^applications/(?P<state>[^/.]+)$', views.applications, name='applications'),
    url(r'^applications', views.applications, name='applications'),
    url(r'^results/(?P<state>[^/.]+)$', views.results, name='results'),
    url(r'^results', views.results, name='results'),
    url(r'^data_sets/(?P<state>[^/.]+)$', views.data_sets, name='data_sets'),
    url(r'^data_sets', views.data_sets, name='data_sets'),
    url(r'^table/(?P<state>[^/.]+)$', views.table, name='table'),
    url(r'^table', views.table, name='table'),
    url(r'^paper/(?P<pk>[^/.]+)/add/(?P<action>[^/.]+)', views.add, name='add'),
    url(r'^paper/(?P<pk>[^/.]+)/add', views.add, name='add'),
    url(r'^paper/(?P<pk>[^/.]+)/edit', views.edit, name='edit'),
    url(r'^paper/(?P<pk>[^/.]+)/extract', views.extract, name='extract'),
    url(r'^paper/(?P<pk>[^/.]+)/pdf', views.pdf, name='pdf'),
    url(r'^admin/', include(admin.site.urls))
]
