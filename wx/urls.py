from django.conf.urls import patterns, include, url
from wx import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'online.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^', views.wxapp),
)
