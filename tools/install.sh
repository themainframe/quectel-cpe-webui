#!/usr/bin/env bash

#
# Installer script for quectel-cpe-webui
# Assumes default Raspbian setup (including credentials) with SSH enabled.
#

PI_USERNAME=pi
PI_HOST=$1
PI_APP_PATH="/home/pi/quectel-cpe-webui"
PI_APP_USER="pi"

INSTALL_TYPE=$2

# Define colours
ESC_SEQ="\x1b["
COL_RESET=$ESC_SEQ"39;49;00m"
COL_RED=$ESC_SEQ"31;01m"
COL_GREEN=$ESC_SEQ"32;01m"
COL_YELLOW=$ESC_SEQ"33;01m"
COL_BLUE=$ESC_SEQ"34;01m"
COL_MAGENTA=$ESC_SEQ"35;01m"
COL_CYAN=$ESC_SEQ"36;01m"

# Print a formatted log message
log() {
  echo -e " $COL_GREEN+$COL_RESET ${1}"
}
err() {
  echo -e " $COL_RED!$COL_RESET ${1}"
}

# Restart the systemd service
restart_systemd() {
  # Enable the systemd unit
  log "Reloading systemd..."
  ssh -q -i keys/${PI_HOST}.key -t -t ${PI_USERNAME}@${PI_HOST} "sudo systemctl daemon-reload"
  log "Enabling the systemd services..."
  ssh -q -i keys/${PI_HOST}.key -t -t ${PI_USERNAME}@${PI_HOST} "sudo systemctl enable quectel-cpe-webui.service"
  log "Restarting the systemd service..."
  ssh -q -i keys/${PI_HOST}.key -t -t ${PI_USERNAME}@${PI_HOST} "sudo systemctl restart quectel-cpe-webui.service"
  sleep 1
  log "Here's the systemd service statuses:"
  ssh -q -i keys/${PI_HOST}.key -t -t ${PI_USERNAME}@${PI_HOST} "sudo systemctl status quectel-cpe-webui.service"
}

# We must have at least one argument
if [ $# -lt 1 ]; then
  echo " ! Usage: ./install.sh PI_HOST"
  exit
fi

# Start
log "Welcome to the quectel-cpe-webui provisioning script"

# Check we can talk to the host first
log "Generating provisioning keypair..."
yes | ssh-keygen -q  -N '' -f ./keys/${PI_HOST}.key > /dev/null

log "Installing the provisioning keypair..."
ssh-copy-id -i keys/${PI_HOST}.key ${PI_USERNAME}@${PI_HOST} > /dev/null 2>&1

# Install scripts
log "Removing existing package..."
ssh -q -i keys/${PI_HOST}.key -t -t ${PI_USERNAME}@${PI_HOST} "rm -rf ${PI_APP_PATH}"
ssh -q -i keys/${PI_HOST}.key -t -t ${PI_USERNAME}@${PI_HOST} "mkdir ${PI_APP_PATH}"

# Copy the code into place
log "Copying package into place..."
rsync -e "ssh -i keys/${PI_HOST}.key" -rqa --exclude=".git" app/* ${PI_USERNAME}@${PI_HOST}:${PI_APP_PATH}

# Copy the generated configuration into place
log "Copying configuration into place..."
scp -q -i keys/${PI_HOST}.key config.yml.dist ${PI_USERNAME}@${PI_HOST}:${PI_APP_PATH}/config.yml

# Installing deps?
if [ "$INSTALL_TYPE" == "app-only" ]; then
  echo " ! app-only: not installing dependencies"
  restart_systemd
  exit
fi

# Ensure user has appropriate group assignments
log "Setting up permissions..."
ssh -q -i keys/${PI_HOST}.key -t -t ${PI_USERNAME}@${PI_HOST} "sudo usermod ${PI_USERNAME} -aG tty"

# Install aptitude deps
log "Installing dpkg dependencies..."
ssh -q -i keys/${PI_HOST}.key -t -t ${PI_USERNAME}@${PI_HOST} "sudo apt-get update -yqq"
ssh -q -i keys/${PI_HOST}.key -t -t ${PI_USERNAME}@${PI_HOST} "sudo apt -yqq install git python3-pip"

# Install deps
log "Installing pip dependencies..."
ssh -q -i keys/${PI_HOST}.key -t -t ${PI_USERNAME}@${PI_HOST} "cd ${PI_APP_PATH} && pip3 install -r requirements.txt"

# Add a systemd unit for the application
log "Creating a systemd unit..."
cat > /tmp/quectel-cpe-webui.service <<EOL
[Unit]
Description=Quectel CPE Web UI
After=network.target

[Service]
User=${PI_USERNAME}
WorkingDirectory=${PI_APP_PATH}
ExecStart=/usr/bin/python3 ${PI_APP_PATH}/main.py
Restart=always
TimeoutStartSec=10
RestartSec=10

[Install]
WantedBy=network.target
EOL

# Copy the systemd unit into place
log "Copying systemd unit to RPi..."
scp -q -i keys/${PI_HOST}.key /tmp/quectel-cpe-webui.service ${PI_USERNAME}@${PI_HOST}:/tmp/quectel-cpe-webui.service
log "Moving systemd unit into place..."
ssh -q -i keys/${PI_HOST}.key -t -t ${PI_USERNAME}@${PI_HOST} "sudo mv /tmp/quectel-cpe-webui.service /lib/systemd/system/quectel-cpe-webui.service"

restart_systemd
