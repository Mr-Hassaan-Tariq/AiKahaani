import django_filters
from django.db.models import Q

from .models import Niche, NichePacing, NicheTone


class NicheFilter(django_filters.FilterSet):
    """
    Filter for Niche list view
    """

    search = django_filters.CharFilter(method="filter_search")
    status = django_filters.ChoiceFilter(
        choices=[
            ("active", "Active"),
            ("inactive", "Inactive"),
        ]
    )

    class Meta:
        model = Niche
        fields = ["status"]

    def filter_search(self, queryset, name, value):
        """
        Search by title or tagline
        """
        if value:
            return queryset.filter(
                Q(title__icontains=value) | Q(tagline__icontains=value)
            )
        return queryset


class NicheToneFilter(django_filters.FilterSet):
    """
    Filter for NicheTone list view
    """

    search = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = NicheTone
        fields = []

    def filter_search(self, queryset, name, value):
        """
        Search by name
        """
        if value:
            return queryset.filter(name__icontains=value)
        return queryset


class NichePacingFilter(django_filters.FilterSet):
    """
    Filter for NichePacing list view
    """

    search = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = NichePacing
        fields = []

    def filter_search(self, queryset, name, value):
        """
        Search by name
        """
        if value:
            return queryset.filter(name__icontains=value)
        return queryset
