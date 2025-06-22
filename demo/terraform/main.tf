locals {
  provision_script = [
    "export PATH=$HOME/.local/bin:$PATH",
    "sudo NEEDRESTART_MODE=a apt update",
    "sudo NEEDRESTART_MODE=a apt install -y git python3-pip",
    "python3 -m pip install uv",
    "uv --version",
    "git clone https://github.com/boshyxd/QuantDog.git",
    "cd QuantDog",
    "uv sync --package client",
  ]
  private_key = file(pathexpand("~/.ssh/spurhacks_ed25519"))
}

resource "digitalocean_ssh_key" "spurhacks" {
  name       = "Spurhacks 2025"
  public_key = file(pathexpand("~/.ssh/spurhacks_ed25519.pub"))
}

resource "digitalocean_droplet" "demo1" {
  image    = "ubuntu-22-04-x64"
  name     = "quantdog-demo-1"
  region   = var.region
  size     = var.droplet_size
  ssh_keys = [digitalocean_ssh_key.spurhacks.fingerprint]

  connection {
    host        = self.ipv4_address
    user        = "root"
    type        = "ssh"
    private_key = local.private_key
    timeout     = "2m"
  }

  provisioner "remote-exec" {
    inline = local.provision_script
  }
}


resource "digitalocean_droplet" "demo2" {
  image    = "ubuntu-22-04-x64"
  name     = "quantdog-demo-2"
  region   = var.region
  size     = var.droplet_size
  ssh_keys = [digitalocean_ssh_key.spurhacks.fingerprint]

  connection {
    host        = self.ipv4_address
    user        = "root"
    type        = "ssh"
    private_key = local.private_key
    timeout     = "2m"
  }
  provisioner "remote-exec" {
    inline = local.provision_script
  }
}



