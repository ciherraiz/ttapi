from json import JSONDecodeError
import aiohttp
from typing import Any, Optional
from ttapi.models import RequestResult # type: ignore
from ttapi.exceptions import TastyTradeException # type: ignore
from ttapi.config import tastytrade as ttcfg
from ttapi.config import logger

class Session:

    def __init__(self, 
                 user: str, 
                 password: str, 
                 is_production: bool = True, 
                 remember_me: bool = False, 
                 remember_token: Optional[str] = None,
                 two_factor_authentitation: Optional[str] = None) -> None:
        """
        Create a session
        :param user: tastytrade username or email
        :param password: tastytrade password
        :param is_production: production or developer (certification) environment
        :param remember_me: create or not a remember token
        :param remember_token: previously creatd token
        :param two_factor_authentitation: is 2FA is enabled, this is de code sent
        """
        self._session_token: str = ''

        self._payload: dict[str, Any] = {
            "login": user,
            "remember-me": remember_me
        }

        if password is not None:
            self._payload['password'] = password
        elif remember_token is not None:
            self._payload['remember-token'] = remember_token
        else:
            raise TastyTradeException('You must provide a password or a remember token')

        # proxy server
        self._proxy = ttcfg['network']['proxy'] if ttcfg['network'].get('proxy') else None
        # base url selection
        self._base_url = ttcfg['production']['url'] if is_production else ttcfg['certification']['url']
        self._headers: dict[str, str] = ttcfg['network']['headers'].copy()

        if two_factor_authentitation:
            self._headers['X-Tastyworks-OTP'] = two_factor_authentitation


    async def _http_request(self, http_method: str, url: str, endpoint: str, headers: dict[str, str], json: dict[str, str] = {}, data: str = None, params: dict[str, str] = {}) ->  RequestResult:
        """
        Do a http request
        """
        async with aiohttp.ClientSession() as session: 
            async with session.request(method=http_method, url=url + endpoint, headers=headers, json=json, data=data, params=params, proxy=self._proxy) as response:           
                # Deserialize JSON output to Python object if there is some content
                #if response.content:
                try:
                    data_out = await response.json()
                except (ValueError, JSONDecodeError) as e:
                    logger.exception('Adapter exception')
                    raise TastyTradeException('Decoding JSON failed') from e
                #else:
                #    data_out = ''
                
                is_success =  299 >= response.status >= 200
                
                logger.debug(f'method={http_method}, url={url + endpoint} status_code={response.status}, message={response.reason}')

                if is_success:
                    return RequestResult(int(response.status), message=response.reason, data=data_out)
                else:
                    raise TastyTradeException('HTTP request failed')

    @classmethod
    async def create(cls, 
                     user: str, 
                    password: str, 
                    is_production: bool = True, 
                    remember_me: bool = False, 
                    remember_token: Optional[str] = None,
                    two_factor_authentitation: Optional[str] = None):
        """
        Factory methon to create a session
        :param user: tastytrade username or email
        :param password: tastytrade password
        :param is_production: production or developer (certification) environment
        :param remember_me: create or not a remember token
        :param remember_token: previously creatd token
        :param two_factor_authentitation: is 2FA is enabled, this is de code sent
        """
        
        self = cls(user, password, is_production, remember_me, remember_token, two_factor_authentitation)
        
        # TastyTrade API session
        response = await self.tt_request('POST', '/sessions', json=self._payload)

        self._session_token = response.data['data']['session-token']
        self._remember_token: Optional[str] = response.data['data']['remember-token'] if remember_me else None
        self._external_id: str = response.data['data']['user']['external-id']
        # add the header to use for API requests
        self._headers['Authorization'] = self._session_token

        # Get DxFeed API session
        response = await self.tt_request('GET', '/quote-streamer-tokens', json=self._payload)
        self._dxf_token = response.data['data']['token']
        self._dxf_url = response.data['data']['websocket-url'] + '/rest/events.json'
        self._dxf_headers = {'Authorization': f'Bearer {self._dxf_token}'}

        
        return self

    async def tt_request(self, http_method: str, endpoint: str, json: dict[str, str] = {}, data: str = None, params: dict[str, str] = {}):
        '''
        Http request to TastyTrade platform
        '''
        return await self._http_request(http_method, self._base_url, endpoint, self._headers, json, data, params)
    
    async def dxf_request(self, http_method: str, json: dict[str, str] = {}, data: str = None, params: dict[str, str] = {}):
        '''
        Http request to dxFeed platform
        '''
        return await self._http_request(http_method, self._dxf_url, '', self._dxf_headers, json, data, params)


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
    def external_id(self) -> str:
        return self._external_id

    @property
    def proxy(self) -> str:
        return self._proxy