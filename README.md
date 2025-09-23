gcloud auth login
gcloud auth configure-docker
docker build -t gcr.io/learn-gcp-terraform-469711/lastbit-dev:latest .
docker push gcr.io/learn-gcp-terraform-469711/lastbit-dev:latest
