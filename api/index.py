import sys
import os
from urllib.parse import unquote
from io import BytesIO

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

def handler(event, context):
    """
    Netlify Functions handler for Flask app
    """
    # Parse the request
    http_method = event.get('httpMethod', 'GET')
    path = event.get('path', '/')
    query_string = event.get('queryStringParameters', {})
    headers = event.get('headers', {})
    body = event.get('body', '')
    
    # Build the WSGI environ
    environ = {
        'REQUEST_METHOD': http_method,
        'SCRIPT_NAME': '',
        'PATH_INFO': unquote(path),
        'QUERY_STRING': '&'.join([f'{k}={v}' for k, v in (query_string or {}).items()]),
        'CONTENT_TYPE': headers.get('content-type', ''),
        'CONTENT_LENGTH': len(body) if body else 0,
        'SERVER_NAME': headers.get('host', 'localhost').split(':')[0],
        'SERVER_PORT': '443',
        'SERVER_PROTOCOL': 'HTTP/1.1',
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': headers.get('x-forwarded-proto', 'https'),
        'wsgi.input': BytesIO(body.encode() if isinstance(body, str) else body),
        'wsgi.errors': sys.stderr,
        'wsgi.multithread': False,
        'wsgi.multiprocess': False,
        'wsgi.run_once': True,
    }
    
    # Add headers to environ
    for header_name, header_value in headers.items():
        header_name = header_name.upper().replace('-', '_')
        if header_name not in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
            environ[f'HTTP_{header_name}'] = header_value
    
    # Response handler
    status_code = None
    response_headers = {}
    
    def start_response(status, response_headers_list):
        nonlocal status_code, response_headers
        status_code = int(status.split(' ')[0])
        response_headers = dict(response_headers_list)
        return lambda s: None
    
    # Call Flask app
    response_data = app(environ, start_response)
    response_body = b''.join(response_data)
    
    return {
        'statusCode': status_code or 200,
        'headers': response_headers,
        'body': response_body.decode('utf-8') if isinstance(response_body, bytes) else response_body,
    }
