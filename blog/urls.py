from django.urls import path
from . import views


app_name = 'blog'

urlpatterns = [
    path('', views.post_list, name='post_list'),
    #숫자형태의 url이 들어온다.
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('post/new/', views.post_new, name='post_new'),
    path('post/<int:pk>/edit/', views.post_edit, name='post_edit'),
    path('post/<int:pk>/remove/', views.post_remove, name='post_remove'),
    path('post/<int:pk>/comment/', views.add_comment_to_post, name='add_comment_to_post'),
    # localhost:8080/comment/5/approve
    path('comment/<int:pk>/approve', views.comment_approve, name='comment_approve'),
    # localhost:8080/comment/5/remove
    path('comment/<int:pk>/remove', views.comment_remove, name='comment_remove'),

]
