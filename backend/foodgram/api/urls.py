from rest_framework import routers
from django.urls import path, include

from api.views import CustomUserViewSet, TagViewSet, RecipeViewSet, IngredientsViewSet

router = routers.DefaultRouter()
router.register('users', CustomUserViewSet, basename='users')
router.register('tags', TagViewSet)
router.register('recipes', RecipeViewSet)
router.register('ingredients', IngredientsViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
 ]