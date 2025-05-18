from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'promotions', PromotionViewSet, basename='promotion')
router.register(r'carts', CartViewSet, basename='cart')
# router.register(r'cart_items', CartItemViewSet, basename='cart_item')

urlpatterns = [
    path('', include(router.urls)),
]