from json import dumps, JSONDecodeError
from unittest.mock import Mock, patch
from ttapi.adapter import Adapter
from ttapi.models import RequestResult
from requests.exceptions import RequestException
from ttapi.exceptions import AdapterException
import pytest

@pytest.fixture
def adapter():
    return Adapter('https://www.web.com')

def test_do_good_request_returns_result(adapter):
    json_data = {
        "data": {}           
    }
   
    mocked_response= Mock()
    mocked_response.json.return_value = json_data
    mocked_response.status_code = 200

    with patch('requests.request', return_value=mocked_response):
        r = adapter.do('GET', '')
        assert type(r) is RequestResult

def test_do_bad_request_raises_custom_exception(adapter):
    with patch('requests.request', side_effect=RequestException()):
        with pytest.raises(AdapterException, match='Request failed'):
            adapter.do('GET', '')

def test_do_bad_json_raises_adapter_exception(adapter):
    json_data = {
        "data": {}           
    }
    mocked_response= Mock()
    mocked_response.json.return_value = json_data
    mocked_response.status_code = 200
    
    mocked_response.json.side_effect = JSONDecodeError('', '', 0)

    with patch('requests.request', return_value=mocked_response):
        with pytest.raises(AdapterException, match='Decoding JSON failed'):
            adapter.do('GET', '')
def test_do_status_code_300_or_higher_raises_adapter_exception(adapter):
    mocked_response= Mock()
    mocked_response.status_code = 300
    mocked_response.reason = 'Error reason'
    mocked_response.text = 'Error detail'

    with patch('requests.request', return_value=mocked_response):
        with pytest.raises(AdapterException):
            adapter.do('GET', '')

def test_do_status_code_199_or_lower_raises_adapter_exception(adapter):
    mocked_response= Mock()
    mocked_response.status_code = 199
    mocked_response.reason = 'Error reason'
    mocked_response.text = 'Error detail'

    with patch('requests.request', return_value=mocked_response):
        with pytest.raises(AdapterException):
            adapter.do('GET', '')

#def test__get_method_passes_in_get(adapter):
#    json_data={}
#    mocked_response= Mock()
#    mocked_response.json.return_value = json_data
#    mocked_response.status_code = 200
#    mocked_response.method = ''

#    with patch('requests.request', return_value=mocked_response) as request:
#        adapter.get('')
#        assert request.call_args.kwargs['method'] == 'GET'
