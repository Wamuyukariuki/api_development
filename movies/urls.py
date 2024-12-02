from django.urls import path
from .views import GetRecommendationsView, GetMovieDetailsView, SubmitRatingView, GetTrendingMoviesView

urlpatterns = [
    # Recommendations endpoint
    path('recommendations/', GetRecommendationsView.as_view(), name='get_recommendations'),

    # Movie details endpoint
    path('movie/<int:movie_id>/', GetMovieDetailsView.as_view(), name='get_movie_details'),

    # Submit rating endpoint
    path('submit-rating/', SubmitRatingView.as_view(), name='submit_rating'),

    path('trending-movies/', GetTrendingMoviesView.as_view(), name='trending-movies'),

]
