from django.urls import path
from . import views
urlpatterns = [
    path('posts/', views.ArticleListView.as_view(), name='article-list'),
]