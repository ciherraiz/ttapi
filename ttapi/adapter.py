"""
ttapi.ttadapter

This module implements the Tastytrade API Adapter
"""
from json import JSONDecodeError
import logging
from typing import Dict, Any
from ttapi.config import tastytrade as ttcfg
from ttapi.models import RequestResult # type: ignore
from ttapi.exceptions import AdapterException # type: ignore
import requests

class Adapter:
    """Constructor for Adapter
    :param logger: (optional) if your app has a logger, pass it in
    """
    def __init__(self, base_url: str, logger: logging.Logger | None = None) -> None:
        self._logger = logger or logging.getLogger(__name__)  
        self._base_url = base_url
        self._headers = ttcfg['authentication']['headers'].copy()
    
    """ Performs generic a HTTP requests
    :param http_method: http method to use (GET, POST, DELETE)
    :param endpoit: url to connect
    :param body: (optional) body of HTTP request
    :param params: (optional) params of HTTP request
    """
    def do(self, http_method: str, endpoint: str, json: dict[str, str] = {}, data: str = None, params: dict[str, str] = {}) ->  RequestResult:
        full_url = self._base_url + endpoint
        # Log HTTP request params
        log_line_pre = f'method={http_method}, url={full_url}'
        log_line_post = ', '.join((log_line_pre, 'success={}, status_code={}, message={}'))

        try:
            self._logger.debug(msg=log_line_pre)
            response = requests.request(method=http_method,
                                        url=full_url,
                                        headers=self._headers,
                                        #data=json.dumps(body, default=str), #default to serialize date/datetime types
                                        json=json,
                                        data=data,
                                        params=params)
        except requests.exceptions.RequestException as e:
            self._logger.error(msg=(str(e)))
            raise AdapterException('Request failed') from e
        
        # Deserialize JSON output to Python object if there is some content
        if response.content:
            try:
                data_out = response.json()
            except (ValueError, JSONDecodeError) as e:
                print(e)
                self._logger.error(msg=log_line_post.format(False, None, e))
                raise AdapterException('Decoding JSON failed') from e
        else:
            data_out = ''
        
        is_success =  299 >= response.status_code >= 200
        
        log_line = log_line_post.format(is_success, response.status_code, response.reason)
        
        if is_success:
            self._logger.debug(msg=log_line)
            return RequestResult(int(response.status_code), message=response.reason, data=data_out)
        
        log_line = log_line_post.format(is_success, response.status_code, response.reason + '. ' + response.text)
        self._logger.error(msg=log_line)
        raise AdapterException(f'{response.status_code}: {response.reason + ". " + response.text}')

    """Add a new item to HTTP headers configuration
    """
    def add_header(self, key, value):
        self._headers[key]=value
        pass
