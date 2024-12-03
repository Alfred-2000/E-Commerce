import logging
from datetime import datetime

import pytz
from accounts import utils as AccountsUtils
from e_commerce import constants as EcommerceConstants
from e_commerce import settings as EcommerceSettings
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from shopping import models as ShoppingModels
from shopping.serializers import OrderSerializer, ProductSerializer


class ListCreateProducts(generics.ListCreateAPIView):
    authentication_classes = (AccountsUtils.CsrfExemptSessionAuthentication,)
    queryset = ShoppingModels.Product.objects.all().order_by("-created_at")
    serializer_class = ProductSerializer

    def get(self, request):
        query_dict = {}
        queryset = self.queryset.filter(**query_dict).all()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ProductSerializer(
                page, many=True, context={"request": request}
            )
            result = self.get_paginated_response(serializer.data)
            return result

    def post(self, request, **kwargs):
        try:
            if ShoppingModels.Product.objects.filter(
                name=request.data["name"]
            ).exists():
                response = {
                    "error": EcommerceConstants.PRODUCT_ALREADY_EXISTS,
                }
                return Response(response, status=status.HTTP_400_BAD_REQUEST)

            current_time = AccountsUtils.get_current_timestamp_of_timezone(
                EcommerceSettings.TIME_ZONE
            )
            request.data["created_at"] = datetime.fromtimestamp(
                current_time, pytz.timezone(EcommerceSettings.TIME_ZONE)
            ).strftime("%Y-%m-%d %H:%M:%S")
            serializer = ProductSerializer(
                data=request.data, context={"request": request}
            )
            if serializer.is_valid():
                serializer.save()
                response = {"message": EcommerceConstants.PRODUCT_ADDED_SUCCESSFULLY}
                return Response(response, status=status.HTTP_201_CREATED)
            else:
                response = {"error": serializer.errors}
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)


class RetrieveUpdateDeleteProducts(APIView):
    authentication_classes = (AccountsUtils.CsrfExemptSessionAuthentication,)
    queryset = ShoppingModels.Product.objects.all().order_by("-created_at")
    serializer_class = ProductSerializer

    def get(self, request, **kwargs):
        try:
            product_id = kwargs["product_id"]
            queryset = self.queryset.get(id=product_id)
            serialized_data = ProductSerializer(queryset).data
            return Response(serialized_data, status=status.HTTP_200_OK)
        except Exception as error:
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, **kwargs):
        try:
            product_query = self.queryset.filter(id=kwargs["product_id"])
            if product_query:
                current_time = AccountsUtils.get_current_timestamp_of_timezone(
                    EcommerceSettings.TIME_ZONE
                )
                request.data["date_updated"] = datetime.fromtimestamp(
                    current_time, pytz.timezone(EcommerceSettings.TIME_ZONE)
                ).strftime("%Y-%m-%d %H:%M:%S")
                product_object = product_query.get()
                serializer = ProductSerializer(
                    product_object,
                    data=request.data,
                    partial=True,
                    context={"request": request},
                )
                if serializer.is_valid():
                    serializer.save()
                    response = {
                        "message": EcommerceConstants.PRODUCT_UPDATED_SUCCESSFULLY
                    }
                    return Response(status=status.HTTP_200_OK)
                else:
                    response = {"error": serializer.errors}
                    return Response(response, status=status.HTTP_400_BAD_REQUEST)
            else:
                response = {
                    "error": EcommerceConstants.PRODUCT_DOESNT_EXISTS,
                }
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, **kwargs):
        try:
            product_query = self.queryset.filter(id=kwargs["product_id"])
            if product_query:
                product_query.delete()
                response = {"message": EcommerceConstants.PRODUCT_DELETED_SUCCESSFULLY}
                return Response(response, status=status.HTTP_200_OK)
            else:
                response = {
                    "error": EcommerceConstants.PRODUCT_DOESNT_EXISTS,
                }
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)


class ListCreateOrders(generics.ListCreateAPIView):
    authentication_classes = (AccountsUtils.CsrfExemptSessionAuthentication,)
    queryset = ShoppingModels.Order.objects.all()
    serializer_class = OrderSerializer

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
            serializer = OrderSerializer(page, many=True, context={"request": request})
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
            order_serializer = OrderSerializer(
                data=request.data, context={"request": request}
            )
            if order_serializer.is_valid():
                order_serializer.save()
                # orderitem_serializer = OrderItemSerializer(data = orderitems_data, context = {'request':request})
                # if orderitem_serializer.is_valid():
                #     orderitem_serializer.save()
                #     response = {"status": HTTP_201_CREATED, "message": ORDER_ADDED_SUCCESSFULLY, "data": order_serializer.data}
                # else:
                response = {"message": EcommerceConstants.ORDER_ADDED_SUCCESSFULLY}
                return Response(response, status=status.HTTP_200_OK)
            else:
                response = {
                    "error": order_serializer.errors,
                }
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)


class RetrieveUpdateDeleteOrders(APIView):
    authentication_classes = (AccountsUtils.CsrfExemptSessionAuthentication,)
    queryset = ShoppingModels.Order.objects.all()
    serializer_class = OrderSerializer

    def get(self, request, **kwargs):
        try:
            queryset = self.queryset.get(id=kwargs["order_id"])
            serialized_data = OrderSerializer(
                queryset, context={"request": request}
            ).data
            return Response(serialized_data, status=status.HTTP_200_OK)
        except Exception as error:
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, **kwargs):
        try:
            order_query = self.queryset.filter(id=kwargs["order_id"])
            if order_query:
                if request.data.get("status"):
                    request.data["status"] = EcommerceConstants.ORDER_STATUS[
                        int(request.data.get("status"))
                    ]

                order_object = order_query.get()
                serializer = OrderSerializer(
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
                    response = {
                        "message": EcommerceConstants.ORDER_UPDATED_SUCCESSFULLY
                    }
                    return Response(response, status=status.HTTP_200_OK)
                else:
                    response = {"error": serializer.errors}
                    return Response(response, status=status.HTTP_400_BAD_REQUEST)
            else:
                response = {
                    "error": EcommerceConstants.ORDER_DOESNT_EXISTS,
                }
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, **kwargs):
        try:
            order_query = self.queryset.filter(id=kwargs["order_id"])
            if order_query:
                order_query.delete()
                response = {
                    "message": EcommerceConstants.ORDER_DELETED_SUCCESSFULLY,
                }
                return Response(response, status=status.HTTP_200_OK)
            else:
                response = {
                    "error": EcommerceConstants.ORDER_DOESNT_EXISTS,
                }
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)
