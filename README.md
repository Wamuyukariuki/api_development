**Movie Recommendation API**
This is a Django-based API for fetching and recommending movies using the TMDb API. It allows users to filter movies based on genres, language, and release year.

**Table of Contents**
Features
Prerequisites
Setup Instructions
Configuring TMDb API Key
Running the Server
Testing the Endpoints
License

**Features**
Filter movies by genre, language, and release year.
User authentication using JWT.
Fetches movie data from the TMDb API.
Rate and fetch movie recommendations.

**Prerequisites**
Make sure you have the following installed:
Python 3.10 or above
pip (Python package manager)
Virtualenv (optional but recommended)

**Setup Instructions**
Clone the repository:

bash
Copy code
git clone https://github.com/your-username/movie-recommendation-api.git
cd movie-recommendation-api
Set up a virtual environment (optional):

bash
Copy code
python -m venv env
source env/bin/activate    # On Windows: env\Scripts\activate
Install dependencies:

bash
Copy code
pip install -r requirements.txt
Run database migrations:

bash
Copy code
python manage.py migrate
Create a superuser (for admin access):

bash
Copy code
python manage.py createsuperuser

**Configuring TMDb API Key**
Go to the TMDb website and create an account if you don’t have one.
Generate an API key from the developer section.
Create a .env file in the project root and add your API key:

plaintext
Copy code
TMDB_API_KEY=your_tmdb_api_key_here
Ensure the .env file is not tracked by Git by checking your .gitignore file.

**Running the Server**
Start the Django development server:

bash
Copy code
python manage.py runserver
The API will be available at http://127.0.0.1:8000/.

**Testing the Endpoints**
1. Obtain a JWT Token:
Endpoint: /api/token/
Method: POST
Payload:
json
Copy code
{
  "username": "your_username",
  "password": "your_password"
}
Response:
json
Copy code
{
  "access": "your_access_token",
  "refresh": "your_refresh_token"
}
2. Fetch Movie Recommendations:
Endpoint: /api/recommendations/
Method: POST
Headers:
plaintext
Copy code
Authorization: Bearer your_access_token
Payload:
json
Copy code
{
  "genres": ["Action", "Comedy"],
  "language": "en",
  "release_year": 2023
}
Response:
json
Copy code
{
  "count": 20,
  "results": [
    {
      "title": "Movie Title",
      "overview": "Movie overview...",
      "release_date": "2023-01-01"
    },
    ...
  ]
}
License
This project is licensed under the MIT License. See the LICENSE file for details.