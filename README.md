﻿# api_development

## Setup Instructions

1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`.
3. Set up a `.env` file for sensitive keys (e.g., TMDb API key, Redis, etc.).
4. Migrate the database: `python manage.py migrate`.
5. Run the development server: `python manage.py runserver`.

## API Endpoints

### POST /api/recommendations/

**Request Body:**
```json
{
  "genres": ["Action", "Comedy"],
  "language": "en",
  "release_year": 2023
}

