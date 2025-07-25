import os
import base64
from collections import OrderedDict
from time import sleep
from typing import Optional, Tuple
import requests
import re


class TotalConnectClient:

    def __init__(self, jsession_id = None, session_token: Optional[str] = None):

        self.username = None
        self.password = None

        self.load_credentials()

        # Set credentials
        self.username = self.username or os.getenv("EVO_SECURITY_USERNAME")
        self.password = self.password or os.getenv("EVO_SECURITY_PASSWORD")
        self.base_url = "https://tc20e.total-connect.eu"

        self.session = requests.Session()

        self.jsession_id = jsession_id
        self.session_token = session_token

    def load_credentials(self):

        try:
            with open('.env', 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        os.environ[key] = value
                        print(f"Loaded environment variable: {key}")
        except Exception as e:
            print(f"Error loading .env file: {str(e)}")


    def authenticate(self):

        print("Authenticating with Total Connect...")

        from collections import OrderedDict
        start_headers = OrderedDict([
            ("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"),
            ("Accept-Encoding", "gzip, deflate, br, zstd"),
            ("Accept-Language", "en-GB,en;q=0.9,en-US;q=0.8,pl;q=0.7"),
            ("Connection", "keep-alive"),
            ("DNT", "1"),
            ("Host", "tc20e.total-connect.eu"),
            ("Sec-Fetch-Dest", "document"),
            ("Sec-Fetch-Mode", "navigate"),
            ("Sec-Fetch-Site", "none"),
            ("Sec-Fetch-User", "?1"),
            ("Upgrade-Insecure-Requests", "1"),
            ("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"),
            ("sec-ch-ua", '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"'),
            ("sec-ch-ua-mobile", "?0"),
            ("sec-ch-ua-platform", '"macOS"')
        ])


        # First, visit the main page to get initial cookies
        response = self.session.get(self.base_url, headers=start_headers)

        jsessionid = response.cookies.get("JSESSIONID")
        # self.session.cookies.setdefault("JSESSIONID", jsessionid)

        if not response.ok:
            print("Response is not OK, check your credentials or network connection." + response.status_code)
            return False

        # Create the Basic Auth header
        auth_string = f"{self.username}:{self.password}:1:0"
        auth_bytes = auth_string.encode('ascii')
        base64_bytes = base64.b64encode(auth_bytes)
        base64_auth = base64_bytes.decode('ascii')

        import time
        timestamp = int(time.time() * 1000)

        # Send the validation request with timestamp
        validate_url = f"{self.base_url}/validate?_={timestamp}"

        auth_headers = OrderedDict([

                ("Accept", "*/*"),
                ("Accept-Encoding", "gzip, deflate, br, zstd"),
                ("Accept-Language", "en-GB,en;q=0.9,en-US;q=0.8,pl;q=0.7"),
                ("Authorization", f"Basic {base64_auth}"),
                ("Connection", "keep-alive"),
                ("DNT", "1"),
                ("Host", "tc20e.total-connect.eu"),
                ("Referer", "https://tc20e.total-connect.eu/"),
                ("Sec-Fetch-Dest", "empty"),
                ("Sec-Fetch-Mode", "cors"),
                ("Sec-Fetch-Site", "same-origin"),
                ("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"),
                ("X-Requested-With", "XMLHttpRequest"),
                ("sec-ch-ua", '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"'),
                ("sec-ch-ua-mobile", "?0"),
                ("sec-ch-ua-platform", '"macOS"'),
                ("x-captcha", ""),
                ("x-remember-me", "false"),
                ("x-requested-with", "XMLHttpRequest")
        ])


        validate_response = self.session.get(validate_url, headers=auth_headers)
        print("Validate Response Status Code:", validate_response.status_code)
        print("Validate Response:", validate_response.text)

        self.session_token = self.extract_session_token()


    def extract_session_token(self):

        home_url = f"{self.base_url}/go/home"
        response = self.session.get(home_url)

        home_html = response.text

        idx = home_html.find('homeSessionId')
        start = max(0, idx - 50)
        end = min(len(home_html), idx + 100)

        pattern = r"homeSessionId\s*=\s*['\"]([^'\"]+)['\"]"
        match = re.search(pattern, home_html)

        if not match:
            print(f"DID NOT Found homeSessionId using pattern: {pattern}")

        return match.group(1)

    def get_status(self):

        print("Getting status...")

        status_url = f"{self.base_url}/applicationservice/domoweb/panel/commands/status?isBusy=true&checkCompletion=true"

        status_headers = OrderedDict(
            [
                ("Accept", "application/json, text/javascript, */*; q=0.01"),
                ("Accept-Encoding", "gzip, deflate, br, zstd"),
                ("Accept-Language", "en-GB,en;q=0.9"),
                ("Connection", "keep-alive"),
                ("Content-Type", "application/json; charset=UTF-8"),
                ("DNT", "1"),
                ("Host", "tc20e.total-connect.eu"),
                ("Origin", "https://tc20e.total-connect.eu"),
                ("Referer", "https://tc20e.total-connect.eu/go/home"),
                ("Sec-Fetch-Dest", "empty"),
                ("Sec-Fetch-Mode", "cors"),
                ("Sec-Fetch-Site", "same-origin"),
                ("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"),
                ("X-Requested-With", "XMLHttpRequest"),
                ("sec-ch-ua", '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"'),
                ("sec-ch-ua-mobile", "?0"),
                ("sec-ch-ua-platform", '"macOS"'),
                ("x-session-token", f"{self.session_token}"),
            ]
        )

        status_response = self.session.put(status_url, headers=status_headers, json={"key":"","value":""})

        print("Status Response Status Code:", status_response.status_code)
        print("Status Response:", status_response.text)

    def disarm(self):

        print("Disarming the system...")

        disarm_url = f"{self.base_url}/applicationservice/domoweb/panel/commands/disarm?isBusy=true&checkCompletion=true"

        disarm_headers = OrderedDict([
            ("Accept", "application/json, text/javascript, */*; q=0.01"),
            ("Accept-Encoding", "gzip, deflate, br, zstd"),
            ("Accept-Language", "en-GB,en;q=0.9"),
            ("Connection", "keep-alive"),
            ("Content-Type", "application/json; charset=UTF-8"),
            ("DNT", "1"),
            ("Host", "tc20e.total-connect.eu"),
            ("Origin", "https://tc20e.total-connect.eu"),
            ("Referer", "https://tc20e.total-connect.eu/go/home"),
            ("Sec-Fetch-Dest", "empty"),
            ("Sec-Fetch-Mode", "cors"),
            ("Sec-Fetch-Site", "same-origin"),
            ("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"),
            ("X-Requested-With", "XMLHttpRequest"),
            ("sec-ch-ua", '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"'),
            ("sec-ch-ua-mobile", "?0"),
            ("sec-ch-ua-platform", '"macOS"'),
            ("x-session-token", f"{self.session_token}")
        ])

        disarm_response = self.session.put(disarm_url, headers=disarm_headers, json={"key":"disarmCode","value":""})

        print("Disarm Response Status:", disarm_response.status_code)
        print("Disarm Response:", disarm_response.text)

    def partial_arm(self):

        print("Partially arming the system...")

        partial_arm_url = f"{self.base_url}/applicationservice/domoweb/panel/commands/partialarm?isBusy=true&checkCompletion=true"

        partial_arm_headers = OrderedDict([
            ("Accept", "application/json, text/javascript, */*; q=0.01"),
            ("Accept-Encoding", "gzip, deflate, br, zstd"),
            ("Accept-Language", "en-GB,en;q=0.9"),
            ("Connection", "keep-alive"),
            ("Content-Type", "application/json; charset=UTF-8"),
            ("DNT", "1"),
            ("Host", "tc20e.total-connect.eu"),
            ("Origin", "https://tc20e.total-connect.eu"),
            ("Referer", "https://tc20e.total-connect.eu/go/home"),
            ("Sec-Fetch-Dest", "empty"),
            ("Sec-Fetch-Mode", "cors"),
            ("Sec-Fetch-Site", "same-origin"),
            ("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"),
            ("X-Requested-With", "XMLHttpRequest"),
            ("sec-ch-ua", '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"'),
            ("sec-ch-ua-mobile", "?0"),
            ("sec-ch-ua-platform", '"macOS"'),
            ("x-session-token", f"{self.session_token}")
        ])

        partial_arm_response =  self.session.put(partial_arm_url, headers=partial_arm_headers, json={"key":"","value":""})
        print("Partial Arm Response Status:", partial_arm_response.status_code)
        print("Partial Arm Response:", partial_arm_response.text)


    def total_arm(self):

        total_arm_url = f"{self.base_url}/applicationservice/domoweb/panel/commands/arm?isBusy=true&checkCompletion=true"

        total_arm_headers = OrderedDict([
            ("Accept", "application/json, text/javascript, */*; q=0.01"),
            ("Accept-Encoding", "gzip, deflate, br, zstd"),
            ("Accept-Language", "en-GB,en;q=0.9"),
            ("Connection", "keep-alive"),
            ("Content-Type", "application/json; charset=UTF-8"),
            ("DNT", "1"),
            ("Host", "tc20e.total-connect.eu"),
            ("Origin", "https://tc20e.total-connect.eu"),
            ("Referer", "https://tc20e.total-connect.eu/go/home"),
            ("Sec-Fetch-Dest", "empty"),
            ("Sec-Fetch-Mode", "cors"),
            ("Sec-Fetch-Site", "same-origin"),
            ("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"),
            ("X-Requested-With", "XMLHttpRequest"),
            ("sec-ch-ua", '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"'),
            ("sec-ch-ua-mobile", "?0"),
            ("sec-ch-ua-platform", '"macOS"'),
            ("x-session-token", f"{self.session_token}"),
        ])

        total_arm_response = self.session.put(total_arm_url, headers=total_arm_headers, json={"key":"","value":""})
        print("Total Arm Response Status:", total_arm_response.status_code)
        print("Total Arm Response:", total_arm_response.text)

    def logout(self):

        logout_headers = OrderedDict([
            ("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"),
            ("Accept-Encoding", "gzip, deflate, br, zstd"),
            ("Accept-Language", "en-GB,en;q=0.9"),
            ("Connection", "keep-alive"),
            ("DNT", "1"),
            ("Host", "tc20e.total-connect.eu"),
            ("Referer", "https://tc20e.total-connect.eu/go/home"),
            ("Sec-Fetch-Dest", "document"),
            ("Sec-Fetch-Mode", "navigate"),
            ("Sec-Fetch-Site", "same-origin"),
            ("Sec-Fetch-User", "?1"),
            ("Upgrade-Insecure-Requests", "1"),
            ("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"),
            ("sec-ch-ua", '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"'),
            ("sec-ch-ua-mobile", "?0"),
            ("sec-ch-ua-platform", '"macOS"')
        ])

        logout_url = f"{self.base_url}/logout"
        logout_response = self.session.get(logout_url, headers=logout_headers, allow_redirects=False)
        print("Logout Response Status:", logout_response.status_code)

# Example usage
if __name__ == "__main__":
    # Example usage of the simplified get_status2 method
    # You would need to provide actual JSESSIONID and session token values
    jsessionid = None  # Example value
    # jsessionid = "KP4Yoe2kK6Li_UP7tywlavCUrIWEvwn_I3UqfnUN.prod-tc20e-810-ws1"  # Example value
    session_token = None  # Example value
    # session_token = "OOuvUbHsFTu00hDT1BK6A7yJ_yn5NZbkxNh82F8c"  # Example value

    # Create client
    client = TotalConnectClient()

    try:
        client.authenticate()
        client.get_status()
        sleep(5)
        client.total_arm()
        sleep(5)
        # client.get_status()
        # sleep(5)
        client.disarm()
        sleep(5)
        # client.get_status()
        # sleep(5)
    finally:
        client.logout()