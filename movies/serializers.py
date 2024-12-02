import re

from rest_framework import serializers
from .models import Rating

VALID_GENRES = ['Action', 'Comedy', 'Drama', 'Horror', 'Romance', 'Sci-Fi']

class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ['movie_id', 'user', 'rating']
        read_only_fields = ['user']  # user will be set automatically

    def validate_rating(self, value):
        if value < 1 or value > 10:
            raise serializers.ValidationError(
                "Rating must be between 1 and 10."
            )
        return value

class RecommendationsRequestSerializer(serializers.Serializer):
    genres = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    language = serializers.CharField(default='en')
    release_year = serializers.IntegerField(default=2023)

    def validate_genres(self, value):
        invalid_genres = [genre for genre in value if genre not in VALID_GENRES]
        if invalid_genres:
            raise serializers.ValidationError(
                f"Invalid genres: {', '.join(invalid_genres)}. Valid genres are {', '.join(VALID_GENRES)}."
            )
        return value

    def validate_language(self, value):
        if not re.match(r'^[a-z]{2}$', value):
            raise serializers.ValidationError(
                "Language code must be a two-letter ISO 639-1 code (e.g., 'en', 'fr')."
            )
        return value

    def validate_release_year(self, value):
        if value < 1900 or value > 2100:
            raise serializers.ValidationError(
                "Release year must be between 1900 and 2100."
            )
        return value
