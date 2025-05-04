from rest_framework import serializers
from .models import Review, AdminNotification, UserHistory

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'user', 'product', 'rating', 'comment', 'is_visible', 'created_at', 'updated_at']

class AdminNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminNotification
        fields = ['id', 'user', 'title', 'message', 'is_read', 'created_at']

class UserHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserHistory
        fields = ['id', 'user', 'order', 'action_type', 'description', 'created_at']
