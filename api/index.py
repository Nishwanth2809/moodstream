import sys
import os
from urllib.parse import unquote, parse_qs

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from werkzeug.test import EnvironBuilder
from werkzeug.wrappers import Request

def handler(event, context):
    """
    Netlify Functions handler for Flask app
    """
    try:
        http_method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        headers = event.get('headers', {})
        body = event.get('body', '')
        
        # Build the environ using werkzeug
        builder = EnvironBuilder(
            method=http_method,
            path=path,
            data=body if body else None,
            headers=headers,
            environ_base={
                'wsgi.url_scheme': headers.get('x-forwarded-proto', 'https'),
            }
        )
        
        environ = builder.get_environ()
        
        # Capture response
        response_data = []
        status = None
        response_headers = []
        
        def start_response(status_str, headers_list):
            nonlocal status, response_headers
            status = status_str
            response_headers = headers_list
            return lambda x: None
        
        # Call the Flask app
        app_iter = app(environ, start_response)
        
        try:
            response_data = [line for line in app_iter]
        finally:
            if hasattr(app_iter, 'close'):
                app_iter.close()
        
        # Extract status code
        status_code = int(status.split(' ', 1)[0]) if status else 200
        
        # Convert response to string
        body_content = b''.join(response_data)
        
        return {
            'statusCode': status_code,
            'headers': dict(response_headers),
            'body': body_content.decode('utf-8') if isinstance(body_content, bytes) else body_content,
        }
    
    except Exception as e:
        import traceback
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'text/plain'},
            'body': f'Error: {str(e)}\n\n{traceback.format_exc()}',
        }
