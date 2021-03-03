from django.contrib import admin

from .models import FilmWork, Genre, Person, PersonFilmWork


class PersonFilmWorkInline(admin.TabularInline):
    model = PersonFilmWork


@admin.register(FilmWork)
class FilmWorkAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'creation_date', 'rating')
    fields = ('title', 'type', 'description', 'creation_date', 'certificate', 'file_path', 'rating')
    list_filter = ('type',)
    search_fields = ('title', 'description')
    inlines = [PersonFilmWorkInline]


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    inlines = [PersonFilmWorkInline]
