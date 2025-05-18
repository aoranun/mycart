from rest_framework import serializers
from .models import *

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
    
class CustomerSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    username = serializers.CharField()
    password = serializers.CharField()
    points = serializers.IntegerField()

    class Meta:
        model = Customer
        fields = '__all__'

    def create(self, validated_data):
        return Customer.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.username = validated_data.get('username', instance.username)
        instance.password = validated_data.get('password', instance.password)
        instance.points = validated_data.get('points', instance.points)
        instance.save()
        return instance
    
class PromotionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    type = serializers.CharField()
    redeem_code = serializers.CharField()
    discount_rate = serializers.IntegerField()
    detail = serializers.CharField()

    class Meta:
        model = Promotion
        fields = '__all__'

    def create(self, validated_data):
        return Promotion.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.type = validated_data.get('type', instance.type)
        instance.redeem_code = validated_data.get('redeem_code', instance.redeem_code)
        instance.discount_rate = validated_data.get('discount_rate', instance.discount_rate)
        instance.detail = validated_data.get('detail', instance.detail)
        instance.save()
        return instance
class CartItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'total_price']
        read_only_fields = ['total_price']

    def create(self, validated_data):
        product = validated_data['product']
        quantity = validated_data.get('quantity', 1)
        total_price = product.price * quantity
        return CartItem.objects.create(**validated_data, total_price=total_price)
    
class CartSerializer(serializers.ModelSerializer):
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all())
    promotions = serializers.PrimaryKeyRelatedField(
        queryset=Promotion.objects.all(), many=True, required=False
    )
    items = CartItemSerializer(many=True)

    total_price = serializers.SerializerMethodField()
    customer_points = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'customer', 'customer_points', 'promotions', 'created_at', 'items', 'total_price']

    def get_total_price(self, obj):
        return sum(item.total_price for item in obj.items.all())

    def get_customer_points(self, obj):
        return obj.customer.points if obj.customer else 0

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        promotions = validated_data.pop('promotions', [])

        cart = Cart.objects.create(**validated_data)
        cart.promotions.set(promotions)

        for item_data in items_data:
            CartItem.objects.create(cart=cart, **item_data)

        return cart