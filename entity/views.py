from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from entity.models import Attribute, Entity
from entity.serializers import AttributeSerializer, EntitySerializer, GenericEASerializer


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
                print('Dealing with a root node.')
                path = self._generate_path_root(name)
                if len(Entity.objects.path_exists(path)) > 0:
                    return Response(
                        'A root entity with this name already exists',
                        status=status.HTTP_400_BAD_REQUEST
                    )
                request.data['path'] = path
            else:
                request.data['path'] = ''

        
        return super().create(request, *args, **kwargs)

    @action(detail=True, methods=['GET'])
    def subtree(self, request, pk=None):
        root_entity = get_object_or_404(Entity, pk=pk)
        return Response(root_entity.subtree())
    
    def _generate_path_root(self, name):
        return f'/{name}'


class AttributeViewSet(viewsets.ModelViewSet):
    queryset = Attribute.objects.all()
    serializer_class = AttributeSerializer
    permission_classes = [permissions.IsAuthenticated]


class SimpleUseViewSet(viewsets.ModelViewSet):

    queryset = Entity.objects.all()
    serializer_class = GenericEASerializer

    def get(self, request, *args, **kwargs):
        full_path = '/' + kwargs.get('path')
        print('\nfull_path: ', full_path)
        try:
            entity = Entity.objects.get(path=full_path)
            return Response(entity.subtree(), status=status.HTTP_200_OK)
        except Entity.DoesNotExist:
            return Response({'message': 'Entity not found.'})

    def create(self, request, *args, **kwargs):
        full_path = '/' + kwargs.get('path')
        path_parts = full_path.strip('/').split('/')
        entity_name = path_parts[-1]
        parent_path = '/' + '/'.join(path_parts[:-1]) if len(path_parts) > 1 else None

        parent_entity = None
        if parent_path:
            print('\nparent_path: ', parent_path)
            parent_entity = Entity.objects.get(path=parent_path)

        serializer_data = request.data
        # print('request.data: ', request.data)
        # serializer_data['entity_name'] = entity_name
        # serializer_data['parent_path'] = parent_path

        serializer = GenericEASerializer(
            data=serializer_data,
            context={
                'path': full_path,
                'entity_name': entity_name,
                'parent_entity': parent_entity
            }
        )
        if serializer.is_valid():
            body = serializer.save()
            return Response(body, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
