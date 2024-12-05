from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from movies.utils.helper import fetch_from_tmdb


# token = ''

class GetRecommendationsViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('get_recommendations')  # Dynamically resolve the URL
        self.user = self.create_user()
        # self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def create_user(self):
        from django.contrib.auth.models import User
        return User.objects.create_user(username='jackson.wamuyu', password='Admin@001')

    class GetRecommendationsViewTest(TestCase):
        url = '/api/recommendations/'  # Adjust this URL based on your view's actual path

        @patch('movies.utils.helper.fetch_and_paginate_tmdb_data')
        def test_successful_recommendation_request(self, mock_fetch):
            # Mock the response from the external API
            mock_fetch.return_value = {
                "count": 1,
                "results": [
                    {"title": "Test Movie", "description": "A test movie description"}
                ]
            }

            # Define the data to be sent in the POST request
            data = {
                "genres": ["Action", "Comedy"],
                "language": "en",
                "release_year": 2023
            }

            # Make the actual request to the view
            response = self.client.post(self.url, data, format='json')

            # Assert the response status code is 200 OK
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            # Check if 'results' is present in the response
            self.assertIn("results", response.data)

            # Assert that the movie title in the response is "Test Movie"
            self.assertEqual(response.data["results"][0]["title"], "Test Movie")

            # Ensure fetch_and_paginate_tmdb_data was called with the correct arguments
            mock_fetch.assert_called_once_with(
                response.wsgi_request,
                'discover/movie',
                {
                    'with_genres': 'Action,Comedy',
                    'language': 'en',
                    'primary_release_year': 2023
                },
                'recommendations_Action,Comedy_en_2023'
            )

    def test_missing_required_fields(self):
        data = {"language": "en"}  # Missing `genres`, but `release_year` is implied to have default value

        response = self.client.post(self.url, data, format='json')

        # Debug output to inspect the response
        print("Response Status Code:", response.status_code)
        print("Response Data:", response.json())

        # Assert that the response status code is 400 BAD REQUEST
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Assert that the 'genres' field is in the error response
        self.assertIn("genres", response.data)
        self.assertIn("This field is required.", response.data["genres"][0])

        # Check that 'release_year' is not present in the response data error message,
        # because the default value should be used.
        self.assertNotIn("release_year", response.data)


class TestGetTrendingMoviesView(TestCase):
    def test_get_trending_movies_200(self):
        response = self.client.get(reverse('trending-movies'))
        self.assertEqual(response.status_code, 200)


class GetMovieDetailsViewTest(TestCase):

    def setUp(self):
        # Initialize the APIClient for making requests
        self.client = APIClient()

        # Define the URL for the movie details endpoint
        self.url = reverse('get_movie_details', kwargs={'movie_id': 123})

    @patch('movies.views.fetch_from_tmdb')
    def test_get_movie_details_success(self, mock_fetch):
        # Mock the successful response from the TMDb API
        mock_fetch.return_value = {
            'title': 'Star Trek: Insurrection',
            'overview': 'A movie description.',
            'release_date': '1998-12-11',
            'vote_average': 6.4
        }

        # Make the GET request to fetch movie details
        response = self.client.get(self.url)

        # Check the status code and validate response data
        self.assertEqual(response.status_code, 200)
        self.assertIn('data', response.data)
        self.assertIn('title', response.data['data'])
        self.assertEqual(response.data['data']['title'], 'Star Trek: Insurrection')

    @patch('movies.views.fetch_from_tmdb')
    def test_get_movie_details_failure(self, mock_fetch):
        # Mock the failure case when movie details are not found
        mock_fetch.return_value = None

        # Make the GET request to fetch movie details
        invalid_url = reverse('get_movie_details', kwargs={'movie_id': 12})  # Invalid ID
        response = self.client.get(invalid_url)

        # Check for the correct error response
        self.assertEqual(response.status_code, 404)
        self.assertIn('errors', response.data)
        self.assertEqual(response.data['errors']['detail'], 'Movie not found in TMDb.')

    @patch('movies.views.fetch_from_tmdb')
    def test_get_movie_details_exception(self, mock_fetch):
        # Mock a generic exception during the API call
        mock_fetch.side_effect = Exception("Internal server error")

        # Make the GET request to fetch movie details
        response = self.client.get(self.url)

        # Check for a 500 server error response
        self.assertEqual(response.status_code, 500)
        self.assertIn('errors', response.data)
        self.assertEqual(response.data['errors']['detail'], 'Failed to fetch movie details')


from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework import status

class TestSubmitRatingView(APITestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='jackson.wamuyu', password='Admin@001')

        # Obtain a token for the user
        response = self.client.post('/api/token/', {'username': 'jackson.wamuyu', 'password': 'Admin@001'})
        self.token = response.data['access']

        # Set up the URL and data for the rating submission
        self.url = reverse('submit_rating')  # Ensure this matches your URL pattern name
        self.data = {
            'movie_id': 123,
            'rating': 8.5
        }

        # Use APIClient with authentication
        self.api_client = APIClient()
        self.api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def test_submit_rating_201(self):
        # Make the POST request with authenticated user
        response = self.api_client.post(self.url, data=self.data, format='json')

        # Debugging: Inspect the response content
        print("Response Data:", response.data)

        # Assert that the response status code is 201
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Assert that the response contains the success message
        self.assertIn('success', response.json().get('message', ''))

