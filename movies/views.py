import traceback

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from utils.helper import fetch_from_tmdb
from .serializers import RecommendationsRequestSerializer, RatingSerializer
import logging

logger = logging.getLogger(__name__)


# Custom function to return standard response
def standard_response(data=None, errors=None, status=None, message=None):
    return Response({
        "data": data if data else {},
        "errors": errors if errors else {},
        "status": status,
        "message": message
    }, status=status)


class GetRecommendationsView(generics.GenericAPIView):
    serializer_class = RecommendationsRequestSerializer
    permission_classes = [IsAuthenticated]  # Only authenticated users can access this view

    def post(self, request, *args, **kwargs):
        logger.info("Starting to process recommendation request.")

        # Validate the incoming request data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        logger.info("Request data validated successfully.")

        genres = validated_data.get('genres', [])
        language = validated_data.get('language', 'en')
        release_year = validated_data.get('release_year', 2023)

        # Construct cache key
        cache_key = f"recommendations_{','.join(genres)}_{language}_{release_year}"
        params = {
            'with_genres': ','.join(genres),
            'language': language,
            'primary_release_year': release_year
        }

        # Fetch recommendations from TMDb
        recommendations = fetch_from_tmdb('discover/movie', params, cache_key)

        if recommendations:
            # Paginate the recommendations
            paginator = PageNumberPagination()
            paginator.page_size = 10  # Set the number of items per page
            result_page = paginator.paginate_queryset(recommendations.get('results', []), request)

            # Prepare data to return
            data = [{'title': movie['title'], 'description': movie['overview']} for movie in result_page]

            logger.info(f"Fetched {len(data)} recommendations successfully.")
            return paginator.get_paginated_response(data)  # This returns a paginated response as per DRF format
        else:
            logger.error("Failed to fetch recommendations.")
            return standard_response(errors={"detail": "Failed to fetch recommendations from TMDb"}, status=500,
                                     message="Error fetching recommendations")


class GetMovieDetailsView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]  # Only authenticated users can access this view

    def get(self, request, movie_id, *args, **kwargs):
        logger.info(f"Fetching details for movie ID: {movie_id}")

        cache_key = f"movie_details_{movie_id}"
        params = {'language': request.GET.get('language', 'en')}

        # Fetch movie details from TMDb API
        movie_details = fetch_from_tmdb(f"movie/{movie_id}", params, cache_key)

        if movie_details:
            data = {
                'title': movie_details['title'],
                'description': movie_details['overview'],
                'release_date': movie_details['release_date'],
                'rating': movie_details['vote_average']
            }
            logger.info(f"Successfully fetched movie details for ID {movie_id}.")
            return standard_response(data=data, status=200, message="Movie details fetched successfully")
        else:
            logger.error(f"Failed to fetch details for movie ID {movie_id}.")
            return standard_response(errors={"detail": "Failed to fetch movie details"}, status=500,
                                     message="Error fetching movie details")


class SubmitRatingView(generics.CreateAPIView):
    serializer_class = RatingSerializer
    permission_classes = [IsAuthenticated]  # Only authenticated users can access this view

    def perform_create(self, serializer):
        logger.info("Starting rating submission process.")

        try:
            # Extract data from request
            movie_id = self.request.data.get('movie_id')
            rating = self.request.data.get('rating')

            # Validate required fields
            if not movie_id or not rating:
                logger.error("Missing required fields for rating submission.")
                raise ValueError("All fields are required.")

            # Validate rating range
            try:
                rating = float(rating)
                if not (1 <= rating <= 10):
                    logger.error(f"Invalid rating value: {rating}. Must be between 1 and 10.")
                    raise ValueError("Rating must be between 1 and 10.")
            except ValueError:
                logger.error(f"Invalid rating format for movie ID {movie_id}.")
                raise ValueError("Rating must be a valid number.")

            # Save the rating using the serializer and set user to the authenticated user
            serializer.save(movie_id=movie_id, rating=rating, user=self.request.user)
            logger.info(f"Successfully saved rating {rating} for movie ID {movie_id} by user {self.request.user.id}.")

        except Exception as e:
            logger.error(f"Error occurred: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise e


class GetTrendingMoviesView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated to access trending movies

    def get(self, request, *args, **kwargs):
        logger.info("Fetching trending movies")

        # Construct cache key and parameters
        cache_key = "trending_movies"
        params = {'language': request.GET.get('language', 'en')}

        # Fetch trending movies from TMDb API
        try:
            trending_movies = fetch_from_tmdb('trending/movie/day', params, cache_key)
        except Exception as e:
            logger.error(f"Error fetching trending movies: {str(e)}")
            return standard_response(errors={"detail": "Failed to fetch trending movies from TMDb"}, status=500,
                                     message="Error fetching trending movies")

        if trending_movies:
            # Paginate the results
            paginator = PageNumberPagination()
            paginator.page_size = 10  # Limit the number of results per page
            result_page = paginator.paginate_queryset(trending_movies.get('results', []), request)

            # Create the data format for the response
            data = [{'title': movie['title'], 'description': movie['overview']} for movie in result_page]

            logger.info(f"Fetched {len(data)} trending movies successfully.")
            return paginator.get_paginated_response(data)
        else:
            logger.error("Failed to fetch trending movies.")
            return standard_response(errors={"detail": "Failed to fetch trending movies from TMDb"}, status=500,
                                     message="Error fetching trending movies")