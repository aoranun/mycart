from rest_framework import serializers
from .models import *
from decimal import Decimal
from math import floor

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
        quantity = validated_data['quantity']
        total_price = product.price * quantity
        return CartItem.objects.create(product=product, quantity=quantity, total_price=total_price)

    def update(self, instance, validated_data):
        instance.product = validated_data.get('product', instance.product)
        instance.quantity = validated_data.get('quantity', instance.quantity)
        instance.total_price = instance.product.price * instance.quantity
        instance.save()
        return instance
    
class CartSerializer(serializers.ModelSerializer):
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all())
    promotions = serializers.PrimaryKeyRelatedField(
        queryset=Promotion.objects.all(), many=True, required=False
    )
    items = CartItemSerializer(many=True)
    total_price = serializers.SerializerMethodField()
    discount_amount = serializers.SerializerMethodField()
    customer_points = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = [
            'id', 'customer', 'customer_points', 'promotions',
            'created_at', 'items', 'discount_amount', 'total_price'
        ]

    def get_discount_amount(self, obj):
        return self._calculate_discount(obj)

    def get_total_price(self, obj):
        total = Cart.calculate_total(obj)
        discount = self._calculate_discount(obj)
        final_price = total - discount
        return max(round(final_price, 2), Decimal(0))

    def get_customer_points(self, obj):
        return obj.customer.points if obj.customer else 0

    def _calculate_discount(self, cart):
        total = Cart.calculate_total(cart)
        discount = Decimal(0)

        for promo in cart.promotions.all():
            if promo.type == 'coupon':
                if promo.name == 'Fixed amount':
                    discount += Decimal(promo.discount_rate)
                elif promo.name == 'Percentage discount':
                    discount += total * Decimal(promo.discount_rate) / 100

            elif promo.type == 'ontop':
                if promo.name == 'Percentage discount by item category':
                    for item in cart.items.all():
                        if item.product.category == 'C':
                            discount += item.total_price * Decimal(promo.discount_rate) / 100
                elif promo.name == 'Discount by points':
                    points = cart.customer.points
                    used_discount = Decimal(points) * Decimal(promo.discount_rate)
                    discount += used_discount

            elif promo.type == 'seasonal':
                sets = floor(total / 300)
                discount += sets * Decimal(promo.discount_rate)

        return min(discount, total)

    def validate(self, data):
        customer = data.get('customer')
        promotions = data.get('promotions', [])
        items = data.get('items', [])

        temp_total = Decimal(0)
        for item in items:
            temp_total += item['product'].price * item['quantity']

        temp_discount = Decimal(0)
        for promo in promotions:
            if promo.type == 'coupon':
                if promo.name == 'Fixed amount':
                    temp_discount += Decimal(promo.discount_rate)
                elif promo.name == 'Percentage discount':
                    temp_discount += temp_total * Decimal(promo.discount_rate) / 100

            elif promo.type == 'ontop':
                if promo.name == 'Percentage discount by item category':
                    for item in items:
                        if item['product'].category == 'C':
                            temp_discount += item['product'].price * item['quantity'] * Decimal(promo.discount_rate) / 100
                elif promo.name == 'Discount by points':
                    if customer.points <= 0:
                        raise serializers.ValidationError("Customer has no points to redeem.")
                    temp_discount += Decimal(customer.points) * Decimal(promo.discount_rate)

            elif promo.type == 'seasonal':
                sets = floor(temp_total / 300)
                temp_discount += sets * Decimal(promo.discount_rate)

        if temp_discount > temp_total:
            raise serializers.ValidationError("Discount cannot exceed total cart value.")

        return data

    def create(self, validated_data):
        customer = validated_data.get('customer')
        promotion_ids = validated_data.pop('promotions', [])
        items_data = validated_data.pop('items', [])

        cart = Cart.objects.create(customer=customer)

        if promotion_ids:
            cart.promotions.set(promotion_ids)

        for item_data in items_data:
            product = item_data['product']
            quantity = item_data['quantity']
            total_price = product.price * quantity
            CartItem.objects.create(cart=cart, product=product, quantity=quantity, total_price=total_price)

        return cart

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', [])
        promotions = validated_data.pop('promotions', [])

        instance.promotions.set(promotions)

        for item_data in items_data:
            item_id = item_data.pop('id', None)
            if item_id:
                item = instance.items.get(id=item_id)
                item.product = item_data.get('product', item.product)
                item.quantity = item_data.get('quantity', item.quantity)
                item.total_price = item.product.price * item.quantity
                item.save()
            else:
                product = item_data['product']
                quantity = item_data['quantity']
                total_price = product.price * quantity
                CartItem.objects.create(cart=instance, product=product, quantity=quantity, total_price=total_price)

        return instance