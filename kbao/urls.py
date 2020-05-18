"""kbao URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls import url, include
from django.conf import settings
from django.conf.urls.static import static
from django.views import static as static_view
from portal.views import index

urlpatterns = [
    url('admin/', admin.site.urls),
    url(r'^portal/', include('portal.urls')),
    url(r'^kf/', include('kf.urls')),
    url(r'^proxy/', include('proxy.urls')),
    url(r'^$', index),
]

if not settings.DEBUG:
    urlpatterns.append(url(r'^static/(?P<path>.*)$', static_view.serve,
                           {'document_root': settings.STATICFILES_DIRS[0]},
                           name='static'), )
    urlpatterns.append(url(r'^data/(?P<path>.*)$', static_view.serve,
                           {'document_root': settings.MEDIA_ROOT},
                           name='media'), )