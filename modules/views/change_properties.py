from rest_framework.permissions import AllowAny
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from modules.usecases.user_ldap import ActionsLDAP


class ChangeViewSet(viewsets.ViewSet):
    
    permission_classes = (AllowAny, )

    @action(detail=False, methods=['post'], url_path='properties')
    def change_properties(self, request):
        ''' View responsável por alterar propriedades do usuario '''

        data = request.data
        actions_ldap = ActionsLDAP()
        data = actions_ldap.change_properties(payload=data)

        return Response(data=data, status=status.HTTP_200_OK)