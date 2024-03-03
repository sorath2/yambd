from django.contrib import admin

from .models import Category, Comment, Genre, GenreTitle, Review, Title


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'slug',
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'pub_date',
        'text',
        'author',
        'review',
    )


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')


@admin.register(GenreTitle)
class GenreTitleAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'genre',
    )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'pub_date',
        'title',
        'author',
        'text',
        'score',
    )


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'year',
        'category',
    )
