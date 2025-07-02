import subprocess
import platform
import re
import logging
import time

import csv
from datetime import datetime

import smtplib
from email.mime.text import MIMEText

import schedule

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def ping_host(host, count=1, timeout=1):
    """
    Pings a given host and returns True if successful, False otherwise.
    Also returns the ping output for detailed analysis.

    Args:
        host (str): The IP address or hostname to ping.
        count (int): The number of packets to send (default: 1).
        timeout (int): Timeout in seconds for each packet (default: 1).

    Returns:
        tuple: (bool success, str raw_output)
    """
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    timeout_param = '-w' if platform.system().lower() == 'windows' else '-W'

    command = ['ping', param, str(count), timeout_param, str(timeout), host]

    try:
        # Run the ping command
        result = subprocess.run(command, capture_output=True, text=True, timeout=timeout * (count + 2)) # Added buffer to timeout

        raw_output = result.stdout + result.stderr

        if result.returncode == 0:
            logging.info(f"Ping successful for {host}.")
            return True, raw_output
        else:
            logging.warning(f"Ping failed for {host}. Return code: {result.returncode}")
            logging.debug(f"Ping output for {host}:\n{raw_output}")
            return False, raw_output
    except subprocess.TimeoutExpired:
        logging.error(f"Ping command timed out for {host}.")
        return False, "TimeoutExpired"
    except FileNotFoundError:
        logging.error("Ping command not found. Make sure ping is installed and in your PATH.")
        return False, "FileNotFound"
    except Exception as e:
        logging.error(f"An unexpected error occurred while pinging {host}: {e}")
        return False, str(e)

# Example usage:
# ... (previous code for ping_host and imports) ...


def monitor_hosts(host_list, interval_seconds=60, count=1, timeout=1):
    """
    Continuously monitors a list of hosts.

    Args:
        host_list (list): A list of IP addresses or hostnames to monitor.
        interval_seconds (int): How often to ping each host (in seconds).
        count (int): Number of packets per ping.
        timeout (int): Timeout per packet.
    """
    logging.info(f"Starting host monitoring for: {host_list}")
    while True:
        for host in host_list:
            logging.info(f"Pinging {host}...")
            success, output = ping_host(host, count=count, timeout=timeout)
            if success:
                # You might want to parse and store latency data here
                logging.info(f"{host} is reachable.")
            else:
                logging.error(f"{host} is unreachable!")
                # Add alert mechanisms here (email, SMS, etc.)
        logging.info(f"Waiting for {interval_seconds} seconds before next cycle...")
        time.sleep(interval_seconds)

