import uuid

from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class UpdatedCreatedMixin(models.Model):
    created_at = models.DateTimeField(_('дата создания'), auto_now_add=True)
    updated_at = models.DateTimeField(_('дата обновления'), auto_now=True)

    class Meta:
        abstract = True


class Person(UpdatedCreatedMixin):
    id = models.UUIDField(_('идентификатор'), primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.TextField(_('полное имя'), max_length=50, null=False)
    birth_date = models.DateField(_('дата рождения'))

    class Meta:
        db_table = '"content"."person"'
        verbose_name = _('участник')
        verbose_name_plural = _('участники')

    def __str__(self):
        return self.full_name


class Genre(UpdatedCreatedMixin):
    id = models.UUIDField(_('идентификатор'), primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField(_('название'), max_length=50, null=False)
    description = models.TextField(_('описание'), blank=True, max_length=255)

    class Meta:
        db_table = '"content"."genre"'
        verbose_name = _('жанр')
        verbose_name_plural = _('жанры')

    def __str__(self):
        return self.name


class FilmWorkType(models.TextChoices):
    MOVIE = 'movie', _('фильм')
    TV_SHOW = 'tv_show', _('шоу')


class FilmWork(UpdatedCreatedMixin):
    id = models.UUIDField(_('идентификатор'), primary_key=True, default=uuid.uuid4, editable=False)
    title = models.TextField(_('название'), max_length=255, null=False)
    description = models.TextField(_('описание'), blank=True, max_length=255)
    creation_date = models.DateField(_('дата создания фильма'), blank=True)
    certificate = models.TextField(_('сертификат'), blank=True)
    file_path = models.FileField(_('файл'), upload_to='film_works/', blank=True)
    rating = models.FloatField(_('рейтинг'), validators=[MinValueValidator(0)], blank=True)
    type = models.TextField(_('тип'), max_length=20, choices=FilmWorkType.choices, null=False)
    genres = models.ManyToManyField(Genre, through='GenreFilmWork')
    persons = models.ManyToManyField(Person, through='PersonFilmWork')

    class Meta:
        db_table = '"content"."film_work"'
        verbose_name = _('кинопроизведение')
        verbose_name_plural = _('кинопроизведения')

    def __str__(self):
        return self.title


class GenreFilmWork(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    film_work_id = models.ForeignKey(FilmWork, on_delete=models.CASCADE, db_column='film_work_id')
    genre_id = models.ForeignKey(Genre, on_delete=models.CASCADE, db_column='genre_id')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = '"content"."genre_film_work"'


class Role(models.TextChoices):
    DIRECTOR = 'director', _('режиссёр')
    WRITER = 'writer', _('сценарист')
    ACTOR = 'actor', _('актёр')


class PersonFilmWork(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    film_work_id = models.ForeignKey(FilmWork, on_delete=models.CASCADE, db_column='film_work_id')
    person_id = models.ForeignKey(Person, on_delete=models.CASCADE, db_column='person_id')
    role = models.TextField(choices=Role.choices, max_length=20, null=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = '"content"."person_film_work"'
