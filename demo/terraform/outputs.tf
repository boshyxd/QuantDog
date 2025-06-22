output "demo_1_ip" {
  value = digitalocean_droplet.demo1.ipv4_address
}

output "demo_2_ip" {
  value = digitalocean_droplet.demo2.ipv4_address
}
