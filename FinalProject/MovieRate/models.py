from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
# Create your models here.

#genre table model
class Genre(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

#movie table model
class Movie(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    genre = models.ManyToManyField(Genre)
    release_date = models.DateField()
    director = models.CharField(max_length=255)
    cover_image = models.ImageField(upload_to='covers/', null=True, blank=True)

    def __str__(self):
        return self.title

#movie rating table model
class MovieRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) #if the user who submitted is deleted, the whole rating should be deleted
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE) #if the movie is deleted, the whole rating should be deleted
    rating = models.DecimalField(default=0, max_digits=2, decimal_places=1, validators=[MaxValueValidator(5)])

    def __str__(self):
        return f"{self.user.username} - {self.movie.title}: {self.rating}"

#average rating table model
class AverageRating(models.Model):
    movie = models.OneToOneField(Movie, on_delete=models.CASCADE)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=50, default="")
    bio = models.TextField(blank=True)

# Signal function to create AverageRating for new Movie objects
@receiver(post_save, sender=Movie)
def create_average_rating(sender, instance, created, **kwargs):
    if created:
        AverageRating.objects.create(movie=instance)

# Define the signal for updating the average rating
@receiver(post_save, sender=MovieRating)
@receiver(post_delete, sender=MovieRating)
def update_average_rating(sender, instance, **kwargs):
    movie = instance.movie
    user_ratings = MovieRating.objects.filter(movie=movie)
    total_ratings = sum(rating.rating for rating in user_ratings)
    num_ratings = user_ratings.count()
    average_rating = total_ratings / num_ratings if num_ratings else 0

    # Update the AverageRating model
    avg_rating, created = AverageRating.objects.get_or_create(movie=movie)
    avg_rating.average_rating = average_rating
    avg_rating.save()


