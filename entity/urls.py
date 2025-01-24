from django.urls import include, path
from rest_framework import routers

from entity import views


router = routers.DefaultRouter()
router.register(r'entity', views.EntityViewSet)
router.register(r'attribute', views.AttributeViewSet)

urlpatterns = [
    path('', include(router.urls))
]
