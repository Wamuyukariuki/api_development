import logging
import traceback
from rest_framework import generics
from rest_framework.permissions import AllowAny
from movies.utils.helper import fetch_from_tmdb, fetch_and_paginate_tmdb_data
from movies.utils.responses import standard_response
from .serializers import RecommendationsRequestSerializer, RatingSerializer
from rest_framework.exceptions import NotFound


logger = logging.getLogger(__name__)


class GetRecommendationsView(generics.GenericAPIView):
    serializer_class = RecommendationsRequestSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        logger.info("Starting to process recommendation request.")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        genres = validated_data.get('genres', [])
        language = validated_data.get('language', 'en')
        release_year = validated_data.get('release_year', 2023)

        cache_key = f"recommendations_{','.join(genres)}_{language}_{release_year}"
        params = {
            'with_genres': ','.join(genres),
            'language': language,
            'primary_release_year': release_year
        }

        return fetch_and_paginate_tmdb_data(request, 'discover/movie', params, cache_key)


class GetMovieDetailsView(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def get(self, request, movie_id, *args, **kwargs):
        logger.info(f"Fetching details for movie ID: {movie_id}")

        cache_key = f"movie_details_{movie_id}"
        params = {'language': request.GET.get('language', 'en')}

        try:
            # Fetch the movie details from TMDB
            movie_details = fetch_from_tmdb(f"movie/{movie_id}", params, cache_key)

            # Check if the movie details were returned
            if movie_details is None:
                logger.error(f"Movie with ID {movie_id} not found.")
                raise NotFound(detail="Movie not found in TMDb.")

            # Parse the movie details
            data = {
                'title': movie_details['title'],
                'description': movie_details['overview'],
                'release_date': movie_details['release_date'],
                'rating': movie_details['vote_average']
            }

            logger.info(f"Successfully fetched movie details for ID {movie_id}.")
            return standard_response(data=data, status=200, message="Movie details fetched successfully")
        except NotFound as e:
            return standard_response(errors={"detail": str(e)}, status=404, message="Movie not found")
        except Exception as e:
            logger.error(f"Error fetching movie details for ID {movie_id}: {str(e)}")
            return standard_response(errors={"detail": "Failed to fetch movie details"}, status=500, message="Error fetching movie details")


class SubmitRatingView(generics.CreateAPIView):
    serializer_class = RatingSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        logger.info("Starting rating submission process.")

        try:
            movie_id = self.request.data.get('movie_id')
            rating = self.request.data.get('rating')

            if not movie_id or not rating:
                logger.error("Missing required fields for rating submission.")
                raise ValueError("All fields are required.")

            try:
                rating = float(rating)
                if not (1 <= rating <= 10):
                    logger.error(f"Invalid rating value: {rating}. Must be between 1 and 10.")
                    raise ValueError("Rating must be between 1 and 10.")
            except ValueError:
                logger.error(f"Invalid rating format for movie ID {movie_id}.")
                raise ValueError("Rating must be a valid number.")

            if not self.request.user.is_authenticated:
                logger.error("Unauthenticated user attempted to submit a rating.")
                raise PermissionError("User must be authenticated to submit a rating.")

            serializer.save(movie_id=movie_id, rating=rating, user=self.request.user)
            logger.info(f"Successfully saved rating {rating} for movie ID {movie_id} by user {self.request.user.id}.")

        except Exception as e:
            logger.error(f"Error occurred: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise e


class GetTrendingMoviesView(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        logger.info("Fetching trending movies")

        cache_key = "trending_movies"
        params = {'language': request.GET.get('language', 'en')}

        return fetch_and_paginate_tmdb_data(request, 'trending/movie/day', params, cache_key)
