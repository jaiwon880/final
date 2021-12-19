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
    # path('survey-results/<int:choice>/', views.SurveyResultsView.as_view(), name='fullre'),
    path('register/', views.RegisterView.as_view(), name='register'),
  # path('login/', auth_views.LoginView.as_view(template_name='survey/login.html'), name='login'),
  path('profile/', views.ProfileView.as_view(), name='profile'),
  # path('logout/', auth_views.LogoutView.as_view(), name='logout'),
  path('surveys/create/', views.SurveyCreateView.as_view(), name='survey_create'),
  # path('survey-assginment/<int:assignment_id>/', views.SurveyAssignmentView.as_view(), name='survey_assignment'),
  path('survey-management/<int:survey_id>/', views.SurveyManagerView.as_view(), name='survey_management'),
  path('survey-results/<int:survey_id>/', views.SurveyResultsView.as_view(), name='survey_results'),
]