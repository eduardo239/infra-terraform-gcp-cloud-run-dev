```bash
gcloud auth login
gcloud auth configure-docker
docker build -t gcr.io/learn-gcp-terraform-469711/lastbit-dev:latest .
docker push gcr.io/learn-gcp-terraform-469711/lastbit-dev:latest
```

# Dev API

## API Endpoints

New Endpoints Added:
Health Check - /health

Perfect for load balancer health checks and monitoring
API Information - /api/info

Returns API metadata, version, and available endpoints
User Management (CRUD):

```bash
GET /api/users - List all users
POST /api/users - Create a new user
GET /api/users/<id> - Get a specific user
PUT /api/users/<id> - Update a user
DELETE /api/users/<id> - Delete a user
Data Processing:
```

```bash
POST /api/process - Process data (simulated)
GET /api/status - System status and statistics
GET /api/tasks - List all processing tasks
GET /api/tasks/<id> - Get specific task details
```

Error Handling:
Custom 400, 403, 404, 405, 500 error pages
Proper JSON error responses

Key Improvements:  
✅ Logging: Added proper logging configuration  
✅ JSON Responses: All endpoints return structured JSON  
✅ Error Handling: Comprehensive error handling with meaningful messages  
✅ Input Validation: Request validation for POST/PUT endpoints  
✅ Documentation: Each endpoint has docstrings explaining its purpose  
✅ REST Standards: Follows RESTful API conventions  
✅ Cloud-Ready: Health check endpoint for container orchestration

## Cloud Build Triggers

- gcp-trigger-gh -> branch=main -> cloudbuild.yaml
- gcp-trigger-github-destroy -> branch=destroy -> destroy.yaml
