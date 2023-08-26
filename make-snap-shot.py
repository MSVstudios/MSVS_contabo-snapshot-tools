# by MSV studios - for contabo api https://api.contabo.com/
# https://github.com/MSVstudios/contabo-snapshot-tools
# version 20230825

import requests
import json
import argparse
import datetime
from dotenv import load_dotenv
import os
import uuid

# Load variables from .env file
load_dotenv()
# Read credentials from environment variables
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
API_USER = os.getenv("API_USER")
API_PASSWORD = os.getenv("API_PASSWORD")

# Set a unique trace ID for the request
TRACE_ID = uuid.uuid1()

def verbose_print(data):
    if args.verbose:
        print(data)

def get_access_token():
    token_url = "https://auth.contabo.com/auth/realms/contabo/protocol/openid-connect/token"
    token_data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "username": API_USER,
        "password": API_PASSWORD,
        "grant_type": "password"
    }
    
    try:
        response = requests.post(token_url, data=token_data)
        response.raise_for_status()  # Raise an exception for non-2xx responses
        verbose_print(json.dumps(response.json(), indent=2))
        return response.json().get("access_token")
    except requests.exceptions.RequestException as e:
        print("An error occurred while obtaining the access token:", str(e))
        return None
    except json.JSONDecodeError:
        print("Failed to decode JSON response from access token request.")
        return None

def list_instances(access_token):
    instances_url = "https://api.contabo.com/v1/compute/instances"
    request_id = uuid.uuid4()
    headers = {
        "Authorization": f"Bearer {access_token}",
        "x-request-id": f"{request_id}"
    }
    
    try:
        instances_response = requests.get(instances_url, headers=headers)
        instances_response.raise_for_status()  # Raise an exception for non-2xx responses      
        instances_data = instances_response.json().get("data")
        verbose_print(json.dumps(instances_response.json(), indent=2))
        if instances_response.status_code == 200 and isinstance(instances_data, list):
            print("#### INSTANCES LIST ####")
            instances = []
            for instance in instances_data:
                instances.append(instance)
                print(f"Instance Name: {instance['name']}")
                print(f"Instance Display Name: {instance['displayName']}")
                print(f"Instance ID: {instance['instanceId']}")
                print()
            return instances    
        else:
            print(f"Failed to fetch instances. Status code: {instances_response.status_code}")
        
    except requests.exceptions.RequestException as e:
        print("An error occurred while fetching instances:", str(e))
        print(instances_response.status_code)
        exit()

def select_instance(instances):
    if not instances:
        return None
    
    print("Select an instance to use:")
    for i, instance in enumerate(instances):
        print(f"{i+1}. {instance['displayName']} ({instance['name']}) instanceId: ({instance['instanceId']}))")
    
    selection = input("Enter the number of the instance you want to use: ")
    
    try:
        selection_index = int(selection) - 1
        if 0 <= selection_index < len(instances):
            return instances[selection_index]
        else:
            print("Invalid selection.")
            return None
    except ValueError:
        print("Invalid input. Please enter a valid number.")
        return None        

def list_snapshots(access_token,instance_id):
    print("Listing snapshots")
    print(f"Instance ID: {instance_id}")
    snapshots_url = f"https://api.contabo.com/v1/compute/instances/{instance_id}/snapshots"
    #print(snapshots_url)
    request_id = uuid.uuid4()
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
        "x-request-id": f"{request_id}",
        "x-trace-id": f"{TRACE_ID}"
    }
    
    try:
        snapshots_response = requests.get(snapshots_url, headers=headers)
        snapshots_response.raise_for_status()  # Raise an exception for non-2xx responses       
        snapshots_data = snapshots_response.json().get("data")
        verbose_print(json.dumps(snapshots_response.json(), indent=2))
        
        if snapshots_response.status_code == 200 and isinstance(snapshots_data, list):
            print("#### SNAPSHOTS LIST ####")
            snapshots = []
            for snapshot in snapshots_data:
                snapshots.append(snapshot)
                snapshot_name = snapshot.get("name")
                snapshot_snapshotId = snapshot.get("snapshotId")
                print(f"Snapshot Name: {snapshot_name}")
                print(f"Snapshot snapshotId: {snapshot_snapshotId}")
                print()
            return snapshots      
        else:
            print(f"Failed to fetch snapshots. Status code: {snapshots_response.status_code}")
        
    except requests.exceptions.RequestException as e:
        print("An error occurred while fetching snapshots:", str(e))

def select_snapshot(snapshot_ids):
    if not snapshot_ids:
        return None
    
    print("Select a snapshot to delete:")
    for i, snapshot_id in enumerate(snapshot_ids):
        print(f"{i+1}. Snapshot data: {snapshot_id}")
        #print(f"{i+1}. Snapshot name: {snapshot_id["name"]} Snapshot ID: {snapshot_id["snapshotId"]}")
    
    selection = input("Enter the number of the snapshot you want to delete: ")
    
    try:
        selection_index = int(selection) - 1
        if 0 <= selection_index < len(snapshot_ids):
            return snapshot_ids[selection_index]
        else:
            print("Invalid selection.")
            return None
    except ValueError:
        print("Invalid input. Please enter a valid number.")
        return None

