from django.contrib import admin
from django.urls import path, include
<<<<<<< HEAD
=======
from api.views import index
>>>>>>> origin/master


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('api.urls') )
]
