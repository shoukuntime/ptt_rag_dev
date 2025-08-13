from django.urls import path
from . import views
urlpatterns = [
    path('posts/', views.ArticleListView.as_view(), name='article-list'),
    path('posts/<int:pk>/', views.ArticleDetailView.as_view(), name='article-detail'),
    path('statistics/', views.ArticleStatisticsView.as_view(), name='article-statistics'),
]