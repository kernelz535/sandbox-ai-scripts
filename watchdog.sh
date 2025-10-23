#!/bin/bash
LOGFILE="/home/ssm-user/bedrock/bedrock_watchdog.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

if [ ! -f "$LOGFILE" ]; then
  touch "$LOGFILE"
  chmod 664 "$LOGFILE"
  chown ssm-user:ssm-user "$LOGFILE"
fi

check_service() {
  local PORT=$1
  local SERVICE=$2

  if ! systemctl is-active --quiet "$SERVICE"; then
    echo "$DATE - $SERVICE is not active. Restarting..." >> "$LOGFILE"
    systemctl restart "$SERVICE"
    return
  fi

  sleep 2

  if ! ss -tuln | grep -q ":$PORT "; then
    echo "$DATE - Port $PORT ($SERVICE) not open. Restarting..." >> "$LOGFILE"
    systemctl restart "$SERVICE"
  else
    echo "$DATE - $SERVICE healthy on port $PORT." >> "$LOGFILE"
  fi
}

check_service 7860 bedrock7860.service
check_service 7861 bedrock7861.service
