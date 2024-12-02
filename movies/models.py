from django.db import models
from django.contrib.auth.models import User

class Rating(models.Model):
    movie_id = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically set when the object is created
    updated_at = models.DateTimeField(auto_now=True)      # Automatically update when the object is saved

    class Meta:
        unique_together = ['movie_id', 'user']

    def __str__(self):
        return f'Movie ID: {self.movie_id}, User ID: {self.user.id}, Rating: {self.rating}'
