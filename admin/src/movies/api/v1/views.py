from django.http import Http404
from django.views.generic.detail import BaseDetailView
from django.views.generic.list import BaseListView

from movies.api.mixins import MoviesApiMixin


class MoviesDetailsApi(MoviesApiMixin, BaseDetailView):
    http_method_names = ['get']

    def get_object(self, queryset=None):
        pk = self.kwargs.get(self.pk_url_kwarg)

        if pk is None:
            raise Http404('No found matching the query')

        movie = self.get_queryset().get(id=pk)
        return movie

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data()
        return self.render_to_response(context)

    def get_context_data(self, *, object_list=None, **kwargs) -> dict:
        return self.object


class MoviesListApi(MoviesApiMixin, BaseListView):
    http_method_names = ['get']
    paginate_by = 50

    def get_context_data(self, *, object_list=None, **kwargs) -> dict:
        _, page, *_ = self.paginate_queryset(queryset=self.get_queryset(), page_size=self.paginate_by)

        context = {
            'count': page.paginator.count,
            'total_pages': page.paginator.num_pages,
            'prev': page.previous_page_number() if page.has_previous() else None,
            'next': page.next_page_number() if page.has_next() else None,
            'results': list(page.object_list),
        }
        return context