def delete_snapshot(access_token, instance_id, snapshot_id):
    snapshot_url = f"https://api.contabo.com/v1/compute/instances/{instance_id}/snapshots/{snapshot_id}"
    request_id = uuid.uuid4()
    headers = {
        # if uncoment the next line you will get an error: BAD request
        # "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
        "x-request-id": f"{request_id}",
        "x-trace-id": f"{TRACE_ID}"
    }
    try:
        response = requests.delete(snapshot_url, headers=headers)
        response.raise_for_status()  # Raise an exception for non-2xx responses
        verbose_print(response.status_code)
        if response.status_code == 204 or response.status_code == 200:
            print(f"Snapshot {snapshot_id} deleted successfully. Status code: {response.status_code}")
        else:
            print(f"Failed to delete snapshot {snapshot_id}. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while deleting snapshot {snapshot_id}:", str(e))
        print(response.status_code)
        exit()

def create_snapshot(access_token, instance_id, snapshot_name, snapshot_description):
    snapshot_url = f"https://api.contabo.com/v1/compute/instances/{instance_id}/snapshots"
    request_id = uuid.uuid4()
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
        "x-request-id": f"{request_id}",
        "x-trace-id": f"{TRACE_ID}"
    }
    data = {
        "name": snapshot_name,
        "description": snapshot_description
    }
    
    try:
        response = requests.post(snapshot_url, headers=headers, json=data)
        response.raise_for_status()  # Raise an exception for non-2xx responses
        if response.status_code == 201 or response.status_code == 200:
            print(f"Snapshot {snapshot_name} created successfully.")
        else:
            print(f"Failed to create snapshot {snapshot_name}. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while creating snapshot {snapshot_name}:", str(e))

