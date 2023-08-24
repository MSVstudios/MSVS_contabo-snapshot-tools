**Contabo VPS Snapshot Management tool Script**

This script allows you to manage snapshots for your Contabo Virtual Private Servers (VPS) using the Contabo API. Snapshots are a way to capture a snapshot of your VPS at a particular point in time, which can be useful for creating backups, testing, or rolling back changes. This script provides various options to list, create, and manage snapshots.

**Usage:**

1. **Installation:** Before using the script, make sure you have Python installed on your system. Additionally, you'll need to install the required Python packages. You can install them using the following command:
   ```
   pip install requests python-dotenv
   ```

2. **Setting Up Environment:** Create a `.env` file in the same directory as the script and provide your Contabo API credentials (CLIENT_ID, CLIENT_SECRET, API_USER, API_PASSWORD) in the following format:
   ```
   CLIENT_ID=your_client_id
   CLIENT_SECRET=your_client_secret
   API_USER=your_api_user
   API_PASSWORD=your_api_password
   ```
   don't forget
   ```
   chmod 400 .env
   ```
   

3. **Run the Script:** Open a terminal, navigate to the directory containing the script, and run the script using the following command:
   ```
   python make-snap-shot.py [options]
   ```

4. **Options:**
   - `--all` or `-a`: Delete the oldest snapshot for all instances and create a new one for each instance.
   - `--instanceid` or `-ii`: Specify the instance ID for which you want to manage snapshots.
   - `--snapshotid` or `-is`: Specify the snapshot ID to directly target a specific snapshot.
   - `--force` or `-f`: Force deletion of an existing snapshot before creating a new one.
   - `--expired` or `-e`: Delete and recreate a snapshot if it's older than the specified number of days.
   - `--oldest` or `-o`: Delete the oldest snapshot for the specified instance without asking for confirmation.
   - `--verbose` or `-v`: Print verbose output for debugging.
   
**Examples:**

- To list all instances and their snapshots:
  ```
  python make-snap-shot.py
  ```

- To delete the oldest snapshot for a specific instance without asking for confirmation:
  ```
  python make-snap-shot.py --instanceid 12345 --oldest
  ```

- To recreate an existing snapshot for a specific instance:
  ```
  python make-snap-shot.py --instanceid 12345 --snapshotid snap123456 --force
  ```

- To delete and recreate an expired snapshot for a specific instance:
  ```
  python make-snap-shot.py --instanceid 12345 --expired 7
  ```

- To delete the oldest snapshot for all instances and create new snapshots:
  ```
  python make-snap-shot.py --all
  ```

5. **Build and Run the Docker Container:**  

 Open a terminal and navigate to the directory containing your project files. Run the following commands to build and run the Docker container:

 **Build the Docker image**
 ```
 docker build -t contabo-snapshot-tools .
 ```

 **Run the Docker container**
 ```
 docker run -d --name contabo-snapshot-container contabo-snapshot-tools
 ```

 This script provides a flexible way to manage snapshots for your Contabo VPS instances, allowing you to automate the process of creating, deleting, and managing snapshots based on your requirements. It's a powerful tool for ensuring the safety and integrity of 
 your VPS data.
