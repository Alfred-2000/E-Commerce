from rest_framework import serializers

from shopping.models import CartItems, Order, Product, ProductImage, WishlistItems


class ProductSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(write_only=True)
    images = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = "__all__"

    def get_images(self, obj):
        return [image.image.url for image in ProductImage.objects.filter(product=obj)]

    def create(self, validated_data):
        image = validated_data.pop("image", None)
        product = Product.objects.create(**validated_data)
        if image:
            ProductImage.objects.create(product=product, image=image)
        return product

    def update(self, instance, validated_data):
        image = validated_data.pop("image", None)
        instance = super().update(instance, validated_data)
        if image:
            ProductImage.objects.create(product=instance, image=image)
        return instance


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
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
