import requests
import json
import argparse
import datetime
from dotenv import load_dotenv
import os

# Load variables from .env file
load_dotenv()

# Read API key and VPS ID from environment variables


CLIENT_ID=os.getenv("CLIENT_ID")
CLIENT_SECRET=os.getenv("CLIENT_SECRET")
API_USER = os.getenv("API_USER")
API_PASSWORD = os.getenv("API_PASSWORD")

# Request access token
token_url = "https://auth.contabo.com/auth/realms/contabo/protocol/openid-connect/token"
token_data = {
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "username": API_USER,
    "password": API_PASSWORD,
    "grant_type": "password"
}

# get the acess token
try:
    response = requests.post(token_url, data=token_data)
    response.raise_for_status()  # Raise an exception for non-2xx responses
    
    # print(json.dumps(response.json(), indent=2))

    ACCESS_TOKEN = response.json().get("access_token")


    # Get list of instances using ACCESS_TOKEN
    instances_url = "https://api.contabo.com/v1/compute/instances"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "x-request-id": "51A87ECD-754E-4104-9C54-D01AD0F83406"
    }
    instances_response = requests.get(instances_url, headers=headers)

  # Check if instances response is valid
    if instances_response.status_code == 200:
        instances_data = instances_response.json()
        # Print JSON response
        print("#### INSTANCES LIST ####")
        # print(json.dumps(instances_response.json(), indent=2))
        print()
        for instance in instances_data.get("data"):
            instance_name = instance.get("name")
            instance_display_name = instance.get("displayName")
            print(f"Instance Name: {instance_name}")
            print(f"Instance Display Name: {instance_display_name}")
            print()
    else:
        print(f"Failed to fetch instances. Status code: {instances_response.status_code}")
        # rise an exception



except requests.exceptions.RequestException as e:
    print("An error occurred while obtaining the access token:", str(e))
except json.JSONDecodeError:
    print("Failed to decode JSON response from access token request.")


#listing snapshots





exit()
#ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
#VPS_ID = os.getenv("VPS_ID")

# chose the VPS ID if not specified




# API endpoints
SNAPSHOTS_URL = f"https://api.contabo.com/v1/vps/{VPS_ID}/snapshots"
CREATE_SNAPSHOT_URL = f"https://api.contabo.com/v1/vps/{VPS_ID}/create_snapshot"

# Headers with API key
headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
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
