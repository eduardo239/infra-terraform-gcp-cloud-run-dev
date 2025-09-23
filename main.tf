provider "google" {
  project = "learn-gcp-terraform-469711"
  region  = "us-central1"
}

resource "google_cloud_run_service" "default" {
  name     = "lastbit-dev"
  location = "us-central1"

  template {
    spec {
      containers {
        image = "gcr.io/learn-gcp-terraform-469711/lastbit-dev:1:0"
      }
    }
  }
}
