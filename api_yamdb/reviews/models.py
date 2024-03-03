from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

MAX_LENGTH = 256
MAX_SCORE = 10
MIN_SCORE = 1
PREVIEW_LENGTH = 15

User = get_user_model()


class PubDateModel(models.Model):
    pub_date = models.DateTimeField(
        verbose_name='Дата создания',
        auto_now_add=True,
    )

    class Meta:
        abstract = True
        ordering = ('-pub_date',)


class Category(models.Model):
    name = models.CharField(
        verbose_name='Название категории',
        max_length=MAX_LENGTH,
    )
    slug = models.SlugField(
        verbose_name='Слаг категории',
        unique=True,
    )

    class Meta:
        verbose_name = 'Категория произведений'
        verbose_name_plural = 'Категории произведений'
        ordering = ('slug',)

    def __str__(self) -> str:
        return self.name


class Genre(models.Model):
    name = models.CharField(
        verbose_name='Название жанра',
        max_length=MAX_LENGTH,
    )
    slug = models.SlugField(
        verbose_name='Слаг жанра',
        unique=True,
    )

    class Meta:
        verbose_name = 'Жанр произведения'
        verbose_name_plural = 'Жанры произведений'
        ordering = ('slug',)

    def __str__(self) -> str:
        return self.name


class Title(models.Model):
    name = models.CharField(
        verbose_name='Название произведения',
        max_length=MAX_LENGTH,
    )
    year = models.PositiveSmallIntegerField(
        db_index=True,
        verbose_name='Год создания произведения',
    )
    description = models.TextField(
        verbose_name='Описание произведения',
        blank=True,
    )
    category = models.ForeignKey(
        verbose_name='Категория произведения',
        to='Category',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='titles',
    )
    genre = models.ManyToManyField(Genre, through='GenreTitle')

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ('name',)

    def __str__(self) -> str:
        return self.name


class GenreTitle(models.Model):
    title = models.ForeignKey(
        verbose_name='Произведение',
        to=Title,
        on_delete=models.CASCADE,
        related_name='genres',
    )
    genre = models.ForeignKey(
        verbose_name='Жанр',
        to=Genre,
        on_delete=models.CASCADE,
        related_name='titles',
    )

    class Meta:
        verbose_name = 'Связь жанра и произведения'
        verbose_name_plural = 'Связи жанров и произведений'
        constraints = [
            models.UniqueConstraint(
                fields=('title', 'genre'),
                name='unique_genre_title',
            ),
        ]
        ordering = ('title',)

    def __str__(self) -> str:
        return f'{self.title} - {self.genre}'


class Review(PubDateModel):
    text = models.TextField(
        verbose_name='Текст отзыва',
    )
    score = models.PositiveSmallIntegerField(
        verbose_name='Рейтинг',
        validators=[
            MinValueValidator(MIN_SCORE),
            MaxValueValidator(MAX_SCORE),
        ],
    )
    title = models.ForeignKey(
        verbose_name='Произведение',
        to=Title,
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    author = models.ForeignKey(
        verbose_name='Автор отзыва',
        to=User,
        on_delete=models.CASCADE,
        related_name='reviews',
    )

    class Meta(PubDateModel.Meta):
        verbose_name = 'Отзыв на произведение'
        verbose_name_plural = 'Отзывы на произведения'
        constraints = [
            models.UniqueConstraint(
                fields=('title_id', 'author_id'),
                name='unique_title_author',
            ),
        ]

    def __str__(self) -> str:
        return self.text[:PREVIEW_LENGTH]


class Comment(PubDateModel):
    text = models.TextField(verbose_name='Текст комментария')
    review = models.ForeignKey(
        verbose_name='Отзыв на произведение',
        to=Review,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    author = models.ForeignKey(
        verbose_name='Автор комментария',
        to=User,
        on_delete=models.CASCADE,
        related_name='comments',
    )

    class Meta(PubDateModel.Meta):
        verbose_name = 'Комментарий к отзыву на произведение'
        verbose_name_plural = 'Комментарии к отзывам на произведения'

    def __str__(self) -> str:
        return self.text[:PREVIEW_LENGTH]
