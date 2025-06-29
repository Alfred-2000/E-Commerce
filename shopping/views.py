from rest_framework import decorators, status, viewsets
from rest_framework.response import Response

from accounts import utils as AccountsUtils
from e_commerce import constants as EcommerceConstants
from shopping import constants as ShoppingConstants
from shopping import models as ShoppingModels
from shopping import serializers as ShoppingSerializer
from shopping import utils as ShoppingUtils
from utils.classes import (
    ErrorResponse,
    FilterSearchOrderingMixin,
    GetUserFromTokenMixin,
    HttpMethod,
    SuccessResponse,
)


class ProductManagementViewSet(
    GetUserFromTokenMixin, FilterSearchOrderingMixin, viewsets.ModelViewSet
):
    authentication_classes = (AccountsUtils.CsrfExemptSessionAuthentication,)
    queryset = ShoppingModels.Product.objects.order_by("-updated_at", "-created_at")
    serializer_class = ShoppingSerializer.ProductSerializer
    filterset_class = ShoppingUtils.ProductListingFilterSet
    search_fields = ShoppingConstants.PRODUCT_SEARCH_AND_FILTER_FIELDS

    @decorators.action(
        detail=False,
        url_path="delete",
        methods=[HttpMethod.DELETE],
    )
    def delete_many(self, request, *args, **kwargs) -> Response:
        try:
            self.queryset.filter(id__in=request.data["ids"]).delete()
            return SuccessResponse(
                msg=EcommerceConstants.PRODUCTS_DELETED_SUCCESSFULLY,
                status=status.HTTP_204_NO_CONTENT,
            )
        except Exception as error:
            return ErrorResponse(error=str(error), status=status.HTTP_400_BAD_REQUEST)


class OrderManagementViewSet(
    GetUserFromTokenMixin, FilterSearchOrderingMixin, viewsets.ModelViewSet
):
    authentication_classes = (AccountsUtils.CsrfExemptSessionAuthentication,)
    queryset = ShoppingModels.Order.objects.order_by("-updated_at", "-created_at")
    serializer_class = ShoppingSerializer.OrderSerializer

    def update(self, request, *args, **kwargs) -> Response:
        try:
            request_status = request.data.get("order_status")
            if request_status:
                request.data["order_status"] = EcommerceConstants.ORDER_STATUS[
                    int(request_status)
                ]
            return super().update(request, *args, **kwargs)
        except Exception as error:
            return ErrorResponse(error=str(error), status=status.HTTP_400_BAD_REQUEST)

    @decorators.action(
        detail=False,
        url_path="delete",
        methods=[HttpMethod.DELETE],
    )
    def delete_many(self, request, *args, **kwargs) -> Response:
        try:
            self.queryset.filter(id__in=request.data["ids"]).delete()
            return SuccessResponse(
                msg=EcommerceConstants.ORDERS_DELETED_SUCCESSFULLY,
                status=status.HTTP_204_NO_CONTENT,
            )
        except Exception as error:
            return ErrorResponse(error=str(error), status=status.HTTP_400_BAD_REQUEST)


class CartListManagementViewSet(
    GetUserFromTokenMixin, FilterSearchOrderingMixin, viewsets.ModelViewSet
):
    authentication_classes = (AccountsUtils.CsrfExemptSessionAuthentication,)
    serializer_class = ShoppingSerializer.CartItemsSerializer

    def get_queryset(self):
        CartItems = ShoppingModels.CartItems
        user_obj = self.request.user
        if not user_obj:
            return CartItems.objects.none()
        return CartItems.objects.filter(user=user_obj).order_by(
            "-updated_at", "-created_at"
        )

    @decorators.action(
        detail=False,
        url_path="delete",
        methods=[HttpMethod.DELETE],
    )
    def delete_many(self, request, *args, **kwargs) -> Response:
        try:
            queryset = self.get_queryset()
            deleted_count, _ = queryset.delete()
            return SuccessResponse(
                msg=EcommerceConstants.CARTS_DELETED_SUCCESSFULLY,
                status=status.HTTP_204_NO_CONTENT,
            )
        except Exception as error:
            return ErrorResponse(error=str(error), status=status.HTTP_400_BAD_REQUEST)


class WishListManagementViewSet(FilterSearchOrderingMixin, viewsets.ModelViewSet):
    authentication_classes = (AccountsUtils.CsrfExemptSessionAuthentication,)
    queryset = ShoppingModels.WishlistItems.objects.order_by(
        "-updated_at", "-created_at"
    )
    serializer_class = ShoppingSerializer.WishlistItemsSerializer
