provider "google" {
  project = "learn-gcp-terraform-469711"
  region  = "us-central1"
}

variable "image_url" {
  description = "The Docker image URL for the Cloud Run service"
  type        = string
  default     = "gcr.io/learn-gcp-terraform-469711/lastbit-dev:latest"
}

resource "google_cloud_run_service" "default" {
  name     = "lastbit-dev"
  location = "us-central1"

  template {
    spec {
      containers {
        image = var.image_url
      }
    }
  }
}
