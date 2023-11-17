import ldap
from configs.settings import SERVER_AD, BASEDN, USER_PORTAL, PASS_USER_PORTAL


class SearchLDAP():
    '''Buscas no servidor AD'''
    
    def __init__(self):
        self.conn = ldap.initialize(SERVER_AD)
        self.conn.protocol_version = 3
        self.conn.set_option(ldap.OPT_REFERRALS, 0)

    def search(self, filter=None):
        '''Faz uma busca generica de acordo com o filtro passado no parametro'''

        try:
            self.conn.simple_bind_s(USER_PORTAL, PASS_USER_PORTAL)
            result = self.conn.search_s(BASEDN, ldap.SCOPE_SUBTREE, filter)
            return result
            
        finally:
            self.conn.unbind()