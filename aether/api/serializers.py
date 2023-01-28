from django.contrib.auth.models import User
from rest_framework.serializers import ModelSerializer

from aether.forum.models import ForumPost, ForumPostEdit, ForumUser


class LimitedForumUserSerializer(ModelSerializer):
    class Meta:
        model = ForumUser
        fields = ("id", "alias", "signature")


class LimitedUserSerializer(ModelSerializer):
    profile = LimitedForumUserSerializer()

    class Meta:
        model = User
        fields = ("id", "is_staff", "date_joined", "profile")


class ForumPostEditSerializer(ModelSerializer):
    class Meta:
        model = ForumPostEdit
        fields = ("id", "editor", "message", "created_at")


class ForumPostSerializer(ModelSerializer):
    user = LimitedUserSerializer()
    edits = ForumPostEditSerializer(many=True)

    class Meta:
        model = ForumPost
        fields = ("id", "thread", "user", "edits", "message", "created_at")
