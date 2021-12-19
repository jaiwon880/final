from django.urls import path
from . import views

from django.conf.urls import *
from polls.views import PollFeed
from django.contrib import admin
admin.autodiscover()

app_name = 'polls'

urlpatterns=[
    path('',views.IndexView.as_view(),name='index'), #인덱스 첫 메인 polls
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    path('<int:question_id>/vote/', views.vote, name='vote'),
    # path('<int:pk>/full/', views.FullResultsView.as_view(), name='full'),
    path('<int:pk>/fullre/', views.FullResultsView.as_view(), name='fullre'),
    path('register/', views.RegisterView.as_view(), name='register'),
]