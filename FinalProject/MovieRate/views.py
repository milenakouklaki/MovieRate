from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import *
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from .forms import UserProfileForm, RatingForm

# Create your views here.


def index(request):
    user = request.user
    top_rated_movies = Movie.objects.order_by('-averagerating__average_rating')[:5]  # Get the top 5 movies ordered by rating

    if user.is_authenticated:
        # For authenticated users, check if they have rated any movies with 4 stars or above
        user_rated_movies = MovieRating.objects.filter(user=user, rating__gte=4)
        if user_rated_movies.exists():
            # If the user has rated movies, get the genres of the movies they have rated highly
            # Get the ids of the genres of the movies the user has rated 
            top_genre_ids = user_rated_movies.values_list('movie__genre__id', flat=True)
            # Get the recommended movies that match the user's top genres
            recommended_movies = Movie.objects.filter(genre__id__in=top_genre_ids).distinct()[:5]
            if len(recommended_movies) < 5:
                # If there are not enough movies based on the user's preferences, include default recommendations
                # Merge default recommendations with user-based recommendations
                recommended_movies |= top_rated_movies
        else:
            # If the user has not rated any movies, provide fallback standard recommendations
            recommended_movies = top_rated_movies
    else:
        # Non-registered users get standard recommendations, which are not currently visible
        recommended_movies = top_rated_movies

    return render(request, 'MovieRate/index.html', {'user': user, 'recommended_movies': recommended_movies})


def movie_view(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)
    average_rating = AverageRating.objects.filter(movie=movie).first()
    user_rating = None

    if request.user.is_authenticated:
        user_rating = MovieRating.objects.filter(user=request.user, movie=movie).first()

    if request.method == 'POST':
        form = RatingForm(request.POST)
        if form.is_valid() and request.user.is_authenticated:
            rating = form.cleaned_data['rating']
            user_rating, created = MovieRating.objects.get_or_create(user=request.user, movie=movie)
            user_rating.rating = rating
            user_rating.save()
            return redirect('movie_view', movie_id=movie.id)
    else:
        form = RatingForm()

    numratings = MovieRating.objects.filter(movie=movie).count()

    return render(request, 'MovieRate/movie_view.html', {
        'movie': movie,
        'average_rating': average_rating,
        'user_rating': user_rating,
        'rating_form': form,
        'numratings': numratings
    })

def rate_movie(request):
    if request.method == 'GET':
        movie_id = request.GET.get('movie_id')
        rating = request.GET.get('rating')
        user = request.user

        if user.is_authenticated:
            movie = get_object_or_404(Movie, pk=movie_id)
            user_rating, created = MovieRating.objects.get_or_create(user=user, movie=movie)
            user_rating.rating = rating
            user_rating.save()
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error', 'message': 'User not authenticated.'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})


def browse_movies(request):
    genres = Genre.objects.filter(parent=None)
    return render(request, 'MovieRate/browse_movies.html', {'genres': genres})

def movies_by_genre(request, genre_id):
    genre = get_object_or_404(Genre, id=genre_id)
    # Get the Q object to filter movies of the selected genre and its subgenres
    genre_and_subgenres = Q(genre=genre) | Q(genre__parent=genre)
    movies = Movie.objects.filter(genre_and_subgenres).distinct()
    return render(request, 'MovieRate/movies_by_genre.html', {'genre': genre, 'movies': movies})


def search_movies(request):
    query = request.GET.get('q')
    movies = []

    if query:
        if request.user.is_authenticated:
            filter_option = request.GET.get('filter')
            if filter_option == 'title':
                movies = Movie.objects.filter(title__icontains=query)
            elif filter_option == 'genre':
                movies = Movie.objects.filter(genre__name__icontains=query)
            else:
                movies = Movie.objects.filter(title__icontains=query) | Movie.objects.filter(genre__name__icontains=query)
        else:
            movies = Movie.objects.filter(title__icontains=query) | Movie.objects.filter(genre__name__icontains=query)

    movies = movies.distinct()

    return render(request, 'MovieRate/search_results.html', {'movies': movies, 'query': query})

@login_required
def profile(request):
    user = request.user
    try:
        profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        # If UserProfile doesn't exist, create it with default display name and bio
        profile = UserProfile.objects.create(user=user, display_name=user.username)

    ratings = MovieRating.objects.filter(user=user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)

    return render(request, 'MovieRate/profile.html', {'profile': profile, 'ratings': ratings, 'form': form})