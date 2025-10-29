import django_filters
from django.db.models import Q

from .models import Niche, NichePacing, NicheTone


class NicheFilter(django_filters.FilterSet):
    """
    Filter for Niche list view
    """

    search = django_filters.CharFilter(method="filter_search")
    tone = django_filters.CharFilter(method="filter_tone")
    pacing = django_filters.CharFilter(method="filter_pacing")
    script_structure = django_filters.CharFilter(method="filter_script_structure")
    best_for = django_filters.CharFilter(method="filter_best_for")
    status = django_filters.ChoiceFilter(
        choices=[
            ("active", "Active"),
            ("inactive", "Inactive"),
        ]
    )

    class Meta:
        model = Niche
        fields = ["status", "tone", "pacing", "script_structure", "best_for"]

    def filter_search(self, queryset, name, value):
        if value:
            return queryset.filter(
                Q(title__icontains=value) | Q(tagline__icontains=value)
            )
        return queryset

    def filter_tone(self, queryset, name, value):
        if value:
            return queryset.filter(tone__icontains=value)
        return queryset

    def filter_pacing(self, queryset, name, value):
        if value:
            return queryset.filter(pacing__icontains=value)
        return queryset

    def filter_script_structure(self, queryset, name, value):
        if value:
            return queryset.filter(script_structure__icontains=value)
        return queryset

    def filter_best_for(self, queryset, name, value):
        if value:
            return queryset.filter(best_for__icontains=value)
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
