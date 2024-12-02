from rest_framework import serializers
import re
from .models import Rating


GENRE_ID_TO_NAME = {
    28: "Action",
    12: "Adventure",
    16: "Animation",
    35: "Comedy",
    80: "Crime",
    99: "Documentary",
    18: "Drama",
    10751: "Family",
    14: "Fantasy",
    36: "History",
    27: "Horror",
    10402: "Music",
    9648: "Mystery",
    10749: "Romance",
    878: "Science Fiction",
    10770: "TV Movie",
    53: "Thriller",
    10752: "War",
    37: "Western"
}



class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ['movie_id', 'user', 'rating']
        read_only_fields = ['user']  # user will be set automatically

    def validate_rating(self, value):
        if value < 1 or value > 10:
            raise serializers.ValidationError("Rating must be between 1 and 10.")
        return value

class RecommendationsRequestSerializer(serializers.Serializer):
    genres = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    language = serializers.CharField(default='en')
    release_year = serializers.IntegerField(default=2023)

    def validate_genres(self, value):
        # Convert genre names to their IDs if valid
        validated_genres = []
        for genre in value:
            if genre.isdigit():  # Check if the genre is a numeric ID
                genre_id = int(genre)
                if genre_id in GENRE_ID_TO_NAME:
                    validated_genres.append(str(genre_id))
                else:
                    raise serializers.ValidationError(
                        f"Invalid genre ID: {genre}. Valid genre IDs are {', '.join(map(str, GENRE_ID_TO_NAME.keys()))}."
                    )
            else:  # Treat as genre name
                genre_id = next((id for id, name in GENRE_ID_TO_NAME.items() if name.lower() == genre.lower()), None)
                if genre_id:
                    validated_genres.append(str(genre_id))
                else:
                    raise serializers.ValidationError(
                        f"Invalid genre name: {genre}. Valid genre names are {', '.join(GENRE_ID_TO_NAME.values())}."
                    )
        return validated_genres

    def validate_language(self, value):
        if not re.match(r'^[a-z]{2}$', value):
            raise serializers.ValidationError("Language code must be a two-letter ISO 639-1 code (e.g., 'en', 'fr').")
        return value

    def validate_release_year(self, value):
        if value < 1900 or value > 2100:
            raise serializers.ValidationError("Release year must be between 1900 and 2100.")
        return value
