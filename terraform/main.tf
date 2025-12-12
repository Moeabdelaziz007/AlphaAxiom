provider "google" {
  project = "YOUR_PROJECT_ID"  # ⚠️ Replace with your Project ID
  region  = "us-central1"
  zone    = "us-central1-a"
}

# 1. External Static IP (So IP doesn't change)
resource "google_compute_address" "static_ip" {
  name = "aqt-trade-station-ip"
}

# 2. Firewall Rule (Allow RDP)
resource "google_compute_firewall" "allow_rdp" {
  name    = "allow-rdp"
  network = "default"

  allow {
    protocol = "tcp"
    ports    = ["3389"]
  }

  source_ranges = ["0.0.0.0/0"] # ⚠️ Warning: Open to world. Use your specific IP for better security.
  target_tags   = ["rdp-server"]
}

# 3. Windows VM Instance
resource "google_compute_instance" "aqt_vm" {
  name         = "aqt-trade-station"
  machine_type = "e2-standard-2" # 2 vCPU, 8GB RAM ($0.067/hour approx)
  zone         = "us-central1-a"

  tags = ["rdp-server", "http-server", "https-server"]

  boot_disk {
    initialize_params {
      image = "windows-cloud/windows-2022"
      size  = 50
      type  = "pd-balanced"
    }
  }

  network_interface {
    network = "default"
    access_config {
      nat_ip = google_compute_address.static_ip.address
    }
  }

  service_account {
    scopes = ["cloud-platform"]
  }
}

# 4. Output the IP to connect
output "vm_external_ip" {
  value = google_compute_address.static_ip.address
}

output "next_steps" {
  value = "Run: gcloud compute reset-windows-password aqt-trade-station --zone us-central1-a --user admin"
}
