from rest_framework import serializers

from shopping.models import Order, Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"

    def to_representation(self, instance):
        representation = super(OrderSerializer, self).to_representation(instance)
        # if self.context['request'].method == 'GET':
        #     orderitem_query_object = OrderItem.objects.get(order_id = instance.id)
        #     representation['user_id'] = instance.user_id_id
        #     representation['username'] = instance.user_id.username
        #     representation['email'] = instance.user_id.email
        #     representation['name'] = orderitem_query_object.product_id.name
        #     representation['status'] = instance.status
        #     representation['description'] = orderitem_query_object.product_id.description
        #     representation['price'] = orderitem_query_object.product_id.price
        #     representation['date_placed'] = instance.date_placed
        return representation
