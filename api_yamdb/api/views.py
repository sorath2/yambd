from typing import Type

from django.db.models import Avg, QuerySet
from django.utils.functional import cached_property
from django_filters.rest_framework import (
    CharFilter,
    DjangoFilterBackend,
    FilterSet,
)
from rest_framework import (
    filters,
    mixins,
    permissions,
    serializers,
    status,
    viewsets,
)
from rest_framework.generics import get_object_or_404
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.tokens import AccessToken

from api.permissions import (
    AdminOrReadOnly,
    IsAdmin,
    IsAdminOrModeratorOrAuthorOrReadOnly,
    MePermission,
)
from api.sendmail import send_mail_code
from api.serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    ReviewSerializer,
    SignUpSerializer,
    TitleReadSerializer,
    TitleWriteSerializer,
    TokenSerializer,
    UserMeSerializer,
    UsernameSerializer,
    UsersSerializer,
)
from reviews.models import Category, Genre, Review, Title
from users.models import CustomUser


class ListCreateDestroyViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    pass


class CategoryViewSet(ListCreateDestroyViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    permission_classes = (AdminOrReadOnly,)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAdminOrModeratorOrAuthorOrReadOnly,)

    @cached_property
    def _review(self) -> QuerySet:
        return get_object_or_404(
            Review,
            pk=self.kwargs.get('review_id'),
            title=self.kwargs.get('title_id'),
        )

    def get_queryset(self) -> QuerySet:
        return self._review.comments.all()

    def perform_create(
        self,
        serializer: serializers.ModelSerializer,
    ) -> None:
        serializer.save(author=self.request.user, review=self._review)


class GenreViewSet(ListCreateDestroyViewSet):
    serializer_class = GenreSerializer
    queryset = Genre.objects.all()
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    permission_classes = (AdminOrReadOnly,)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsAdminOrModeratorOrAuthorOrReadOnly,)

    @cached_property
    def _title(self) -> QuerySet:
        return get_object_or_404(Title, pk=self.kwargs.get('title_id'))

    def get_queryset(self) -> QuerySet:
        return self._title.reviews.all()

    def perform_create(
        self,
        serializer: serializers.ModelSerializer,
    ) -> None:
        serializer.save(author=self.request.user, title=self._title)


class TitleFilter(FilterSet):
    category = CharFilter(field_name='category__slug')
    genre = CharFilter(field_name='genre__slug')

    class Meta:
        model = Title
        fields = ('name', 'year', 'category', 'genre')


class TitleViewSet(viewsets.ModelViewSet):
    http_method_names = [
        'get',
        'post',
        'patch',
        'delete',
        'head',
        'options',
        'trace',
    ]
    queryset = Title.objects.annotate(rating=Avg('reviews__score')).order_by(
        'name',
    )
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    permission_classes = (AdminOrReadOnly,)

    def get_serializer_class(self) -> serializers.ModelSerializer:
        if self.action in ['list', 'retrieve']:
            return TitleReadSerializer
        return TitleWriteSerializer


class SignUpView(APIView):
    """Отправка письма с кодом подтверждения на email."""

    permission_classes = (permissions.AllowAny,)

    def post(self, request: Request) -> Response:
        user = CustomUser.objects.filter(
            username=request.data.get('username'),
        ).first()
        if user:
            email = getattr(user, 'email')
            if request.data.get('email') != email:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            user.confirmation_code = send_mail_code(user)
            user.save()
            return Response(status=status.HTTP_200_OK)
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        serializer.save(confirmation_code=send_mail_code(user))
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class TokenView(APIView):
    """Получение JWT-токена в обмен на username и confirmation code."""

    permission_classes = (permissions.AllowAny,)

    def post(self, request: Request) -> Response:
        serializer = TokenSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )
        username = serializer.data['username']
        user = get_object_or_404(CustomUser, username=username)
        confirmation_code = serializer.data['confirmation_code']
        if user.confirmation_code != confirmation_code:
            return Response(
                {'Код подтверждения не верен'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        token = AccessToken.for_user(user)
        return Response({'token': str(token)}, status=status.HTTP_200_OK)


class UsersViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdmin,)
    queryset = CustomUser.objects.all()
    serializer_class = UsersSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)


class UsernameViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    permission_classes = (IsAdmin,)
    lookup_field = 'username'
    queryset = CustomUser.objects.all()
    serializer_class = UsernameSerializer


class UserMeViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    GenericViewSet,
):
    permission_classes = (MePermission,)
    queryset = CustomUser.objects.all()
    serializer_class = UsernameSerializer

    def get_object(self) -> QuerySet:
        queryset = self.filter_queryset(self.get_queryset())
        user = queryset.get(username=self.request.user)
        self.check_object_permissions(self.request, user)
        return user

    def get_serializer_class(self) -> Type[serializers.ModelSerializer]:
        if self.action == 'retrieve':
            return UsernameSerializer
        return UserMeSerializer
