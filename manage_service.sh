#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SERVICE_FILE="currency-forecasting.service"

# Function to check if the service is running
check_service() {
    if launchctl list | grep -q "currency-forecasting"; then
        echo "Service is running"
    else
        echo "Service is not running"
    fi
}

# Function to start the service
start_service() {
    echo "Starting currency forecasting service..."
    launchctl load "$SCRIPT_DIR/$SERVICE_FILE"
    check_service
}

# Function to stop the service
stop_service() {
    echo "Stopping currency forecasting service..."
    launchctl unload "$SCRIPT_DIR/$SERVICE_FILE"
    check_service
}

# Function to restart the service
restart_service() {
    stop_service
    sleep 2
    start_service
}

# Function to show service status
status_service() {
    check_service
    echo "Service logs:"
    tail -n 50 "$SCRIPT_DIR/logs/app.log"
}

# Main script logic
case "$1" in
    start)
        start_service
        ;;
    stop)
        stop_service
        ;;
    restart)
        restart_service
        ;;
    status)
        status_service
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac

exit 0 