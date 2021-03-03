from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q
from django.http import JsonResponse

from movies.models import FilmWork, Role


class MoviesApiMixin:
    model = FilmWork

    def _get_person_array(self, role):
        return ArrayAgg(
            'personfilmwork__person_id__full_name',
            filter=Q(personfilmwork__role=role),
            distinct=True
        )

    def get_queryset(self):
        values = ['id', 'title', 'description', 'creation_date', 'rating', 'type']

        movie_data = self.model.objects.values(*values).annotate(
            genres=ArrayAgg('genrefilmwork__genre_id__name', distinct=True),
            actors=self._get_person_array(Role.ACTOR),
            directors=self._get_person_array(Role.DIRECTOR),
            writers=self._get_person_array(Role.WRITER)).order_by('title')

        return movie_data

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)
