import logging
from typing import Any, Optional
#from config.config import tastytrade as ttcfg
#from config.config import foo
from ttapi.adapter import Adapter
from ttapi.config import tastytrade as ttcfg

class Session:
    """
    Has the configuration to interact with API
    """
    def __init__(self, user: str, password: str, is_certification: bool = False, logger: logging.Logger | None = None) -> None:
        """
        Create a session
        :param login: tastytrade username or email
        :param password: tastytrade password or a remember token obtained previously
        """
        self._session_token: str = ''

        payload: dict[str, Any] = {
            "login": user,
            "password": password,
            "remember-me": ttcfg['authentication']['remember_me']
        }

        # base url selection
        self._base_url = ttcfg['certification']['url'] if is_certification else ttcfg['production']['url']
        self._base_wss = ttcfg['certification']['wss'] if is_certification else ttcfg['production']['wss']

        self._adapter = Adapter(self._base_url)
        self._user = user
        self._password = password

        if ttcfg['authentication']['mfa'] == True:
            two_factor_auth = input('2FA: ')
            self._adapter.add_header('X-Tastyworks-OTP', two_factor_auth)
   
        response = self._adapter.do('POST', '/sessions', json=payload)

        self._session_token = response.data['data']['session-token']
        self._remember_token: Optional[str] = response.data['data']['remember-token'] if ttcfg['authentication']['remember_me'] else None
        self._external_id: str = response.data['data']['user']['external-id']

        # add the header to use for API requests
        self._adapter.add_header('Authorization', self._session_token)

    def request(self, http_method: str, endpoint: str, json: dict[str, str] = {}, data: str = None, params: dict[str, str] = {}):
        return self._adapter.do(http_method, endpoint, json, data, params)

    def validate(self) -> bool:
        """
        Validate the current session
        :return: True if the session is valid and False otherwise. 
        """
        self._adapter.do('POST', '/sessions/validate')
        return True
    
    def get_customer(self) -> dict[str, Any]:
        """
        Get the customer information
        :return: a 'Customer' object in JSON format.
        """
        response = self._adapter.do('GET', '/customers/me')
        return response.data
    
    def logout(self) -> bool:
        """
        Remove the session
        :return: True if the logout is valid
        """
        self._adapter.do('DELETE', '/sessions')
        return True
    
    @property
    def token(self) -> str:
        return self._session_token
    
    @property
    def wss(self) -> str:
        return self._base_wss
