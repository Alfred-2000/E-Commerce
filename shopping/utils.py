from utilities import filtersets as UtilitiesFilters
from shopping import models as ShoppingModels
from shopping import constants as ShoppingConstants


class ProductListingFilterSet(UtilitiesFilters.GenericModelFilterSet):
    class Meta:
        model = ShoppingModels.Product
        fields = ShoppingConstants.PRODUCT_SEARCH_AND_FILTER_FIELDS