def snapshot_all(access_token):
    instances = list_instances(access_token)
    # for each instance get the snapshots
    for i, instance in enumerate(instances):
        snapshots=list_snapshots(access_token,instance['instanceId'])
        if len(snapshots) == 0:
            print(f"no snapshots for instance {instance['name']} no need to delete")
            #create a new snapshot
            snapshot_name = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            snapshot_description = "snapshot created by make-snap-shot.py script - github.com/msvs/msvs-contabo-snapshot"
            create_snapshot(access_token, instance['instanceId'], snapshot_name, snapshot_description) 
        else:
            snapshot=snapshots[0]
            # check if the selected snapshot is expired
            created_date = datetime.datetime.strptime(snapshot['createdDate'], "%Y-%m-%dT%H:%M:%S.%fZ")
            current_date = datetime.datetime.now()
            elapsed_days = (current_date - created_date).days
            print(f"elapsed days: {elapsed_days}")
            if args.expired and elapsed_days < args.expired:
                print(f"Snapshot {snapshot['name']} is not expired.")
                print("not deleting the snapshot")
            else:
                #delete the oldest snapshot
                delete_snapshot(access_token, instance['instanceId'], snapshot['snapshotId'])
                print(f"Snapshot {snapshot['name']} deleted successfully.")
                #create a new snapshot
                snapshot_name = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
                snapshot_description = "snapshot created by make-snap-shot.py script - github.com/msvs/msvs-contabo-snapshot"
                create_snapshot(access_token, instance['instanceId'], snapshot_name, snapshot_description)

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Create or recreate a snapshot for a Contabo VPS")
    parser.add_argument("--force","-f", action="store_true", help="Force deletion of existing snapshot")
    parser.add_argument("--expired","-e", type=int, help="Delete and recreate snapshot if older than specified days")
    parser.add_argument("--instanceid","-ii", type=int, help="provide instance id")
    parser.add_argument("--snapshotid", "-is", type=str, help="provide snapshot id")
    parser.add_argument("--oldest","-o", action="store_true", help="if is set he will delete the oldest snapshot in the specified instance without asking or specifying --snapshotid, (is overriden by --snapshotid). Don't need --force to forcibly delete the oldest snapshot." )
    parser.add_argument("--verbose","-v", action="store_true", help="Print verbose output")
    parser.add_argument("--all","-a", action="store_true", help="delete the oldest snapshot for all instances and make a new one")
    args = parser.parse_args()

    # get the access token
    access_token = get_access_token()

    if args.all and access_token:
        print("you used --all delete the oldest snapshot for all instances and make a new one")
        snapshot_all(access_token)

        exit()
    elif access_token:
        instances = list_instances(access_token)
        if instances:
            # if args.instanceid is specified check if the instance exist in the list
            if args.instanceid:
                #check if there the instance exist in the list
                found_instance = None
                for instance in instances:
                    if instance["instanceId"] == args.instanceid:
                        found_instance = instance
                        break
                if not found_instance:
                    print(f"Instance with instance ID {args.instanceid} not found.")
                    exit()
                selected_instance = found_instance
            else:
                selected_instance = select_instance(instances)
            if selected_instance:
                print("You selected:")
                print(f"Instance Name: {selected_instance['name']}")
                print(f"Instance Display Name: {selected_instance['displayName']}")
                print(f"Instance ID: {selected_instance['instanceId']}")

                # list snapshots
                snapshots=list_snapshots(access_token,selected_instance['instanceId'])

                # if snapshot list exist check
                new_snapshot = False 
                if snapshots:
                    print("snapshot(s) list exist")   
                    existing_snapshot = False
                    # check if the args.oldest and snapshotid are set
                    # if args.snapshotid is set then  args.oldest is everriden
                    if args.oldest and not args.snapshotid:
                        # Use the first snapshot in the list as the oldest snapshot
                        selected_snapshot = snapshots[0]
                        existing_snapshot = True
                        # set args.force to true
                        args.force = True
                        print("The oldest snapshot is:")
                        print(f"Snapshot Name: {selected_snapshot['name']}")
                        print(f"Snapshot snapshotId: {selected_snapshot['snapshotId']}")
                    # if args.snapshotid is set then check if the snapshot exist in the list
                    if args.snapshotid:
                        found_snapshot = False
                        for snapshot in snapshots:
                            if snapshot["snapshotId"] == args.snapshotid:
                                found_snapshot = True
                                existing_snapshot = True
                                selected_snapshot = snapshot
                                break
                        if not found_snapshot:
                            print(f"Snapshot with instance ID {args.snapshotid} not found.")
                            exit()
                    # if not set select a snapshot mauanlly
                    if not select_snapshot: 
                            selected_snapshot = select_snapshot(snapshots)
                            existing_snapshot = True
                    if selected_snapshot:
                        print("You selected:")
                        print(f"Snapshot Name: {selected_snapshot['name']}")
                        print(f"Snapshot snapshotId: {selected_snapshot['snapshotId']}")
                        if existing_snapshot:
                            print("the snapshot exist")
                            if not args.force and not args.expired :
                                print("An existing snapshot already exists. To recreate it, use --force or --expired.")
                            else:
                                # check if the selected snapshot is expired
                                if args.force:
                                    print("you used --force to delete existing snapshot.")
                                    print(f"now deleting snapshot {selected_snapshot['name']}")
                                    delete_snapshot(access_token, selected_instance['instanceId'], selected_snapshot['snapshotId'])
                                    new_snapshot = True 
                                elif args.expired:
                                    # check if the selected snapshot is expired
                                    created_date = datetime.datetime.strptime(selected_snapshot['createdDate'], "%Y-%m-%dT%H:%M:%S.%fZ")
                                    current_date = datetime.datetime.now()
                                    elapsed_days = (current_date - created_date).days
                                    print(f"elapsed days: {elapsed_days}")
                                    if args.expired is not None and elapsed_days > args.expired:
                                        print(f"you used --expired {args.expired} to delete existing snapshot.")
                                        print(f"Snapshot {selected_snapshot['name']} is expired ({elapsed_days} days).")
                                        print(f"now deleting snapshot {selected_snapshot['name']}")
                                        print()
                                        delete_snapshot(access_token, selected_instance['instanceId'], selected_snapshot['snapshotId'])
                                        new_snapshot = True 
                                    else:
                                        print(f"Snapshot {selected_snapshot['name']} is not expired.")
                                        print("Exiting.")
                                        exit()  
                        else:
                            print("selected snapshot don't exists! Exiting")  
                            exit()                
                    else:
                        print("No snapshot selected. something whent wrong! Exiting.")  
                        exit             
                # else create a new one
                else:
                    print("no snapshots exist for this instance") 
                    new_snapshot = True       
                # create a new snapshot
                if new_snapshot: 
                    print("creating a new snapshot ####")    
                    #snapshot_name = input("Enter a name for the snapshot: ")
                    snapshot_name = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
                    #snapshot_description = input("Enter a description for the new snapshot: ")
                    snapshot_description = "snapshot created by make-snap-shot.py script - github.com/msvs/msvs-contabo-snapshot"
                    create_snapshot(access_token, selected_instance['instanceId'], snapshot_name, snapshot_description)
                    # --------------------
                    print("all done!!!")          
                else:
                    print("No snapshot selected. Exiting.")  
                    exit()       
            # --------------------
            else:
                print("No instance selected. Exiting.")
                exit()
        else:
            print("Failed to obtain instances.")
            exit()        
    else:
        print("Failed to obtain access token.")
        exit()   

