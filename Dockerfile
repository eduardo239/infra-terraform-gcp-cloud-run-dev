# Use official Python base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Expose port 8080 for Cloud Run
EXPOSE 8080

# Run the app
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]