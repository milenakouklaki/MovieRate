from django.contrib import admin
from .models import *

admin.site.register(Movie)
admin.site.register(Genre)
admin.site.register(MovieRating)
admin.site.register(AverageRating)
admin.site.register(UserProfile)
