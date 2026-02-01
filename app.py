from flask import Flask, jsonify, request, abort
from google.cloud import firestore
from datetime import datetime
import logging
import re

app = Flask(__name__)

# Segurança: limite de tamanho do body (1 MB)
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Limites de validação
MAX_NAME_LENGTH = 200
MAX_EMAIL_LENGTH = 254
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')


def _add_security_headers(response):
    """Adiciona headers de segurança à resposta."""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    return response


app.after_request(_add_security_headers)


def _validate_name(name):
    """Valida e sanitiza o nome (sem caracteres de controle)."""
    if not name or not isinstance(name, str):
        return None
    name = name.strip()
    if not name or len(name) > MAX_NAME_LENGTH:
        return None
    if any(ord(c) < 32 and c not in '\t' for c in name):
        return None
    return name


def _validate_email(email):
    """Valida formato de email (opcional)."""
    if not email:
        return ''
    if not isinstance(email, str) or len(email) > MAX_EMAIL_LENGTH:
        return None
    return email if EMAIL_REGEX.match(email.strip()) else None

# In-memory data store for demo purposes
users = []
tasks = []

@app.route('/')
def hello():
    return "Hello, World!"

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring and load balancers"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    }), 200

@app.route('/api/info')
def api_info():
    """API information endpoint"""
    return jsonify({
        'name': 'Cloud Run Demo API',
        'version': '1.0.0',
        'description': 'A demo Flask application for Google Cloud Run',
        'endpoints': [
            'GET /',
            'GET /health',
            'GET /api/info',
            'GET /api/users',
            'POST /api/users',
            'GET /api/users/<id>',
            'PUT /api/users/<id>',
            'DELETE /api/users/<id>',
            'POST /api/process',
            'GET /api/status'
        ],
        'timestamp': datetime.now().isoformat()
    })

# User Management Endpoints
@app.route('/api/users', methods=['GET'])
def get_users():
    """Get all users"""
    return jsonify({'users': users, 'count': len(users)})

@app.route('/api/users', methods=['POST'])
def create_user():
    """Create a new user"""
    try:
        db = firestore.Client()
        data = request.get_json(force=False, silent=True)
        if data is None:
            abort(400, 'Invalid JSON')

        if not data or 'name' not in data:
            abort(400, 'Name is required')

        name = _validate_name(data['name'])
        if name is None:
            abort(400, f'Name must be 1-{MAX_NAME_LENGTH} characters and contain no control characters')

        email_raw = data.get('email', '')
        email = _validate_email(email_raw) if email_raw else ''
        if email is None:
            abort(400, 'Invalid email format')

        user_data = {
            "name": name,
            "email": email,
            "created_at": datetime.now().isoformat()
        }
        db.collection("users").add(user_data)

        logger.info("Created user successfully")
        return jsonify(user_data), 201
    except Exception as e:
        logger.error("Error creating user: %s", str(e))
        abort(500, 'Internal Server Error')

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get a specific user"""
    user = next((u for u in users if u['id'] == user_id), None)
    if not user:
        abort(404, 'User not found')
    return jsonify(user)

@app.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """Update a user"""
    user = next((u for u in users if u['id'] == user_id), None)
    if not user:
        abort(404, 'User not found')

    data = request.get_json(force=False, silent=True)
    if data is None:
        abort(400, 'Invalid JSON')
    if not data:
        abort(400, 'No data provided')

    if 'name' in data:
        name = _validate_name(data['name'])
        if name is None:
            abort(400, f'Name must be 1-{MAX_NAME_LENGTH} characters and contain no control characters')
        user['name'] = name
    if 'email' in data:
        email = _validate_email(data['email'])
        if email is None:
            abort(400, 'Invalid email format')
        user['email'] = email

    user['updated_at'] = datetime.now().isoformat()
    logger.info("Updated user successfully")
    return jsonify(user)

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete a user"""
    global users
    user = next((u for u in users if u['id'] == user_id), None)
    if not user:
        abort(404, 'User not found')
    
    users = [u for u in users if u['id'] != user_id]
    logger.info(f"Deleted user: {user['name']}")
    return jsonify({'message': 'User deleted successfully'})

# Data Processing Endpoints
@app.route('/api/process', methods=['POST'])
def process_data():
    """Process data endpoint - simulates data processing"""
    data = request.get_json(force=False, silent=True)
    if data is None:
        abort(400, 'Invalid JSON')
    if not data:
        abort(400, 'No data provided')
    
    task_id = len(tasks) + 1
    task = {
        'id': task_id,
        'status': 'processing',
        'data': data,
        'created_at': datetime.now().isoformat(),
        'result': None
    }
    
    # Simulate processing by adding some metadata
    processed_result = {
        'original_data': data,
        'processed_at': datetime.now().isoformat(),
        'character_count': len(str(data)) if data else 0,
        'data_type': type(data).__name__
    }
    
    task['status'] = 'completed'
    task['result'] = processed_result
    task['completed_at'] = datetime.now().isoformat()
    
    tasks.append(task)
    logger.info(f"Processed task {task_id}")
    
    return jsonify({
        'task_id': task_id,
        'status': 'completed',
        'result': processed_result
    }), 201

@app.route('/api/status')
def get_status():
    """Get system status and statistics"""
    return jsonify({
        'system_status': 'running',
        'uptime': 'N/A - stateless',
        'statistics': {
            'total_users': len(users),
            'total_tasks': len(tasks),
            'completed_tasks': len([t for t in tasks if t['status'] == 'completed'])
        },
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/tasks')
def get_tasks():
    """Get all processing tasks"""
    return jsonify({'tasks': tasks, 'count': len(tasks)})

@app.route('/api/tasks/<int:task_id>')
def get_task(task_id):
    """Get a specific task"""
    task = next((t for t in tasks if t['id'] == task_id), None)
    if not task:
        abort(404, 'Task not found')
    return jsonify(task)

# Error Handlers
@app.errorhandler(403)
def forbidden(error):
    """Handle 403 errors"""
    return jsonify({
        'error': 'Forbidden',
        'message': 'You do not have permission to access this resource',
        'status_code': 403
    }), 403

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Not Found',
        'message': 'The requested resource was not found',
        'status_code': 404
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors"""
    return jsonify({
        'error': 'Method Not Allowed',
        'message': 'The method is not allowed for the requested URL',
        'status_code': 405
    }), 405


@app.errorhandler(400)
def bad_request(error):
    """Handle 400 errors"""
    return jsonify({
        'error': 'Bad Request',
        'message': str(error.description) if hasattr(error, 'description') else 'Invalid request',
        'status_code': 400
    }), 400

@app.errorhandler(413)
def payload_too_large(error):
    """Handle 413 - Request Entity Too Large"""
    return jsonify({
        'error': 'Payload Too Large',
        'message': 'Request body exceeds maximum allowed size (1 MB)',
        'status_code': 413
    }), 413


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error("Internal server error: %s", str(error))
    return jsonify({
        'error': 'Internal Server Error',
        'message': 'An unexpected error occurred',
        'status_code': 500
    }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)