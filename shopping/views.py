import logging
from datetime import datetime

import pytz
from accounts import utils as AccountsUtils
from e_commerce import constants as EcommerceConstants
from e_commerce import settings as EcommerceSettings
from rest_framework import generics, status, viewsets, decorators
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

from shopping import models as ShoppingModels
from shopping import serializers as ShoppingSerializer
from utilities.classes import SuccessResponse, ErrorResponse
from shopping import constants as ShoppingConstants
from shopping import utils as ShoppingUtils
from utilities.classes import HttpMethod


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


class ListCreateOrders(generics.ListCreateAPIView):
    authentication_classes = (AccountsUtils.CsrfExemptSessionAuthentication,)
    queryset = ShoppingModels.Order.objects.all()
    serializer_class = ShoppingSerializer.OrderSerializer

    def get(self, request):
        query_dict = {}
        jwt_token = request.META["HTTP_AUTHORIZATION"]
        user_details = AccountsUtils.encode_decode_jwt_token(
            jwt_token, convertion_type=EcommerceConstants.DECODE
        )
        request.username = user_details["username"]
        query_dict["user_id"] = user_details["id"]
        queryset = self.queryset.filter(**query_dict)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ShoppingSerializer.OrderSerializer(
                page, many=True, context={"request": request}
            )
            result = self.get_paginated_response(serializer.data)
            return result

    def post(self, request, **kwargs):
        try:
            jwt_token = request.META["HTTP_AUTHORIZATION"]
            user_details = AccountsUtils.encode_decode_jwt_token(
                jwt_token, convertion_type=EcommerceConstants.DECODE
            )
            request.username = user_details["username"]
            current_time = AccountsUtils.get_current_timestamp_of_timezone(
                EcommerceSettings.TIME_ZONE
            )
            request.data["date_placed"] = datetime.fromtimestamp(
                current_time, pytz.timezone(EcommerceSettings.TIME_ZONE)
            ).strftime("%Y-%m-%d %H:%M:%S")
            request.data["status"] = EcommerceConstants.ORDER_STATUS[
                1
            ]  # For order Placed
            request.data["user_id"] = user_details["id"]
            order_serializer = ShoppingSerializer.OrderSerializer(
                data=request.data, context={"request": request}
            )
            if order_serializer.is_valid():
                order_serializer.save()
                # orderitem_serializer = OrderItemSerializer(data = orderitems_data, context = {'request':request})
                # if orderitem_serializer.is_valid():
                #     orderitem_serializer.save()
                # else:
                return Response(
                    SuccessResponse(EcommerceConstants.ORDER_ADDED_SUCCESSFULLY),
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    ErrorResponse(order_serializer.errors),
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as error:
            return Response(ErrorResponse(error), status=status.HTTP_400_BAD_REQUEST)


class RetrieveUpdateDeleteOrders(APIView):
    authentication_classes = (AccountsUtils.CsrfExemptSessionAuthentication,)
    queryset = ShoppingModels.Order.objects.all()
    serializer_class = ShoppingSerializer.OrderSerializer

    def get(self, request, **kwargs):
        try:
            queryset = self.queryset.get(id=kwargs["order_id"])
            serialized_data = ShoppingSerializer.OrderSerializer(
                queryset, context={"request": request}
            ).data
            return Response(serialized_data, status=status.HTTP_200_OK)
        except Exception as error:
            return Response(ErrorResponse(error), status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, **kwargs):
        try:
            order_query = self.queryset.filter(id=kwargs["order_id"])
            if order_query:
                if request.data.get("status"):
                    request.data["status"] = EcommerceConstants.ORDER_STATUS[
                        int(request.data.get("status"))
                    ]

                order_object = order_query.get()
                serializer = ShoppingSerializer.OrderSerializer(
                    order_object,
                    data=request.data,
                    partial=True,
                    context={"request": request},
                )
                if serializer.is_valid():
                    serializer.save()
                    if request.data.get("quantity"):
                        # OrderItem.objects.filter(order_id=kwargs['order_id']).update(quantity  = request.data['quantity'])
                        pass
                    return Response(
                        SuccessResponse(EcommerceConstants.ORDER_UPDATED_SUCCESSFULLY),
                        status=status.HTTP_200_OK,
                    )
                else:
                    return Response(
                        ErrorResponse(serializer.errors),
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            else:
                return Response(
                    ErrorResponse(EcommerceConstants.ORDER_DOESNT_EXISTS),
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as error:
            return Response(ErrorResponse(error), status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, **kwargs):
        try:
            order_query = self.queryset.filter(id=kwargs["order_id"])
            if order_query:
                order_query.delete()
                return Response(
                    SuccessResponse(EcommerceConstants.ORDER_DELETED_SUCCESSFULLY),
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    ErrorResponse(EcommerceConstants.ORDER_DOESNT_EXISTS),
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as error:
            return Response(ErrorResponse(error), status=status.HTTP_400_BAD_REQUEST)
