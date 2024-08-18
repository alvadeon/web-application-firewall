import http.server
import socketserver
import requests
import re
import json
import logging
from urllib.parse import urlparse, parse_qs
import geoip2.database
import sys
import asyncio
import websockets
import time

# Configuration file path
CONFIG_FILE = 'waf_config.json'

# Load configuration
def load_config():
    with open(CONFIG_FILE, 'r') as file:
        return json.load(file)

config = load_config()
PORT = config['port']
blocked_countries = config['blocked_countries']
sql_injection_patterns = config['sql_injection_patterns']
xss_patterns = config['xss_patterns']
command_injection_patterns = config['command_injection_patterns']
rate_limit = config.get('rate_limit', 100)

# Logging configuration
logging.basicConfig(filename='waf.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# WebSocket clients
clients = set()

# WebSocket server
async def websocket_handler(websocket, path):
    clients.add(websocket)
    try:
        async for message in websocket:
            pass
    except websockets.ConnectionClosed:
        pass
    finally:
        clients.remove(websocket)

def is_sql_injection(query):
    for pattern in sql_injection_patterns:
        if re.search(pattern, query, re.IGNORECASE):
            return True
    return False

def is_xss(query):
    for pattern in xss_patterns:
        if re.search(pattern, query, re.IGNORECASE):
            return True
    return False

def is_command_injection(query):
    for pattern in command_injection_patterns:
        if re.search(pattern, query, re.IGNORECASE):
            return True
    return False

def get_country_from_ip(ip):
    if ip == '127.0.0.1' or ip == 'localhost':
        return 'LOCAL'
    try:
        reader = geoip2.database.Reader('GeoLite2-Country.mmdb')
        response = reader.country(ip)
        return response.country.iso_code
    except Exception as e:
        logging.error(f"Error getting country for IP {ip}: {e}")
        return None

# Rate limiting data structure
ip_requests = {}

def rate_limit_exceeded(ip):
    current_time = time.time()
    if ip not in ip_requests:
        ip_requests[ip] = []
    # Clean up old requests
    ip_requests[ip] = [timestamp for timestamp in ip_requests[ip] if current_time - timestamp < 60]  # 60 seconds window
    if len(ip_requests[ip]) >= rate_limit:
        return True
    ip_requests[ip].append(current_time)
    return False

class ProxyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.handle_request()

    def do_POST(self):
        self.handle_request()

    def handle_request(self):
        url = f"{target_url}{self.path}"
        headers = {key: value for key, value in self.headers.items() if key != 'Host'}

        # Check for blocked country
        client_ip = self.client_address[0]
        country_code = get_country_from_ip(client_ip)
        if country_code in blocked_countries:
            self.send_error(403, "Access forbidden: your country is blocked")
            logging.info(f"ALERT: Blocked request from {client_ip} (Country: {country_code})")
            asyncio.run(send_alert(f"Blocked request from {client_ip} (Country: {country_code})"))
            return

        # Rate limit check
        if rate_limit_exceeded(client_ip):
            self.send_error(429, "Too many requests")
            logging.info(f"ALERT: Rate limit exceeded by {client_ip}")
            asyncio.run(send_alert(f"Rate limit exceeded by {client_ip}"))
            return

        # Check for SQL injection, XSS, and command injection
        parsed_url = urlparse(self.path)
        query_string = parse_qs(parsed_url.query)
        if any(is_sql_injection(value[0]) or is_xss(value[0]) or is_command_injection(value[0]) for value in query_string.values()):
            self.send_error(403, "Malicious request detected")
            logging.info(f"ALERT: Blocked SQL injection or XSS attempt from {client_ip} on URL {self.path}")
            asyncio.run(send_alert(f"Blocked SQL injection or XSS attempt from {client_ip} on URL {self.path}"))
            return

        if self.command == 'GET':
            response = requests.get(url, headers=headers)
        elif self.command == 'POST':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            if is_sql_injection(post_data) or is_xss(post_data) or is_command_injection(post_data):
                self.send_error(403, "Malicious request detected")
                logging.info(f"ALERT: Blocked SQL injection or XSS attempt from {client_ip} in POST data")
                asyncio.run(send_alert(f"Blocked SQL injection or XSS attempt from {client_ip} in POST data"))
                return
            response = requests.post(url, headers=headers, data=post_data)

        self.send_response(response.status_code)
        for key, value in response.headers.items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(response.content)

async def send_alert(message):
    if clients:
        await asyncio.wait([client.send(message) for client in clients])

def check_sql_injection(ip, query):
    if is_sql_injection(query):
        logging.info(f"Blocked SQL injection attempt from {ip}")
        return "Blocked: SQL injection attempt detected"
    return "Allowed"

def check_xss_and_command_injection(ip, query):
    if is_xss(query):
        logging.info(f"Blocked XSS attempt from {ip}")
        return "Blocked: XSS attempt detected"
    if is_command_injection(query):
        logging.info(f"Blocked command injection attempt from {ip}")
        return "Blocked: Command injection attempt detected"
    return "Allowed"

if __name__ == "__main__":
    target_url = sys.argv[1]
    # Start WebSocket server
    start_server = websockets.serve(websocket_handler, "localhost", 8766)
    asyncio.get_event_loop().run_until_complete(start_server)

    # Start HTTP proxy server
    with socketserver.TCPServer(("", PORT), ProxyHTTPRequestHandler) as httpd:
        logging.info(f"Starting WAF on port {PORT} targeting {target_url}...")
        asyncio.get_event_loop().run_in_executor(None, httpd.serve_forever)
        asyncio.get_event_loop().run_forever()
