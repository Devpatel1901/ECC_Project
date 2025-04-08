#!/bin/bash

# generate_systemd_services.sh - Register and enable systemd services for code runner containers

set -e

# Language-to-port mapping
declare -A languages=(
  [python]=9001
  [java]=9002
  [cpp]=9003
  [javascript]=9004
  [go]=9005
)

for lang in "${!languages[@]}"; do
  port=${languages[$lang]}
  image="code-runner-$lang"
  service_name="runner-$lang.service"
  container_name="runner-$lang"

  echo "🛠 Generating systemd service for $lang..."

  cat <<EOF | sudo tee /etc/systemd/system/$service_name > /dev/null
[Unit]
Description=Code Runner - $lang
After=docker.service
Requires=docker.service

[Service]
Restart=always
ExecStart=/usr/bin/docker run --rm -p ${port}:5000 --name ${container_name} ${image}
ExecStop=/usr/bin/docker stop ${container_name}

[Install]
WantedBy=multi-user.target
EOF

  sudo systemctl daemon-reload
  sudo systemctl enable $service_name
  sudo systemctl restart $service_name

  echo "$service_name is now enabled and running on port $port"
done

echo "\n All runner containers registered with systemd and auto-start enabled."
