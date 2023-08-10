
import logging, pytz
from datetime import datetime
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import(
    HTTP_400_BAD_REQUEST,
    HTTP_201_CREATED,
    HTTP_200_OK,
)
from accounts.utils import(
    encode_decode_jwt_token,
    get_current_timestamp_of_timezone,
)
from shopping.models import Product, Order, OrderItem
from e_commerce.constants import (
    ENCODE,
    DECODE,
    ORDER_STATUS,
    PRODUCT_ADDED_SUCCESSFULLY,
    PRODUCTS_LISTED_SUCCESSFULLY,
    PRODUCT_DELETED_SUCCESSFULLY,
    PRODUCT_DETAILS_LISTED_SUCCESSFULLY,
    PRODUCT_UPDATED_SUCCESSFULLY,
    PRODUCT_DOESNT_EXISTS,
    ORDER_ADDED_SUCCESSFULLY,
    ORDER_DELETED_SUCCESSFULLY,
    ORDER_DETAILS_LISTED_SUCCESSFULLY,
    ORDER_DOESNT_EXISTS,
    ORDER_UPDATED_SUCCESSFULLY,
    ORDERS_LISTED_SUCCESSFULLY,
    USER_DOSENT_EXISTS,
)
from e_commerce.settings import TIME_ZONE
from accounts.models import User
from shopping.serializers import ProductSerializer, OrderSerializer, OrderItemSerializer
from rest_framework.generics import ListCreateAPIView


class ListCreateProducts(ListCreateAPIView):
    queryset = Product.objects.all().order_by('-date_created')
    serializer_class = ProductSerializer

    def get(self, request):
        query_dict = {}
        queryset  = Product.objects.filter(**query_dict).all()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ProductSerializer(page, many=True, context = {'request': request})
            result = self.get_paginated_response(serializer.data)
            return result


    def post(self, request, **kwargs):
        try:
            current_time = get_current_timestamp_of_timezone(TIME_ZONE)
            request.data['date_created'] = datetime.fromtimestamp(current_time, pytz.timezone(TIME_ZONE)).strftime("%Y-%m-%d %H:%M:%S")
            serializer = ProductSerializer(data = request.data, context = {'request': request})
            if serializer.is_valid():
                serializer.save()
                response = {"status": HTTP_201_CREATED, "message": PRODUCT_ADDED_SUCCESSFULLY, "data": serializer.data}
                logging.info(response)
                return Response(response)
            else:
                response = {"status": HTTP_400_BAD_REQUEST, "error": serializer.errors, "data": None}
                logging.info(response)
                return Response(response)

        except Exception as error:
            response = {"status": HTTP_400_BAD_REQUEST, "error": error, "data": None}
            logging.info(response)
            return Response(response)


class RetrieveUpdateDeleteProducts(APIView):
    queryset = Product.objects.all().order_by('-date_created')
    serializer_class = ProductSerializer

    def get(self, request, **kwargs):
        try:
            product_id = kwargs['product_id']
            queryset = self.queryset.get(id = product_id)
            serialized_data = ProductSerializer(queryset).data
            response = {"status": HTTP_200_OK, "message": PRODUCT_DETAILS_LISTED_SUCCESSFULLY, "data": serialized_data}
            logging.info(response)
            return Response(response)
        except Exception as error:
            response = {"status": HTTP_400_BAD_REQUEST, "error": error, "data": None}
            logging.info(response)
            return Response(response)
        

    def put(self, request, **kwargs):
        try:
            product_query = Product.objects.filter(id = kwargs['product_id'])
            if product_query:
                current_time = get_current_timestamp_of_timezone(TIME_ZONE)
                request.data['date_updated'] = datetime.fromtimestamp(current_time, pytz.timezone(TIME_ZONE)).strftime("%Y-%m-%d %H:%M:%S")
                product_object = product_query.get()
                serializer = ProductSerializer(product_object, data=request.data, partial=True, context={'request': request})
                if serializer.is_valid():
                    serializer.save()
                    response = {"status": HTTP_200_OK, "message": PRODUCT_UPDATED_SUCCESSFULLY, "data": serializer.data}
                else:
                    response = {"status": HTTP_400_BAD_REQUEST, "error": serializer.errors, "data": None}
                
                logging.info(response)
                return Response(response)
            else:
                response = {"status": HTTP_400_BAD_REQUEST, "error": PRODUCT_DOESNT_EXISTS, "data": None}
                logging.info(response)
                return Response(response)
        except Exception as error:
            response = {"status": HTTP_400_BAD_REQUEST, "error": error, "data": None}
            logging.info(response)
            return Response(response)
    

    def delete(self, request, **kwargs):
        try:
            product_query = Product.objects.filter(id = kwargs['product_id'])
            if product_query:
                product_query.delete()
                response = {"status": HTTP_200_OK, "message": PRODUCT_DELETED_SUCCESSFULLY, "data": []}
            else:
                response = {"status": HTTP_400_BAD_REQUEST, "error": PRODUCT_DOESNT_EXISTS, "data": None}
            
            logging.info(response)
            return Response(response)
        except Exception as error:
            response = {"status": HTTP_400_BAD_REQUEST, "error": error, "data": None}
            logging.info(response)
            return Response(response)
        

