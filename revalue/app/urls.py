from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns
from app import views


urlpatterns=format_suffix_patterns([
    url(r'^$',views.api_root),
    url(r'^masters/$', views.MasterList.as_view(),name='master-list'),
    url(r'^masters/(?P<pk>[0-9]+)$', views.MasterDetail.as_view(),name='master-detail'),
    url(r'^pos/$', views.PosList.as_view(),name='pos-list'),
    url(r'^pos/(?P<pk>[0-9]+)$', views.PosDetail.as_view(),name='pos-detail'),
    url(r'^seasonaltrend/$', views.SeasonalTrendList.as_view(),name='seasonaltrend-list'),
    url(r'^seasonaltrend/(?P<pk>[0-9]+)$', views.SeasonalTrendDetail.as_view(),name='seasonaltrend-detail'),
    url(r'^predict/$', views.PredictList.as_view(),name='predict-list'),
    url(r'^predict/(?P<pk>[0-9]+)$', views.Predict.as_view(),name='predict'),

])