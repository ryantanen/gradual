from flask import Flask, request, jsonify
from flask_cors import CORS
from functools import wraps
import jwt
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app, origins=["*"])

# Auth0 configuration
AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN')
AUTH0_API_AUDIENCE = os.getenv('AUTH0_API_AUDIENCE')
AUTH0_CLIENT_ID = os.getenv('AUTH0_CLIENT_ID')
AUTH0_CLIENT_SECRET = os.getenv('AUTH0_CLIENT_SECRET')

def get_token_auth_header():
    """Obtains the Access Token from the Authorization Header"""
    auth = request.headers.get('Authorization', None)
    if not auth:
        return None
    parts = auth.split()
    token = parts[1]
    return token

def requires_auth(f):
    """Decorator to validate Auth0 tokens"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_auth_header()
        if not token:
            return jsonify({'message': 'No authorization token provided'}), 401
        # You need to provide your Auth0 secret or public key here
        auth0_secret = AUTH0_CLIENT_SECRET
        
        payload = jwt.decode(
            token, 
            auth0_secret,
            algorithms=['RS256']  # Specify the algorithm(s) you expect
        )
        return f(*args, **kwargs)
    return decorated

# Public route
@app.route('/api/public', methods=['GET'])
def public():
    return jsonify({
        'message': 'This is a public endpoint. No authentication required.'
    })

# Protected route
@app.route('/api/protected', methods=['GET'])
@requires_auth
def protected():
    return jsonify({
        'message': 'This is a protected endpoint. Authentication required.',
        'user': request.user if hasattr(request, 'user') else None
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
