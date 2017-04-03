"""revalue URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
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
from django.conf.urls import url
from django.contrib import admin
from app import views
from django.conf.urls import include
from rest_framework.routers import DefaultRouter
from django.views.generic import RedirectView
# router = DefaultRouter()
# router.register(r'products',views.MasterViewSet)
# router.register(r'pos',views.PosViewSet)
# router.register(r'seasonalTrend',views.SeasonalTrendViewSet)
#router.register(r'sample',views.SampleViewSet)


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    #url(r'^$', views.index),
    #url(r'^aaa$', views.Sample),

    url(r'^api/', include('app.urls')),
    #url(r'^api/pos/(?P<jan>.+)/$', views.PosFilterViewSet.as_view()),
    # url(r'^api/preprocess$', views.preprocess.as_view()),
    # url(r'^api/predictPrice$', views.predictPrice.as_view()),
    url('^$', RedirectView.as_view(url='/static/index.html')),

    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