def log_ping_result_to_csv(host, success, raw_output, filename="ping_log.csv"):
    """
    Logs ping results to a CSV file.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status = "Success" if success else "Failed"
    latency = "N/A" # Default
    packet_loss = "N/A" # Default

    # Attempt to parse latency and packet loss from raw_output
    if platform.system().lower() == 'windows':
        latency_match = re.search(r"Average = (\d+)ms", raw_output)
        if latency_match:
            latency = f"{latency_match.group(1)}ms"
        loss_match = re.search(r"Packets: Sent = \d+, Received = \d+, Lost = \d+ \((\d+)% loss\)", raw_output)
        if loss_match:
            packet_loss = f"{loss_match.group(1)}%"
    else: # Linux/macOS
        latency_match = re.search(r"min/avg/max/mdev = [\d.]+/([\d.]+)/[\d.]+/\S+ ms", raw_output)
        if latency_match:
            latency = f"{latency_match.group(1)}ms"
        loss_match = re.search(r"(\d+)% packet loss", raw_output)
        if loss_match:
            packet_loss = f"{loss_match.group(1)}%"

    data = [timestamp, host, status, latency, packet_loss, raw_output.strip().replace('\n', ' ')]

    try:
        with open(filename, 'a', newline='') as f:
            writer = csv.writer(f)
            # Write header if file is empty
            if f.tell() == 0:
                writer.writerow(["Timestamp", "Host", "Status", "Latency", "Packet Loss", "Raw Output"])
            writer.writerow(data)
        logging.debug(f"Logged result for {host} to {filename}")
    except Exception as e:
        logging.error(f"Error writing to CSV file {filename}: {e}")

# Modify monitor_hosts to use CSV logging
def monitor_hosts_with_csv(host_list, interval_seconds=60, count=1, timeout=1, log_file="ping_results.csv"):
    logging.info(f"Starting host monitoring (with CSV logging) for: {host_list}")
    while True:
        for host in host_list:
            logging.info(f"Pinging {host}...")
            success, output = ping_host(host, count=count, timeout=timeout)
            log_ping_result_to_csv(host, success, output, filename=log_file)
            if success:
                logging.info(f"{host} is reachable.")
            else:
                logging.error(f"{host} is unreachable!")
        logging.info(f"Waiting for {interval_seconds} seconds before next cycle...")
        time.sleep(interval_seconds)

# Email configuration (replace with your actual details)
EMAIL_SENDER = "your_email@example.com"
EMAIL_PASSWORD = "your_email_password" # Use app-specific passwords for Gmail/Outlook
EMAIL_RECEIVER = "alert_recipient@example.com"
SMTP_SERVER = "smtp.example.com" # e.g., "smtp.gmail.com" for Gmail
SMTP_PORT = 587 # 465 for SSL, 587 for TLS

def send_alert_email(subject, body):
    """
    Sends an email alert.
    """
    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = EMAIL_SENDER
        msg['To'] = EMAIL_RECEIVER

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Upgrade connection to TLS
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
        logging.info(f"Email alert sent: '{subject}'")
    except Exception as e:
        logging.error(f"Failed to send email alert: {e}")

# Modify monitor_hosts to include email alerts
def monitor_hosts_with_alerts(host_list, interval_seconds=60, count=1, timeout=1):
    logging.info(f"Starting host monitoring (with email alerts) for: {host_list}")
    while True:
        for host in host_list:
            logging.info(f"Pinging {host}...")
            success, output = ping_host(host, count=count, timeout=timeout)
            if not success:
                subject = f"CRITICAL: Host {host} is DOWN!"
                body = f"Ping to {host} failed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.\n\nRaw Output:\n{output}"
                logging.critical(body)
                send_alert_email(subject, body)
            else:
                logging.info(f"{host} is reachable.")
        logging.info(f"Waiting for {interval_seconds} seconds before next cycle...")
        time.sleep(interval_seconds)

HOSTS_TO_MONITOR_SCHEDULE = ["8.8.8.8", "google.com"]

def job_ping_hosts():
    logging.info("Running scheduled ping job...")
    for host in HOSTS_TO_MONITOR_SCHEDULE:
        success, output = ping_host(host)
        log_ping_result_to_csv(host, success, output, filename="scheduled_ping_results.csv")
        if not success:
            subject = f"ALERT: Scheduled Ping Failed for {host}"
            body = f"Host {host} is unreachable at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.\n\nOutput:\n{output}"
            logging.error(body)
            # send_alert_email(subject, body) # Uncomment to enable email alerts   

if __name__ == "__main__":
    target_host = "8.8.8.8"  # Google's public DNS server
    success, output = ping_host(target_host)

    if success:
        print(f"Successfully pinged {target_host}")
        # You can parse the output here for more details if needed
        # For example, to get average latency:
        if platform.system().lower() == 'windows':
            match = re.search(r"Average = (\d+)ms", output)
            if match:
                print(f"Average latency: {match.group(1)}ms")
        else:   # Linux/macOS
            match = re.search(r"min/avg/max/mdev = [\d.]+/([\d.]+)/[\d.]+/\S+ ms", output)
            if match:
                print(f"Average latency: {match.group(1)}ms")
    else:
        print(f"Failed to ping {target_host}")
        print(f"Raw output:\n{output}")
    hosts_to_monitor = ["8.8.8.8", "google.com", "192.168.1.1"] # Example hosts
    # Be careful with 192.168.1.1 if it's not your gateway or doesn't exist

    # Run the monitoring in a loop (uncomment to run)
    # monitor_hosts(hosts_to_monitor, interval_seconds=10)
    print("Run `monitor_hosts` function to start continuous monitoring.")
    # Example for CSV logging:
    # hosts_to_monitor = ["8.8.8.8", "google.com"]
    # monitor_hosts_with_csv(hosts_to_monitor, interval_seconds=10, log_file="my_network_ping_log.csv")
    print("Uncomment `monitor_hosts_with_csv` to start continuous monitoring with CSV logging.")
    # Example for email alerts:
    # IMPORTANT: Replace placeholder email credentials before running!
    # hosts_to_monitor = ["google.com", "nonexistent-domain-12345.com"]
    # monitor_hosts_with_alerts(hosts_to_monitor, interval_seconds=10)
    print("Uncomment `monitor_hosts_with_alerts` and configure email settings to enable alerts.")
     # Schedule the job
    schedule.every(1).minute.do(job_ping_hosts)
    # schedule.every().hour.do(job_ping_hosts)
    # schedule.every().day.at("10:30").do(job_ping_hosts)

    print("Scheduler started. Press Ctrl+C to stop.")
    while True:
        schedule.run_pending()
        time.sleep(1)