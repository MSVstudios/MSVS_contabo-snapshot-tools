# Use the official Alpine base image
FROM alpine:latest

# Install required packages
RUN apk update && apk add --no-cache python3 py3-pip

# Set working directory
WORKDIR /app

# Copy the script and .env file
COPY make-snap-shot.py .
COPY contabo-snapshot.sh .

# Copy the .env file
# COPY .env .
COPY .env .env.template /app/

# Install required Python packages
RUN pip3 install requests python-dotenv

# Add cron job file
COPY cronjob /etc/crontabs/root

# Make the script executable
RUN chmod +x make-snap-shot.py
RUN chmod +x contabo-snapshot.sh
RUN chmod 400 .env

# Start cron daemon
CMD crond -f
