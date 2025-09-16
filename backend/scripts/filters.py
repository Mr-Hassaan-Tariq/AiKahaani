import django_filters
from .models import ScriptOutline, FullScript
from django.db.models import Q, Case, When, Value, CharField, IntegerField, FloatField, BooleanField


class ScriptOutlineFilter(django_filters.FilterSet):
    """
    Filter for Script Outline list view
    """
    search = django_filters.CharFilter(method='filter_search')
    filter_type = django_filters.ChoiceFilter(
        choices=[
            ('all', 'All'),
            ('outline_drafts', 'Outline Drafts'),
            ('script_drafts', 'Script Drafts'),
            ('saved', 'Saved'),
        ],
        method='filter_by_type'
    )

    class Meta:
        model = ScriptOutline
        fields = ['status']

    def filter_search(self, queryset, name, value):
        """
        Search by title or outline_text
        """
        if value:
            return queryset.filter(
                django_filters.Q(title__icontains=value) |
                django_filters.Q(outline_text__icontains=value)
            )
        return queryset

    def filter_by_type(self, queryset, name, value):
        """
        Filter by frontend filter tabs
        """
        if value == 'outline_drafts':
            # Only outlines that are still drafts or generated
            return queryset.filter(status__in=['draft', 'generated'])
        elif value == 'script_drafts':
            # Only outlines that have been converted to scripts
            return queryset.filter(status='saved')
        elif value == 'saved':
            # Only saved outlines
            return queryset.filter(status='saved')
        elif value == 'all':
            # Return all outlines
            return queryset
        return queryset


class FullScriptFilter(django_filters.FilterSet):
    """
    Filter for Full Script list view
    """
    search = django_filters.CharFilter(method='filter_search')
    filter_type = django_filters.ChoiceFilter(
        choices=[
            ('all', 'All'),
            ('outline_drafts', 'Outline Drafts'),
            ('script_drafts', 'Script Drafts'),
            ('saved', 'Saved'),
        ],
        method='filter_by_type'
    )
    word_count_min = django_filters.NumberFilter(field_name='word_count', lookup_expr='gte')
    word_count_max = django_filters.NumberFilter(field_name='word_count', lookup_expr='lte')
    duration_min = django_filters.NumberFilter(field_name='estimated_duration', lookup_expr='gte')
    duration_max = django_filters.NumberFilter(field_name='estimated_duration', lookup_expr='lte')

    class Meta:
        model = FullScript
        fields = ['status', 'is_published']

    def filter_search(self, queryset, name, value):
        """
        Search by title or content
        """
        if value:
            return queryset.filter(
                django_filters.Q(title__icontains=value) |
                django_filters.Q(content__icontains=value)
            )
        return queryset

    def filter_by_type(self, queryset, name, value):
        """
        Filter by frontend filter tabs
        """
        if value == 'script_drafts':
            # Only scripts that are still drafts or generated
            return queryset.filter(status__in=['draft', 'generated'])
        elif value == 'saved':
            # Only saved scripts
            return queryset.filter(status='saved')
        elif value == 'outline_drafts':
            # This doesn't apply to full scripts, return empty queryset
            return queryset.none()
        elif value == 'all':
            # Return all scripts
            return queryset
        return queryset


def generation_filters(search, status_filter, filter_type, type_filter, ordering):
    """
    Applies filters to both outline and script querysets and returns the filtered querysets
    along with the sorting criteria.
    """
    # Build outline queryset
    outline_queryset = ScriptOutline.objects.annotate(
        type=Value('outline', output_field=CharField()),
        word_count=Value(None, output_field=IntegerField()),
        estimated_duration=Value(None, output_field=FloatField()),
        is_published=Value(None, output_field=BooleanField()),
        status_display=Case(
            When(status='draft', then=Value('Draft')),
            When(status='generated', then=Value('Generated')),
            When(status='saved', then=Value('Saved')),
            default=Value('Unknown'),
            output_field=CharField()
        )
    ).values(
        'uuid', 'title', 'type', 'status', 'status_display',
        'word_count', 'estimated_duration', 'created', 'modified',
        'is_published', 'version'
    )

    # Build script queryset
    script_queryset = FullScript.objects.annotate(
        type=Value('script', output_field=CharField()),
        status_display=Case(
            When(status='draft', then=Value('Draft')),
            When(status='generated', then=Value('Generated')),
            When(status='saved', then=Value('Saved')),
            default=Value('Unknown'),
            output_field=CharField()
        )
    ).values(
        'uuid', 'title', 'type', 'status', 'status_display',
        'word_count', 'estimated_duration', 'created', 'modified',
        'is_published', 'version'
    )

    # Apply search filter
    if search:
        outline_queryset = outline_queryset.filter(
            Q(title__icontains=search) | Q(outline_text__icontains=search)
        )
        script_queryset = script_queryset.filter(
            Q(title__icontains=search) | Q(content__icontains=search)
        )

    # Apply status filter
    if status_filter:
        outline_queryset = outline_queryset.filter(status=status_filter)
        script_queryset = script_queryset.filter(status=status_filter)

    # Apply type filter
    if type_filter:
        if type_filter == 'outline':
            script_queryset = script_queryset.none()
        elif type_filter == 'script':
            outline_queryset = outline_queryset.none()

    # Apply filter_type logic
    if filter_type == 'outline_drafts':
        outline_queryset = outline_queryset.filter(status__in=['draft', 'generated'])
        script_queryset = script_queryset.none()
    elif filter_type == 'script_drafts':
        outline_queryset = outline_queryset.none()
        script_queryset = script_queryset.filter(status__in=['draft', 'generated'])
    elif filter_type == 'saved':
        outline_queryset = outline_queryset.filter(status='saved')
        script_queryset = script_queryset.filter(status='saved')

    # Sorting logic
    reverse = ordering.startswith('-')
    field = ordering.lstrip('-')

    if field in ['created', 'modified']:
        combined_queryset = list(outline_queryset) + list(script_queryset)
        combined_queryset.sort(key=lambda x: x[field], reverse=reverse)
    elif field == 'title':
        combined_queryset = list(outline_queryset) + list(script_queryset)
        combined_queryset.sort(key=lambda x: x[field] or '', reverse=reverse)

    return combined_queryset
