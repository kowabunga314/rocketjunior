from django.shortcuts import get_object_or_404
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from entity.models import Attribute, Entity
from entity.serializers import AttributeSerializer, EntitySerializer


class EntityViewSet(viewsets.ModelViewSet):
    queryset = Entity.objects.all()
    serializer_class = EntitySerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['GET'])
    def subtree(self, request, pk=None):
        root_entity = get_object_or_404(Entity, pk=pk)
        return Response(root_entity.subtree())


class AttributeViewSet(viewsets.ModelViewSet):
    queryset = Attribute.objects.all()
    serializer_class = AttributeSerializer
    permission_classes = [permissions.IsAuthenticated]
