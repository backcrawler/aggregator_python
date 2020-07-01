from django.urls import path
from . import views

app_name = 'news'

urlpatterns = [
    path('', views.PostListView.as_view(), name='mainpage'),
    path('webdev/', views.PostListView.as_view(cat='web_dev'), name='webpage'),
    path('data-science/', views.PostListView.as_view(cat='data_science'), name='datasciencepage'),
    path('userpost/', views.userform_submitting, name='userpost'),
    #path('err/<slug:errcode>/', views.err, name='err'),  # for testing error pages
    ]