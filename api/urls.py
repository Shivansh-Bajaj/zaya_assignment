"""bookcab URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib.auth import logout
from rest_framework import routers
from api import views
from rest_framework_jwt.views import (
    obtain_jwt_token,
    refresh_jwt_token)


urlpatterns = [

    url(r'^user/$',
        views.getUser.as_view()),
    url(r'^driver/$',
        views.DriverViewSet.as_view()),
    url(r'^rider/$',
        views.RiderViewSet.as_view()),
    url(r'^rider/book/$', views.BookingViewSet.as_view()),
    url(r'^driver/book/$', views.DriverStartApi.as_view()),
    url(r'^rider/book/pool/$', views.BookingPoolViewSet.as_view()),
    url(r'^driver/book/complete/$', views.DriverEndApi.as_view()),
    url(r'^rider/book/complete/$', views.RiderEndApi.as_view()),
    url(r'^social_auth/complete/$', views.SocialAuth.as_view()),
    url(r'^driver/profile/$', views.DriverAPI.as_view()),
    url(r'^rider/profile/$', views.RiderAPI.as_view()),
    url(r'^token/$', obtain_jwt_token, name='token_obtain_pair'),
    url(r'^token/refresh/$', refresh_jwt_token, name='token_refresh'),
    url(r'^logout/$', logout, name='logout'),
]

