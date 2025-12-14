from rest_framework import serializers
from .models import Ticket, TicketComment
from django.contrib.auth.models import User

class TicketCommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = TicketComment
        fields = ['id', 'user', 'comment', 'created_at']


class TicketSerializer(serializers.ModelSerializer):
    comments = TicketCommentSerializer(many=True, read_only=True)
    created_by = serializers.StringRelatedField(read_only=True)
    assigned_to = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Ticket
        fields = '__all__'
        read_only_fields = ['status', 'created_by']

class TicketAgentIDSerializer(serializers.Serializer):
    agent_id = serializers.IntegerField()
    