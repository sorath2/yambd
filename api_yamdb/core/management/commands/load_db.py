import csv
from typing import Dict

from django.contrib.auth.base_user import AbstractBaseUser
from django.core.management.base import BaseCommand

from reviews.models import (
    Category,
    Comment,
    Genre,
    GenreTitle,
    Review,
    Title,
    User,
)


class Command(BaseCommand):
    help = 'Loads data from csv files'

    def handle(self, *args: tuple, **options: dict) -> None:
        UsersLoader().read()
        CategoryLoader().read()
        GenreLoader().read()
        TitleLoader().read()
        GenreTitleLoader().read()
        ReviewLoader().read()
        CommentLoader().read()


class CsvLoader:
    def get_file_name(self) -> str:
        assert isinstance(self.file_name, str), (
            "'%s' should either include a `file_name` attribute, "
            "or override the `get_file_name()` method."
            % self.__class__.__name__
        )
        return self.file_name

    def read(self) -> None:
        file_name = self.get_file_name()
        print(f'load data from {file_name}')
        with open(file_name) as file:
            reader = csv.DictReader(file)
            for row in reader:
                instance = self.parse(row)
                instance.save()


class UsersLoader(CsvLoader):
    file_name = 'static/data/users.csv'

    def parse(self, data: Dict[str, str]) -> AbstractBaseUser:
        instance = User(
            id=data.get('id'),
            username=data.get('username'),
            email=data.get('email'),
            role=data.get('role'),
            bio=data.get('bio'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
        )
        return instance


class CategoryLoader(CsvLoader):
    file_name = 'static/data/category.csv'

    def parse(self, data: Dict[str, str]) -> Category:
        instance = Category(
            id=data.get('id'),
            name=data.get('name'),
            slug=data.get('slug'),
        )
        return instance


class GenreLoader(CsvLoader):
    file_name = 'static/data/genre.csv'

    def parse(self, data: Dict[str, str]) -> Genre:
        instance = Genre(
            id=data.get('id'),
            name=data.get('name'),
            slug=data.get('slug'),
        )
        return instance


class TitleLoader(CsvLoader):
    file_name = 'static/data/titles.csv'

    def parse(self, data: Dict[str, str]) -> Title:
        instance = Title(
            id=data.get('id'),
            name=data.get('name'),
            year=data.get('year'),
            category_id=data.get('category'),
        )
        return instance


class GenreTitleLoader(CsvLoader):
    file_name = 'static/data/genre_title.csv'

    def parse(self, data: Dict[str, str]) -> GenreTitle:
        instance = GenreTitle(
            id=data.get('id'),
            title_id=data.get('title_id'),
            genre_id=data.get('genre_id'),
        )
        return instance


class ReviewLoader(CsvLoader):
    file_name = 'static/data/review.csv'

    def parse(self, data: Dict[str, str]) -> Review:
        instance = Review(
            id=data.get('id'),
            title_id=data.get('title_id'),
            text=data.get('text'),
            author_id=data.get('author'),
            score=data.get('score'),
            pub_date=data.get('pub_date'),
        )
        return instance


class CommentLoader(CsvLoader):
    file_name = 'static/data/comments.csv'

    def parse(self, data: Dict[str, str]) -> Comment:
        instance = Comment(
            id=data.get('id'),
            review_id=data.get('review_id'),
            text=data.get('text'),
            author_id=data.get('author'),
            pub_date=data.get('pub_date'),
        )
        return instance
