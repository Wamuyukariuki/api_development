import logging
import requests
from django.conf import settings
from django.core.cache import cache
from requests.exceptions import RequestException, HTTPError
import time

from rest_framework.pagination import PageNumberPagination

from utils.responses import standard_response

# Set up logging
logger = logging.getLogger(__name__)


def fetch_from_tmdb(endpoint, params, cache_key, timeout=600, retries=3, backoff_factor=1.0):
    """
    Fetch data from TMDb API with Redis caching, retry logic, and rate limit handling.
    """
    try:
        # Check cache first
        cached_data = cache.get(cache_key)
        if cached_data:
            logger.info(f"Cache hit for key: {cache_key}")
            return cached_data

        # Fetch from TMDb API
        url = f"{settings.TMDB_API_URL}{endpoint}"
        params['api_key'] = settings.TMDB_API_KEY

        # Retry loop in case of failure
        for attempt in range(retries):
            try:
                response = requests.get(url, verify=False, params=params)
                response.raise_for_status()  # Raise an HTTPError for bad responses

                # Check for rate limit (429 Too Many Requests)
                if response.status_code == 429:
                    logger.warning(f"Rate limit exceeded. Retrying in {backoff_factor * (2 ** attempt)} seconds...")
                    time.sleep(backoff_factor * (2 ** attempt))  # Exponential backoff
                    continue  # Retry the request

                # Parse and cache the data
                data = response.json()
                cache.set(cache_key, data, timeout=timeout)
                logger.info(f"Cache miss for key: {cache_key} - Fetched and cached data from TMDb API")
                return data

            except HTTPError as http_err:
                logger.error(f"HTTP error occurred: {http_err}")  # Log HTTP errors
                break  # Exit retry loop on permanent errors (e.g., 4xx, 5xx)

            except RequestException as req_err:
                logger.error(f"Request error occurred: {req_err}")  # Log request errors
                break  # Exit retry loop on errors like network issues

            except Exception as e:
                logger.critical(f"Unexpected error in fetch_from_tmdb: {e}")  # Log unexpected errors
                break

        # If the retries are exhausted or we hit a fatal error
        logger.error(f"Failed to fetch data from TMDb after {retries} retries.")
        return None

    except Exception as e:
        # Catch-all for unexpected exceptions at the top level
        logger.critical(f"Unexpected error in fetch_from_tmdb: {e}")
        return None


# Helper function to handle TMDb fetching and pagination
def fetch_and_paginate_tmdb_data(request, endpoint, params, cache_key, page_size=10):
    try:
        data = fetch_from_tmdb(endpoint, params, cache_key)
        if data:
            paginator = PageNumberPagination()
            paginator.page_size = page_size
            result_page = paginator.paginate_queryset(data.get('results', []), request)
            return paginator.get_paginated_response(
                [{'title': movie['title'], 'description': movie['overview']} for movie in result_page]
            )
        else:
            logger.error(f"Failed to fetch data for {cache_key}.")
            return standard_response(errors={"detail": "Failed to fetch data from TMDb"}, status=500,
                                     message="Error fetching data")
    except Exception as e:
        logger.error(f"Error occurred while fetching data: {str(e)}")
        return standard_response(errors={"detail": "Internal server error"}, status=500, message="Error fetching data")
