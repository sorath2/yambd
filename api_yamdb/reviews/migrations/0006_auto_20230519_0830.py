# Generated by Django 3.2.19 on 2023-05-19 08:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0005_auto_20230516_1454'),
    ]

    operations = [
        migrations.AddField(
            model_name='title',
            name='genre',
            field=models.ManyToManyField(through='reviews.GenreTitle', to='reviews.Genre'),
        ),
        migrations.AddField(
            model_name='title',
            name='rating',
            field=models.IntegerField(default=0, verbose_name='Рейтинг произведения'),
        ),
        migrations.AlterField(
            model_name='title',
            name='description',
            field=models.TextField(blank=True, default='', verbose_name='Описание произведения'),
        ),
    ]
