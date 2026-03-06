# accounts/api/serializers.py
from django.contrib.auth import authenticate
from rest_framework import serializers

class LoginSerializer(serializers.Serializer):
    identifier = serializers.CharField(max_length=254)
    password = serializers.CharField(max_length=128, write_only=True)
    remember = serializers.BooleanField(default=False)

    def validate(self, attrs):
        identifier = attrs["identifier"].strip()
        password = attrs["password"]

        user = authenticate(
            self.context.get("request"),
            identifier=identifier,
            password=password,
        )

        # ВАЖНО: единая ошибка (не палим существует ли юзер)
        if not user:
            raise serializers.ValidationError({"detail": "Invalid credentials."})

        attrs["user"] = user
        attrs["identifier"] = identifier
        return attrs