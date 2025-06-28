from rest_framework import serializers

from shopping.models import CartItems, Order, Product, WishlistItems


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"


class CartItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItems
        fields = "__all__"


class WishlistItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = WishlistItems
        fields = "__all__"
