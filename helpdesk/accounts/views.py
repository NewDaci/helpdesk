from django.db.models import CharField
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.models import User
from .serializers import RegisterSerializer, UserSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from drf_spectacular.types import OpenApiTypes
from django.db.models import Value, Q
from django.db.models.functions import Concat, Cast

from accounts.permissions import IsAdmin
from .serializers import RoleUpdateSerializer
from django.shortcuts import get_object_or_404


# register
@extend_schema(
    request=RegisterSerializer,
    responses=UserSerializer,
    summary="Register a new user account",
)
@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response(UserSerializer(user).data, status=201)
    return Response(serializer.errors, status=400)


# me
@extend_schema(
    responses=UserSerializer, summary="Get current authenticated user details"
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    return Response(UserSerializer(request.user).data)


# update account
@extend_schema(
    request=UserSerializer,
    responses=UserSerializer,
    summary="Update current authenticated user account",
)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_account(request):
    user = request.user
    user.username = request.data.get("username", user.username)
    user.email = request.data.get("email", user.email)
    user.save()
    return Response(UserSerializer(user).data)


# logout
@extend_schema(
    summary="Logout user",
    request=None,
    responses={
        200: OpenApiResponse(
            description="Logout successful",
            response={"type": "object", "properties": {"message": {"type": "string"}}},
        )
    },
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    return Response({"message": "Logout successful. Please delete token on client."})


# delete account
@extend_schema(
    responses=OpenApiTypes.OBJECT, summary="Delete current authenticated user account"
)
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_account(request):
    request.user.delete()
    return Response({"message": "Account deleted"})


# search users
@extend_schema(
    summary="Search users by username, email, first name, or last name",
    parameters=[
        OpenApiParameter(
            name="q",
            description="Search keyword (username, email, first name, last name)",
            required=False,
            type=str,
        )
    ],
    responses=UserSerializer(many=True),
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def search_users(request):
    keyword = request.GET.get("q", "")

    users = (
        User.objects.filter(
            Q(username__icontains=keyword)
            | Q(email__icontains=keyword)
            | Q(first_name__icontains=keyword)
            | Q(last_name__icontains=keyword)
        )
        .annotate(
            nameEmail=Concat(
                "username",
                Value(" "),
                "last_name",
                Value(" - "),
                Cast("email", CharField()),
            )
        )
        .values("id", "nameEmail")
    )

    return Response(users)


# admin can update user role
@extend_schema(
    request=RoleUpdateSerializer,
    responses=UserSerializer,
    summary="Admin can update user role",
)
@api_view(["PUT"])
@permission_classes([IsAuthenticated, IsAdmin])
def update_user_role(request, user_id):
    user = get_object_or_404(User, id=user_id)

    serializer = RoleUpdateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user.profile.role = serializer.validated_data["role"]
    user.profile.save()

    return Response(UserSerializer(user).data)
