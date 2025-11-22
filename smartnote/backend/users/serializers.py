from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
import re

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        required=True, max_length=150,
        validators=[UniqueValidator(queryset=User.objects.all())],
    )
    email = serializers.EmailField(
        required=False, allow_blank=True,
        validators=[UniqueValidator(queryset=User.objects.all())],
    )
    # KHÔNG trả password ra ngoài
    password = serializers.CharField(write_only=True, required=True, min_length=6)

    class Meta:
        model = User
        fields = ["id", "username", "email", "fullname", "password", "firebase_id", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate_username(self, v):
        if not re.fullmatch(r"[A-Za-z0-9_.]{4,150}", v):
            raise serializers.ValidationError("Username ≥4 ký tự, chỉ gồm chữ/số/_.")
        return v

    def create(self, validated_data):
        pwd = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(pwd)           # <-- HASH mật khẩu
        user.is_active = True
        user.save()
        return user

    def update(self, instance, validated_data):
        pwd = validated_data.pop("password", None)
        for k, v in validated_data.items():
            setattr(instance, k, v)
        if pwd:
            instance.set_password(pwd)   # <-- HASH khi đổi mật khẩu qua PATCH/PUT
        instance.save()
        return instance
