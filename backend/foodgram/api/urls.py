from rest_framework import routers
from django.urls import path, include

from api.views import CustomUserViewSet, TagViewSet, RecipeViewSet, IngredientsViewSet, CartViewSet

router = routers.DefaultRouter()
router.register('users', CustomUserViewSet)
router.register('tags', TagViewSet)
router.register('recipes', RecipeViewSet)
router.register('ingredients', IngredientsViewSet)
router.register(r'cart', CartViewSet, basename='cart')

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls))
 ]