from rest_framework.permissions import AllowAny
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from modules.usecases.user_ldap import ActionsLDAP

class LdapViewSet(viewsets.ViewSet):
    
    permission_classes = (AllowAny, )

    @action(detail=False, methods=['post'], url_path='login')
    def authenticate_user(self, request):
        ''' View responsável por autenticar o usuário no AD '''

        actions_ldap = ActionsLDAP()
        data = actions_ldap.authenticate(username=request.GET.get('username'), password=request.GET.get('password'))

        if data['is_authenticate']:
            return Response(data={'data': data['info'],
                'user_properties': data['user_properties'],
                'is_authenticate': data['is_authenticate']}, status=status.HTTP_200_OK)
        else:
            return Response(data={'data': data['info'],
                'user_properties': data['user_properties'],
                'is_authenticate': data['is_authenticate']}, status=status.HTTP_401_UNAUTHORIZED)
                

    @action(detail=False, methods=['post'], url_path='change_pwd')
    def change_password(self, request):
        ''' View responsável por mudar a senha do usuário AD'''

        _username = request.GET.get('username')
        _new_pwd = request.GET.get('new_password')

        action_ldap = ActionsLDAP()
        data = action_ldap.change_password(username=_username, new_pwd=_new_pwd)
        
        if data['is_authenticate'] and data['pass_has_change']:
            #Senha alterada
            return Response(data={'data': data['info']}, status=status.HTTP_200_OK)
        
        if data['is_authenticate'] and not data['pass_has_change']:
            #Erro no sistema
            return Response(data={'data': data['info']}, status=status.HTTP_400_BAD_REQUEST)
        
        if not data['is_authenticate'] and not data['is_authenticate']:
            #Usuário ou senha invalidos
            return Response(data={'data': data['info']}, status=status.HTTP_401_UNAUTHORIZED)