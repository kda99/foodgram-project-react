from django.urls import include, path
from rest_framework import routers

from api.views import (CustomUserViewSet, IngredientsViewSet, RecipeViewSet,
                       TagViewSet)

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
