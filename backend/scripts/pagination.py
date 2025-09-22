from rest_framework.pagination import LimitOffsetPagination

#TODO: Add support for the general listing APIs
class GenerationsLimitOffsetPagination(LimitOffsetPagination):
    """
    Custom pagination class for unified generation listing API.
    Provides limit-offset pagination with sensible defaults.
    """
    
    # Default number of items per page when limit is not specified
    default_limit = 20
    
    # Maximum number of items that can be requested per page
    max_limit = 100
    
    # Custom query parameter names (optional - defaults to 'limit' and 'offset')
    limit_query_param = 'limit'
    offset_query_param = 'offset'
