import streamlit as st
import subprocess
import os
import json
import time

# Configuration file path
CONFIG_FILE = 'waf_config.json'
LOG_FILE = 'waf.log'

# Function to load configuration
def load_config():
    if not os.path.exists(CONFIG_FILE):
        config = {
            "port": 8080,
            "blocked_countries": [],
            "sql_injection_patterns": [
                "union.*select.*\\(", "select.*from.*information_schema.tables",
                "select.*from.*mysql.user", "select.*from.*pg_user"
            ],
            "xss_patterns": [
                "<script.*?>.*?</script.*?>", "onerror.*?=", "alert.*?\\(", "eval.*?\\("
            ],
            "command_injection_patterns": [
                ".*;.*", ".*&&.*", ".*\\|\\|.*", ".*\\|.*", ".*`.*", ".*\\$\\(.*"
            ]
        }
        save_config(config)
    else:
        with open(CONFIG_FILE, 'r') as file:
            return json.load(file)
    return config

# Function to save configuration
def save_config(config):
    with open(CONFIG_FILE, 'w') as file:
        json.dump(config, file, indent=4)

# Function to start WAF with the provided target address
def start_waf(target_url):
    subprocess.Popen(["python", "waf.py", target_url])

# Function to read log
def read_log():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as file:
            return file.read()
    return ""

# Function to check for alerts
def check_for_alerts(log_content):
    alert_patterns = ["alert", "error", "warning"]
    alerts = [line for line in log_content.split('\n') if any(pattern in line.lower() for pattern in alert_patterns)]
    return alerts

# Streamlit UI
st.title("SHIELDON Web Application Firewall")

# Load current configuration
config = load_config()

# Input for target web application URL
target_url = st.text_input("Enter the target web application URL", "http://localhost:5000")

# Input for port number
port = st.number_input("Enter the port number for the WAF", value=config['port'])

# Set rate limit

rate_limit = st.number_input("Number of requests per IP allowed:", min_value=1, value=config.get('rate_limit', 100))
config['rate_limit'] = rate_limit

# Multi-select for blocked countries
countries = ['US', 'CN', 'RU', 'IN', 'BR']  # Add more country codes as needed
blocked_countries = st.multiselect("Select countries to block", countries, default=config['blocked_countries'])

if st.button("Start WAF"):
    config['port'] = port
    config['blocked_countries'] = blocked_countries
    save_config(config)
    start_waf(target_url)
    st.success(f"WAF started for target URL: {target_url}")
    st.write(f"Access the web application through: http://127.0.0.1:{port}")

# Display log details
st.subheader("Log Details")
log_area = st.empty()

# Display alert details
alert_area = st.empty()

# Monitor log updates
def display_updates():
    log_content = read_log()
    alerts = check_for_alerts(log_content)

    # Update log details
    log_area.text_area("WAF Log", log_content, height=300, key="log_area")

    # Update alert details
    if alerts:
        alert_area.subheader("Real-time Alerts")
        for alert in alerts:
            alert_area.write(alert)

# Main loop
if __name__ == "__main__":
    while True:
        display_updates()
        time.sleep(2)  # Poll every 2 seconds
        st.rerun()  # Refresh the Streamlit app
