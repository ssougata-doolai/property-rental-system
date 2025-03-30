from django_filters import rest_framework as filters
from mess.models import Mess

class MessFilter(filters.FilterSet):
    min_price = filters.NumberFilter(field_name='rooms__expected_rent_per_person', lookup_expr='gte')
    max_price = filters.NumberFilter(field_name='rooms__expected_rent_per_person', lookup_expr='lte')

    class Meta:
        model = Mess
        fields = ['min_price', 'max_price']
