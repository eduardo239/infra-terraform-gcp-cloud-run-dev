

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
    metadata {
      annotations = {
        "autoscaling.knative.dev/maxScale"  = "10"
        "run.googleapis.com/cpu-throttling" = "false"
      }
    }
    spec {
      container_concurrency = 80
      timeout_seconds       = 300

      containers {
        image = var.image_url

        ports {
          container_port = 8080
        }

        resources {
          limits = {
            cpu    = "1000m"
            memory = "512Mi"
          }
          requests = {
            cpu    = "100m"
            memory = "128Mi"
          }
        }

        startup_probe {
          http_get {
            path = "/health"
            port = 8080
          }
          initial_delay_seconds = 10
          timeout_seconds       = 5
          period_seconds        = 10
          failure_threshold     = 3
        }

        liveness_probe {
          http_get {
            path = "/health"
            port = 8080
          }
          initial_delay_seconds = 30
          timeout_seconds       = 5
          period_seconds        = 30
          failure_threshold     = 3
        }
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

resource "google_cloud_run_service_iam_member" "default" {
  service  = google_cloud_run_service.default.name
  location = google_cloud_run_service.default.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

resource "google_firestore_database" "default" {
  project     = "learn-gcp-terraform-469711"
  name        = "(default)"
  location_id = "us-central1"
  type        = "FIRESTORE_NATIVE"
}
