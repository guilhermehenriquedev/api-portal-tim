from rest_framework.permissions import AllowAny
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from modules.usecases.user_ldap import ActionsLDAP


class SearchViewSet(viewsets.ViewSet):
    
    permission_classes = (AllowAny, )

    @action(detail=False, methods=['get'], url_path='user_company')
    def search_users_company(self, request):
        ''' View responsável por buscar usuários de uma empresa especifica '''

        actions_ldap = ActionsLDAP()
        data = actions_ldap.list_users_per_company(company=request.GET.get('company'))
        return Response(data=data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='per_user')
    def search_user_per_properties(self, request):
        ''' View responsável por buscar usuários pelo samaccountname '''

        actions_ldap = ActionsLDAP()
        data = actions_ldap.search_user_properties(samaccountname=request.GET.get('samaccountname'))
        return Response(data=data, status=status.HTTP_200_OK)
