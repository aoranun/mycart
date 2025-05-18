from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    product_name = serializers.CharField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    detail = serializers.CharField()
    category = serializers.CharField()

    class Meta:
        model = Product
        fields = '__all__'

    def create(self, validated_data):
        return Product.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.product_name = validated_data.get('product_name', instance.product_name)
        instance.detail = validated_data.get('detail', instance.detail)
        instance.price = validated_data.get('price', instance.price)
        instance.category = validated_data.get('category', instance.category)
        instance.save()
        return instance