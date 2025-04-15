from accounts import utils as AccountsUtils
from django_filters.rest_framework import DjangoFilterBackend
from e_commerce import constants as EcommerceConstants
from rest_framework import decorators, status, viewsets
from rest_framework.filters import SearchFilter
from rest_framework.response import Response

from shopping import constants as ShoppingConstants
from shopping import models as ShoppingModels
from shopping import serializers as ShoppingSerializer
from shopping import utils as ShoppingUtils
from utils.classes import ErrorResponse, HttpMethod, SuccessResponse


class ProductManagementViewSet(viewsets.ModelViewSet):
    authentication_classes = (AccountsUtils.CsrfExemptSessionAuthentication,)
    filter_backends = [DjangoFilterBackend, SearchFilter]
    queryset = ShoppingModels.Product.objects.order_by("-updated_at", "-created_at")
    serializer_class = ShoppingSerializer.ProductSerializer
    filterset_class = ShoppingUtils.ProductListingFilterSet
    search_fields = ShoppingConstants.PRODUCT_SEARCH_AND_FILTER_FIELDS

    @decorators.action(
        detail=False,
        url_path="delete",
        methods=[HttpMethod.DELETE],
    )
    def delete_many(self, request, *args, **kwargs):
        try:
            self.queryset.filter(id__in=request.data["ids"]).delete()
            return Response(
                SuccessResponse(EcommerceConstants.PRODUCTS_DELETED_SUCCESSFULLY),
                status=status.HTTP_204_NO_CONTENT,
            )
        except Exception as error:
            return Response(ErrorResponse(error), status=status.HTTP_400_BAD_REQUEST)


class OrderManagementViewSet(viewsets.ModelViewSet):
    authentication_classes = (AccountsUtils.CsrfExemptSessionAuthentication,)
    filter_backends = [DjangoFilterBackend, SearchFilter]
    queryset = ShoppingModels.Order.objects.order_by("-updated_at", "-created_at")
    serializer_class = ShoppingSerializer.OrderSerializer

    def update(self, request, *args, **kwargs):
        try:
            request_status = request.data.get("order_status")
            if request_status:
                request.data["order_status"] = EcommerceConstants.ORDER_STATUS[
                    int(request_status)
                ]
            return super().update(request, *args, **kwargs)
        except Exception as error:
            return Response(ErrorResponse(error), status=status.HTTP_400_BAD_REQUEST)

    @decorators.action(
        detail=False,
        url_path="delete",
        methods=[HttpMethod.DELETE],
    )
    def delete_many(self, request, *args, **kwargs):
        try:
            self.queryset.filter(id__in=request.data["ids"]).delete()
            return Response(
                SuccessResponse(EcommerceConstants.ORDERS_DELETED_SUCCESSFULLY),
                status=status.HTTP_204_NO_CONTENT,
            )
        except Exception as error:
            return Response(ErrorResponse(error), status=status.HTTP_400_BAD_REQUEST)
