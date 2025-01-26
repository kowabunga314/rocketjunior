from django.conf import settings
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from entity.models import Attribute, Entity
from entity.serializers import (
    AttributeSerializer, EntitySerializer, GenericEASerializer, GenericEAInputSerializer, GenericEASubtreeSerializer
)


@extend_schema_view(
    list=extend_schema(exclude=settings.HIDE_API_EXTENSIONS),
    retrieve=extend_schema(exclude=settings.HIDE_API_EXTENSIONS),
    create=extend_schema(exclude=settings.HIDE_API_EXTENSIONS),
    update=extend_schema(exclude=settings.HIDE_API_EXTENSIONS),
    partial_update=extend_schema(exclude=settings.HIDE_API_EXTENSIONS),
    destroy=extend_schema(exclude=settings.HIDE_API_EXTENSIONS),
    subtree=extend_schema(exclude=settings.HIDE_API_EXTENSIONS),
)
class EntityViewSet(viewsets.ModelViewSet):
    queryset = Entity.objects.all()
    serializer_class = EntitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        name = request.data.get('name')
        parent = request.data.get('parent')
        path = request.data.get('path')

        if path is None:
            if parent is None:
                path = self._generate_path_root(name)
                if len(Entity.objects.path_exists(path)) > 0:
                    return Response(
                        'A root entity with this name already exists',
                        status=status.HTTP_400_BAD_REQUEST
                    )
                request.data['path'] = path
            else:
                # Temporarily allow changes to request data, required to work around unique_together constraint on path
                _mutable = request.data._mutable
                request.data._mutable = True
                request.data['path'] = ''
                request.data._mutable = _mutable

        return super().create(request, *args, **kwargs)

    @action(detail=True, methods=['GET'])
    def subtree(self, request, pk=None):
        root_entity = get_object_or_404(Entity, pk=pk)
        return Response(root_entity.subtree())

    def _generate_path_root(self, name):
        return f'/{name}'


@extend_schema_view(
    list=extend_schema(exclude=settings.HIDE_API_EXTENSIONS),
    retrieve=extend_schema(exclude=settings.HIDE_API_EXTENSIONS),
    create=extend_schema(exclude=settings.HIDE_API_EXTENSIONS),
    update=extend_schema(exclude=settings.HIDE_API_EXTENSIONS),
    partial_update=extend_schema(exclude=settings.HIDE_API_EXTENSIONS),
    destroy=extend_schema(exclude=settings.HIDE_API_EXTENSIONS),
)
class AttributeViewSet(viewsets.ModelViewSet):
    queryset = Attribute.objects.all()
    serializer_class = AttributeSerializer
    permission_classes = [permissions.IsAuthenticated]


class SimpleUseViewSet(viewsets.ModelViewSet):

    queryset = Entity.objects.all()
    serializer_class = GenericEASerializer

    @extend_schema(
        summary='View a Node\'s Subtree',
        description='Get a node\'s subtree by providing its path in the URL.',
        responses={200: GenericEASubtreeSerializer},
    )
    def get(self, request, *args, **kwargs):
        # Get path and eliminate trailing slash if present
        full_path = '/' + kwargs.get('path').strip('/')
        try:
            entity = Entity.objects.get(path=full_path)
            return Response(entity.subtree(), status=status.HTTP_200_OK)
        except Entity.DoesNotExist:
            return Response({'message': 'Entity not found.'})

    @extend_schema(
        summary='Create a Node or Attribute',
        description='Create a node by leaving the payload blank, or an attribute by including key/value pairs where \
            type(value) == float.',
        request=GenericEAInputSerializer,
        responses={201: GenericEASubtreeSerializer},
    )
    def create(self, request, *args, **kwargs):
        # Set up context fields from path kwarg
        full_path = '/' + kwargs.get('path')
        path_parts = full_path.strip('/').split('/')
        entity_name = path_parts[-1]
        parent_path = '/' + '/'.join(path_parts[:-1]) if len(path_parts) > 1 else None

        # Get parent entity if exists
        parent_entity = None
        if parent_path:
            try:
                parent_entity = Entity.objects.get(path=parent_path)
            except Entity.DoesNotExist:
                return Response({'message': 'Entity parent does not exist.'}, status.HTTP_404_NOT_FOUND)

        # Pass request data to serializer
        serializer_data = request.data
        serializer = GenericEASerializer(
            data=serializer_data,
            context={
                'path': full_path,
                'entity_name': entity_name,
                'parent_entity': parent_entity
            }
        )
        # Validate request data and return response
        if serializer.is_valid():
            body = serializer.save()
            return Response(body, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
