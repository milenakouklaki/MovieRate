from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("<int:movie_id>", views.movie_view, name="movie_view"),
    path('rate_movie/', views.rate_movie, name='rate_movie'),
    path('browse/', views.browse_movies, name="browse_movies"),
    path('movies_by_genre/<int:genre_id>/', views.movies_by_genre, name="movies_by_genre"),
    path('profile/', views.profile, name='profile'),
    path('search/', views.search_movies, name="search_movies")
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
