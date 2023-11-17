import ldap
import logging
from ldap3 import *
from configs.settings import SERVER_AD, BASEDN, USER_PORTAL, PASS_USER_PORTAL, DOMAIN_COMPANY
from modules.helpers.ldap_search import SearchLDAP


#Bloco de configuração dos logs
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
fh = logging.FileHandler('logs/portal-app.log')
fh.setFormatter(formatter)
logger.addHandler(fh)


class ActionsLDAP():
    
    def __init__(self):
        ''' Inicializa o servidor quando chama a Classe '''
        
        logging.info(f'Iniciando conexão com o servidor -> {SERVER_AD}')
        self.conn = ldap.initialize(SERVER_AD)
        self.conn.protocol_version = 3
        self.conn.set_option(ldap.OPT_REFERRALS, 0)
        

    def authenticate(self, username=None, password=None):
        '''Function responsible for authenticating the user'''

        logger.info('**** FUNÇÃO DE AUTENTICAÇÃO DO USUÁRIO ****')
        try:
            logger.info(f'Autenticando usuário {username} com o dominio {DOMAIN_COMPANY} no servidor {SERVER_AD}')
            self.conn.simple_bind_s(username + DOMAIN_COMPANY, password)

            #abaixo verifica nivel de permissao e compania
            user_filter = f'(sAMAccountName={username})'
            user_properties = self.conn.search_s(BASEDN, ldap.SCOPE_SUBTREE, user_filter)
            logger.info('USUÀRIO AUTENTICADO!')
            logger.info(f'Propriedades resgatas dos usuário -> {user_properties}')

            _user_category =  user_properties[0][1].get('title', [b'colaborador'])[0].decode('utf-8')
            _user_company = user_properties[0][1].get('company')[0].decode('utf-8')
            _user_name = user_properties[0][1].get('givenName')[0].decode('utf-8') + ' ' + user_properties[0][1].get('sn')[0].decode('utf-8')

            _user_properties = {"category": _user_category, "company": _user_company, "user_name": _user_name}
            
        except ldap.INVALID_CREDENTIALS:
            logger.error(f'USUÁRIO NÃO AUTENTICADO!')
            return {'is_authenticate': False, 
                'info': "Invalid credentials", 
                'user_properties': {"category": None, "company": None, "user_name": None}}

        except ldap.SERVER_DOWN:
            logger.error('SERVIDOR CAIU!')
            return {'is_authenticate': False, 
                'info': "Server down", 
                'user_properties': {"category": None, "company": None, "user_name": None}}

        except ldap.LDAPError as e:
            message = e.message['desc']
            if type(e.message) == dict and e.message.has_key('desc'):
                logger.error(f'ERRO NÃO MAPEADO -> {message}')
                return {'is_authenticate': False, 
                    'info': "Other LDAP error: " + e.message['desc'],
                    'user_properties': {"category": None, "company": None, "user_name": None}
                    }

            else: 
                logger.error(f'ERRO NÃO MAPEADO -> {message}')
                return {'is_authenticate': False, 
                    'info': "Other LDAP error: " + e, 
                    'user_properties': {"category": None, "company": None, "user_name": None}}

        finally:
            logger.info(f'Fechando conexão com o servidor {SERVER_AD}')
            self.conn.unbind_s()
        
        logger.info(F'USUÁRIO {username} AUTENTICADO!')
        return {'is_authenticate': True, 
            'info': 'User Authenticate!',
            'user_properties': _user_properties}
    
    
    def change_properties(self, payload=None):
        '''Função responsavel por alterar propriedades do usuario'''
        
        try:
            logger.info('**** FUNÇÃO PARA -> ALTERAR PROPRIEDADES DO USUÁRIO ****')
            logger.info(f'Verificando se o usuário do portal esta autenticado no servidor | {USER_PORTAL}')
            s = Server(SERVER_AD, get_info=ALL)
            c = Connection(s, user=USER_PORTAL, password=PASS_USER_PORTAL)
            if not c.bind():
                logger.error('Usuário não autenticado!')
                user_is_authenticate = False
            else:
                logger.info('Usuário autenticado')
                user_is_authenticate = True

        except Exception as err:
            logger.error(f'Outros erros -> {err}')
            user_is_authenticate = False
        
        if user_is_authenticate:
            
            try:
                logger.info(f'Dados recebidos -> {payload}')
                _data_change = {}

                _givenName = payload['_givenName'].upper().replace(" ", "_")
                _sn = payload['_sn'].upper().replace(" ", "_")
                _displayname = _givenName + " " + _sn

                if payload['_givenName'] or payload['_sn']:
                    _data_change['givenName'] = [(MODIFY_REPLACE, [_givenName])]
                    _data_change['sn'] = [(MODIFY_REPLACE, [_sn])]
                    _data_change['displayName'] = [(MODIFY_REPLACE, [_displayname])]

                if payload['_password']:
                    _new_password = payload['_password'].encode('utf-16-le')
                    _data_change['unicodePwd'] = [(MODIFY_REPLACE, [_new_password])]
                    
                logger.info(f'Buscando distinguishedName do usuário para alteração de dados')
                _user_properties = self.search_user_properties(samaccountname=payload['_sAMAccountName_user'])
                _basedn_change = _user_properties['distinguishedName']
                logger.info(f'BASEDN do usuário -> {_basedn_change}')

                logger.info(f'Mudando propriedades do usuário com o payload -> {_data_change}')
                c.modify(_basedn_change, _data_change)
                logger.info('Propriedades alteradas com sucesso!')

                return {"is_authenticate": True,
                        "pass_has_change": True,
                        "info": "Senha alterada com sucesso!"}

            except Exception as err:
                logger.error(f'Propriedades não alteradas -> {err}')
                return {"is_authenticate": True,
                        "pass_has_change": False,
                        "info": "Usuário autentiacado, mas você não possui acesso suficiente para executar essa ação!"}
            finally:
                logger.info(f'Fechando conexão com o servidor {SERVER_AD}')
                c.unbind()

        else:
            c.unbind()
            return {"is_authenticate": False,
                    "pass_has_change": False,
                    "info": "Usuário não autenticado, verifique o usuário ou senha e tente novamente!"}
        
    def list_users_per_company(self, company=None):
        ''' Função de listagem de usuários por empresa. '''

        logger.info('**** FUNÇÃO DE LISTAGEM DE USUÁRIOS POR EMPRESA ****')
        logger.info(f'A compania a ser filtrada é -> {company}')

        _filter = f'(company={company})'
        logger.debug('Realizando busca...')
        data = SearchLDAP().search(filter=_filter)
        logger.info(f'Dados retornados da busca -> {data}')
        user_data = []
        
        logger.debug('Montando payload para retornar ao portal...')
        for user in data:
            
            _level_user = user[1].get('title')

            payload = {}
            payload['givenName'] =      user[1].get('givenName', [b'Not Found'])[0].decode('utf-8')
            payload['sn'] =             user[1].get('sn', [b'Not Found'])[0].decode('utf-8')
            payload['sAMAccountName'] = user[1].get('sAMAccountName', [b'Not Found'])[0].decode('utf-8')
            payload['company'] =        user[1].get('company', [b'Not Found'])[0].decode('utf-8')

            if _level_user:
                payload['title'] = _level_user[0].decode('utf-8')
            else:
                payload['title'] = 'colaborador'

            user_data.append(payload)
        
        logger.info(f'Payload -> {user_data}')
        return user_data

    def search_user_properties(self, samaccountname=None):
        ''' Função para buscar propriedades de um unico usuário '''

        logger.info('**** FUNÇÃO DE BUSCA DE PROPRIEDADES DO USUÁRIO ****')
        logger.info(f'Usuário a ser filtrado -> {samaccountname}')

        _filter = f'(sAMAccountName={samaccountname})'
        data = SearchLDAP().search(filter=_filter)
        logger.info(f'Dados retornados da busca -> {data}')
        
        payload = {}
        for key, value in data[0][1].items():
            if key == 'objectGUID' or key == 'objectSid':
                continue

            payload[key] = value[0].decode('utf-8')
        return payload
