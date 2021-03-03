from django.urls import path

from .views import MoviesDetailsApi, MoviesListApi

urlpatterns = [
    path('movies/', MoviesListApi.as_view()),
    path('movies/<uuid:pk>/', MoviesDetailsApi.as_view()),
]
