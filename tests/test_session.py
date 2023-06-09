from unittest.mock import patch
from ttapi.adapter import Adapter
from ttapi.session import Session
from ttapi.models import RequestResult
from ttapi.exceptions import AdapterException
import pytest

@pytest.fixture
def response():
    response = {"data": {
                    "user": {
                    "email": "string",
                    "name": "string",
                    "nickname": "string",
                    "username": "string",
                    "external-id": "string"
                    },
                "remember-token": "string",
                "session-token": "thesessiontoken"
                },
                "context": "/sessions"
            }
    result = RequestResult(201, '', data=response)  
    return result

def test_create_a_session(response):   
    with patch.object(Adapter, 'do', return_value=response):
        session = Session("theuser", "thepass")
        assert session._session_token == 'thesessiontoken'

def test_create_session_fails():
    with patch.object(Adapter, 'do', side_effect=AdapterException('Request failed')):
        with pytest.raises(AdapterException, match='Request failed'):
            session = Session("theuser", "thepass")
            assert session._session_token == ''

def test_logout_success(response):
    delete_response = RequestResult(201, '', data={}) 

    with patch.object(Adapter, 'do', return_value=response):
        session = Session("theuser", "thepass")
        with patch.object(Adapter, 'do', return_value=delete_response):    
            result = session.logout()
            assert result == True

def test_logout_fails(response):
    with patch.object(Adapter, 'do', return_value=response):
        session = Session("theuser", "thepass")
        with patch.object(Adapter, 'do', side_effect=AdapterException('Request failed')):
            with pytest.raises(AdapterException, match='Request failed'):
                result = session.logout()
                assert result == None


def test_validation_success(response):
    validation_response = {"data": {                 
                                "email": "string",
                                "username": "string",
                                "external-id": "string",
                                "id": 555
                            },
                            "context": "/sessions/validate"
                        }
    
    with patch.object(Adapter, 'do', return_value=response):
            session = Session("theuser", "thepass")
            with patch.object(Adapter, 'do', return_value=validation_response):
                result = session.validate()
                assert result == True

def test_get_customer_data(response):
    customer_response = {'data': 
                            {'id': 'me', 'first-name': 'Taco', 'last-name': 'Bot'}
                        }
    result_customer = RequestResult(200, '', data = customer_response)
    
    with patch.object(Adapter, 'do', return_value=response):
            session = Session("theuser", "thepass")
            with patch.object(Adapter, 'do', return_value=result_customer):
                result = session.get_customer()
                assert result['data']['id'] == 'me'

def test_get_customer_fails(response):
    with patch.object(Adapter, 'do', return_value=response):
        session = Session("theuser", "thepass")
        with patch.object(Adapter, 'do', side_effect=AdapterException('Request failed')):
            with pytest.raises(AdapterException, match='Request failed'):
                result = session.validate()
                assert result == None