class ListCreateOrders(ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get(self, request):
        query_dict = {}
        jwt_token = request.META['HTTP_AUTHORIZATION']
        user_details = encode_decode_jwt_token(jwt_token, convertion_type=DECODE)
        request.username = user_details['username']
        query_dict['user_id'] = user_details['id']
        queryset = Order.objects.filter(**query_dict)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = OrderSerializer(page, many=True, context = {'request': request})
            result = self.get_paginated_response(serializer.data)
            return result


    def post(self, request, **kwargs):
        try:
            jwt_token = request.META['HTTP_AUTHORIZATION']
            user_details = encode_decode_jwt_token(jwt_token, convertion_type=DECODE)
            request.username = user_details['username']
            current_time = get_current_timestamp_of_timezone(TIME_ZONE)
            request.data['date_placed'] = datetime.fromtimestamp(current_time, pytz.timezone(TIME_ZONE)).strftime("%Y-%m-%d %H:%M:%S")
            request.data['status'] = ORDER_STATUS[1]    #For order Placed
            request.data['user_id'] = user_details['id']
            order_serializer = OrderSerializer(data = request.data, context = {'request': request})
            if order_serializer.is_valid():
                order_serializer.save()
                order_datas = order_serializer.data
                orderitems_data  = {
                    'order_id': order_datas['id'],
                    'product_id': request.data['product_id'],
                    'quantity': request.data['quantity']
                }
                orderitem_serializer = OrderItemSerializer(data = orderitems_data, context = {'request':request})
                if orderitem_serializer.is_valid():
                    orderitem_serializer.save()
                    response = {"status": HTTP_201_CREATED, "message": ORDER_ADDED_SUCCESSFULLY, "data": order_serializer.data}
                else:
                    response = {"status": HTTP_400_BAD_REQUEST, "error": order_serializer.errors, "data": None}
            else:
                response = {"status": HTTP_400_BAD_REQUEST, "error": order_serializer.errors, "data": None}
                
            logging.info(response)
            return Response(response)
        except Exception as error:
            response = {"status": HTTP_400_BAD_REQUEST, "error": error, "data": None}
            logging.info(response)
            return Response(response)



class RetrieveUpdateDeleteOrders(APIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get(self, request, **kwargs):
        try:
            queryset = self.queryset.get(id = kwargs['order_id'])
            serialized_data = OrderSerializer(queryset, context={'request': request}).data
            response = {"status": HTTP_200_OK, "message": ORDER_DETAILS_LISTED_SUCCESSFULLY, "data": serialized_data}
            logging.info(response)
            return Response(response)
        except Exception as error:
            response = {"status": HTTP_400_BAD_REQUEST, "error": error, "data": None}
            logging.info(response)
            return Response(response)
        

    def put(self, request, **kwargs):
        try:
            order_query = Order.objects.filter(id = kwargs['order_id'])
            if order_query:
                if request.data.get('status'):
                    request.data['status'] = ORDER_STATUS[int(request.data.get('status'))]

                order_object = order_query.get()
                serializer = OrderSerializer(order_object, data=request.data, partial=True, context={'request': request})
                if serializer.is_valid():
                    serializer.save()
                    if request.data.get('quantity'):
                        OrderItem.objects.filter(order_id=kwargs['order_id']).update(quantity  = request.data['quantity'])
                    response = {"status": HTTP_201_CREATED, "message": ORDER_UPDATED_SUCCESSFULLY, "data": serializer.data}
                else:
                    response = {"status": HTTP_400_BAD_REQUEST, "error": serializer.errors, "data": None}
                
                logging.info(response)
                return Response(response)
            else:
                response = {"status": HTTP_400_BAD_REQUEST, "error": ORDER_DOESNT_EXISTS, "data": None}
                logging.info(response)
                return Response(response)
        except Exception as error:
            response = {"status": HTTP_400_BAD_REQUEST, "error": error, "data": None}
            logging.info(response)
            return Response(response)
    

    def delete(self, request, **kwargs):
        try:
            order_query = Order.objects.filter(id = kwargs['order_id'])
            if order_query:
                order_query.delete()
                response = {"status": HTTP_200_OK, "message": ORDER_DELETED_SUCCESSFULLY, "data": []}
            else:
                response = {"status": HTTP_400_BAD_REQUEST, "error": ORDER_DOESNT_EXISTS, "data": None}
            
            logging.info(response)
            return Response(response)
        except Exception as error:
            response = {"status": HTTP_400_BAD_REQUEST, "error": error, "data": None}
            logging.info(response)
            return Response(response)
        
