from rest_framework_nested import routers
from django.urls import path, include

from api.views import CustomUserViewSet, TagViewSet, RecipeViewSet, IngredientsViewSet

router = routers.DefaultRouter()
router.register('users', CustomUserViewSet)
router.register('tags', TagViewSet)
router.register('recipes', RecipeViewSet)
router.register('ingredients', IngredientsViewSet)

# users_router = routers.NestedDefaultRouter(router, 'users', lookup='user')
# users_router.register('subscriptions', UserSubscriptionsViewSet, basename='users-subscriptions')


urlpatterns = [
    path('', include('djoser.urls')),
    # path('', include(users_router.urls)),
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
 ]