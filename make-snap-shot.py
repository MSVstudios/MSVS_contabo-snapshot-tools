import requests
import argparse
import datetime
from dotenv import load_dotenv
import os

# Load variables from .env file
load_dotenv()

# Read API key and VPS ID from environment variables
API_KEY = os.getenv("API_KEY")
VPS_ID = os.getenv("VPS_ID")

# API endpoints
SNAPSHOTS_URL = f"https://api.contabo.com/v1/vps/{VPS_ID}/snapshots"
CREATE_SNAPSHOT_URL = f"https://api.contabo.com/v1/vps/{VPS_ID}/create_snapshot"

# Headers with API key
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Parse command line arguments
parser = argparse.ArgumentParser(description="Create or recreate a snapshot for a Contabo VPS")
parser.add_argument("--force", action="store_true", help="Force deletion of existing snapshot")
parser.add_argument("--expired", type=int, help="Delete and recreate snapshot if older than specified days")
args = parser.parse_args()

# Get existing snapshots
response = requests.get(SNAPSHOTS_URL, headers=headers)
snapshots = response.json()

# Check if a snapshot with the same description already exists
existing_snapshot = next((snapshot for snapshot in snapshots if snapshot["description"] == "My Snapshot"), None)

if not args.force and not args.expired and existing_snapshot:
    print("An existing snapshot already exists. To recreate it, use --force or --expired.")
else:
    if existing_snapshot:
        reason = "expired" if args.expired else "force"
        print(f"Deleting existing snapshot ({reason} reason)...")
        
        # Delete the existing snapshot
        delete_url = f"https://api.contabo.com/v1/vps/{VPS_ID}/delete_snapshot/{existing_snapshot['id']}"
        delete_response = requests.delete(delete_url, headers=headers)

        if delete_response.status_code == 200:
            print("Existing snapshot deleted.")
        else:
            print(f"Failed to delete existing snapshot. Status code: {delete_response.status_code}")
            print(delete_response.text)

    # Create a snapshot request payload
    payload = {
        "description": "My Snapshot"
    }

    # Make the API request to create a snapshot
    response = requests.post(CREATE_SNAPSHOT_URL, json=payload, headers=headers)

    # Check the response
    if response.status_code == 200:
        print("Snapshot created successfully!")
    else:
        print(f"Failed to create snapshot. Status code: {response.status_code}")
        print(response.text)
