#!/bin/bash

# Check if the user provided the SSH address as a parameter
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 user@serveraddress"
    exit 1
fi

# Extract the SSH address from the first parameter
SSH_ADDRESS=$1

# Function to clean up on exit
cleanup() {
    echo "Closing SSH tunnel..."
    kill $SSH_PID
    exit 0
}

# Trap the exit signal to clean up
trap cleanup EXIT

# Establish the SSH tunnel
echo "Establishing SSH tunnel to $SSH_ADDRESS..."
ssh -L 8501:localhost:8501 $SSH_ADDRESS &
SSH_PID=$!

# Check if SSH tunnel was established successfully
if [ $? -ne 0 ]; then
    echo "Failed to establish SSH tunnel. Exiting."
    exit 1
fi

# Give the SSH tunnel a moment to establish
sleep 2

# Run the Streamlit app in the browser
echo "Opening Streamlit app in the browser..."
# Use xdg-open for Linux, open for macOS, or start for Windows
if command -v xdg-open > /dev/null; then
    xdg-open http://localhost:8501
elif command -v open > /dev/null; then
    open http://localhost:8501
elif command -v start > /dev/null; then
    start http://localhost:8501
else
    echo "No suitable command found to open the browser. Please open http://localhost:8501 manually."
fi

# Wait indefinitely to keep the script running and the SSH tunnel open
echo "Press Ctrl+C to close the SSH tunnel and exit."
while true; do
    sleep 1
done
