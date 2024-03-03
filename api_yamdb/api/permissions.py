from django.db.models import Model, QuerySet
from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.viewsets import ModelViewSet


class IsAdmin(permissions.BasePermission):
    """Проверка прав доступа для администратора."""

    def has_permission(self, request: Request, view: QuerySet) -> bool:
        user = request.user
        return user.is_authenticated and user.is_admin or user.is_superuser

    def has_object_permission(
        self,
        request: Request,
        view: QuerySet,
        obj: QuerySet,
    ) -> bool:
        user = request.user
        return user.is_authenticated and user.is_admin or user.is_superuser


class AdminOrReadOnly(permissions.BasePermission):
    """Полный доступ предоставляется администратору,
    остальным - только для чтения."""

    def has_permission(self, request: Request, view: QuerySet) -> bool:
        return request.method in permissions.SAFE_METHODS or (
            request.user.is_authenticated
            and request.user.is_admin
            or request.user.is_superuser
        )


class IsModerator(permissions.BasePermission):
    """Проверка прав доступа для модератора."""

    def has_permission(self, request: Request, view: QuerySet) -> bool:
        user = request.user
        return user.is_authenticated and user.is_moderator

    def has_object_permission(
        self,
        request: Request,
        view: QuerySet,
        obj: QuerySet,
    ) -> bool:
        user = request.user
        return (
            request.method in permissions.SAFE_METHODS
            or user.is_authenticated
            and user.is_moderator
            and (
                obj.__class__.__name__ == 'Review'
                or obj.__class__.__name__ == 'Comment'
            )
        )


class IsAdminOrModeratorOrAuthorOrReadOnly(permissions.BasePermission):
    def has_permission(self, request: Request, view: QuerySet) -> bool:
        user = request.user
        if not user.is_authenticated:
            return request.method in permissions.SAFE_METHODS
        return True

    def has_object_permission(
        self,
        request: Request,
        view: ModelViewSet,
        obj: Model,
    ) -> bool:
        del view
        user = request.user
        if not user.is_authenticated:
            return request.method in permissions.SAFE_METHODS
        return (
            request.method in permissions.SAFE_METHODS
            or request.method == 'POST'
            or request.method in ('PATCH', 'DELETE')
            and (user == obj.author or user.is_moderator or user.is_admin)
        )


class MePermission(permissions.BasePermission):
    """Обеспечивает доступ к users/me только текущему юзеру."""

    def has_permission(self, request: Request, view: QuerySet) -> bool:
        user = request.user
        return user.is_authenticated

    def has_object_permission(
        self,
        request: Request,
        view: QuerySet,
        obj: QuerySet,
    ) -> bool:
        user = request.user
        return user.username == obj.username
