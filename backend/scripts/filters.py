import django_filters
from .models import ScriptOutline, FullScript


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
            # Only outlines that haven't been converted to scripts yet
            return queryset.filter(status__in=['generating', 'generated', 'edited', 'approved'])
        elif value == 'script_drafts':
            # Only outlines that have been converted to scripts
            return queryset.filter(status='script_generated')
        elif value == 'saved':
            # Only approved/saved outlines
            return queryset.filter(status__in=['approved', 'script_generated'])
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
            # Only scripts that are still in draft (not finalized/published)
            return queryset.filter(status__in=['generating', 'generated', 'edited'])
        elif value == 'saved':
            # Only finalized/published scripts
            return queryset.filter(status__in=['finalized', 'published'])
        elif value == 'outline_drafts':
            # This doesn't apply to full scripts, return empty queryset
            return queryset.none()
        elif value == 'all':
            # Return all scripts
            return queryset
        return queryset
