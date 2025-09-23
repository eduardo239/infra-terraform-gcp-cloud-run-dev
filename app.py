from flask import Flask, jsonify, request, abort
from google.cloud import firestore
from datetime import datetime
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        data = request.get_json()
        
        if not data or 'name' not in data:
            abort(400, 'Name is required')
        # user_id = len(users) + 1
        # user = {
        #     'id': user_id,
        #     'name': data['name'],
        #     'email': data.get('email', ''),
        #     'created_at': datetime.now().isoformat()
        # }
        # users.append(user)


        # storage
        user_data = {
            "name": data['name'],
            "email": data.get('email', ''),
            "created_at": datetime.now().isoformat()
        }
        db.collection("users").add(user_data)

        
        logger.info(f"Created user: {data['name']}")
        return jsonify(user_data), 201
    except Exception as e:
        logger.error(f"Error creating user: {e}")
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
    
    data = request.get_json()
    if not data:
        abort(400, 'No data provided')
    
    user['name'] = data.get('name', user['name'])
    user['email'] = data.get('email', user['email'])
    user['updated_at'] = datetime.now().isoformat()
    
    logger.info(f"Updated user: {user['name']}")
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
    data = request.get_json()
    
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

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({
        'error': 'Internal Server Error',
        'message': 'An unexpected error occurred',
        'status_code': 500
    }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)