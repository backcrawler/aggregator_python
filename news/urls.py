from django.urls import path
from django.conf.urls import include, url
from . import views

app_name = 'news'

urlpatterns = [
    path('', views.PostListView.as_view(), name='mainpage'),
    path('webdev/', views.PostListView.as_view(cat='web_dev'), name='webpage'),
    path('datascience/', views.PostListView.as_view(cat='data_science'), name='datasciencepage'),
    path('userpost/', views.userform_submitting, name='userpost'),
    ]