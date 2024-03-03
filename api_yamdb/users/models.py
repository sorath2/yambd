from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models

MAX_LENGTH_USERNAME = 150
MAX_LENGTH_EMAIL = 254
MAX_LENGHT_CONFORMATION_CODE = 50


def validate_user(value: str) -> None:
    """Проверка поля username."""

    if value.lower() == 'me':
        raise ValidationError('Использовать имя <me> запрещено.')


class CustomUser(AbstractUser):
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER = 'user'

    ROLES = (
        (ADMIN, 'Admin'),
        (MODERATOR, 'Moderator'),
        (USER, 'User'),
    )

    username = models.CharField(
        max_length=MAX_LENGTH_USERNAME,
        verbose_name='Логин',
        help_text='Укажите логин',
        unique=True,
        validators=[validate_user],
    )

    email = models.EmailField(
        max_length=MAX_LENGTH_EMAIL,
        verbose_name='Email address',
        help_text='Укажите email',
        unique=True,
        null=False,
    )

    first_name = models.CharField(
        max_length=MAX_LENGTH_USERNAME,
        verbose_name='Имя',
        help_text='Укажите Имя',
        blank=True,
    )

    last_name = models.CharField(
        max_length=MAX_LENGTH_USERNAME,
        verbose_name='Фамилия',
        help_text='Укажите Фамилию',
        blank=True,
    )

    bio = models.TextField(
        verbose_name='Биография',
        help_text='Укажите Биографию',
        blank=True,
    )

    role = models.CharField(
        max_length=MAX_LENGTH_USERNAME,
        verbose_name='Роль',
        choices=ROLES,
        default='user',
        help_text='Уровень доступа',
    )

    confirmation_code = models.CharField(
        max_length=MAX_LENGHT_CONFORMATION_CODE,
        blank=True,
        verbose_name='Код подтверждения',
    )

    @property
    def is_admin(self) -> bool:
        return self.is_superuser or self.role == self.ADMIN

    @property
    def is_moderator(self) -> bool:
        return self.is_admin or self.role == self.MODERATOR

    @property
    def is_user(self) -> bool:
        return self.is_moderator or self.role == self.USER

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self) -> str:
        return self.username
