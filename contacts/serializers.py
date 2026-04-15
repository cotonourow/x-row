from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Contact, Worker


# -----------------------------------------
# USER REGISTER SERIALIZER
# -----------------------------------------
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "password"]

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"],
        )
        return user


# -----------------------------------------
# CONTACT SERIALIZER
# -----------------------------------------
class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ["id", "name", "phone_number"]


# -----------------------------------------
# WORKER SERIALIZER (NEW!)
# -----------------------------------------
class WorkerSerializer(serializers.ModelSerializer):
    skill_display = serializers.CharField(source='get_skill_display', read_only=True)
    rating_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Worker
        fields = [
            'id', 
            'name', 
            'skill', 
            'skill_display',
            'location', 
            'phone',
            'experience_years',
            'rating',
            'rating_display',
            'is_available',
            'created_at'
        ]
    
    def get_rating_display(self, obj):
        """Return star rating display"""
        return f"{'⭐' * int(obj.rating)}{'½' if obj.rating % 1 >= 0.5 else ''}" if obj.rating > 0 else "No rating"

    def validate_phone(self, value):
        """Validate Nigerian phone format"""
        normalized = Worker.normalize_phone(value)
        if len(normalized) != 11:
            raise serializers.ValidationError("Phone number must be 11 digits (e.g., 08012345678)")
        if not normalized.startswith(('070', '080', '081', '090', '091')):
            raise serializers.ValidationError("Invalid Nigerian phone number prefix")
        return normalized

    def validate_rating(self, value):
        if value < 0 or value > 5:
            raise serializers.ValidationError("Rating must be between 0.0 and 5.0")
        return value