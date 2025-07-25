import requests
from enum import Enum
from typing import Optional
from dataclasses import dataclass
import time
import logging
import json
from datetime import datetime, timedelta

class ArmStatus(Enum):
    DISARMED = "Disarmed"
    PARTIAL_ARM = "Partial Armed"
    TOTAL_ARM = "Total Armed"

class SecurityCommand(Enum):
    DISARM = 2
    PARTIAL_ARM = 3
    TOTAL_ARM = 4

@dataclass
class SecurityConfig:
    username: str
    password: str
    base_url: str = "https://tc20e.total-connect.eu"
    log_level: int = logging.INFO

class SecuritySystem:
    def __init__(self, config: SecurityConfig):
        self.config = config
        self._logged_in = False
        self._last_request_time = datetime.min
        self._min_request_interval = timedelta(seconds=2)  # Minimum 2 seconds between requests

        # Set up logging
        self.logger = logging.getLogger("evosec")
        self.logger.setLevel(config.log_level)

        # Add a console handler if none exists
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

        # Create a session with request/response hooks for logging
        self.session = requests.Session()

        # Add request and response hooks for logging
        self.session.hooks['response'] = [self._log_response]
        self.session.hooks['request'] = [self._log_request]

    def _mask_sensitive_data(self, data):
        """Mask sensitive data like passwords in logs."""
        if not data:
            return data

        # Create a copy to avoid modifying the original
        if isinstance(data, dict):
            masked_data = data.copy()
            # Mask sensitive fields
            for key in masked_data:
                if key.lower() in ['password', 'pwd', 'secret', 'token', 'key', 'auth', 'credential']:
                    if isinstance(masked_data[key], str) and masked_data[key]:
                        # Keep first 2 and last 2 chars, mask the rest
                        if len(masked_data[key]) > 4:
                            masked_data[key] = masked_data[key][:2] + '*' * (len(masked_data[key]) - 4) + masked_data[key][-2:]
                        else:
                            masked_data[key] = '****'
            return masked_data
        elif isinstance(data, str):
            # Try to parse as JSON
            try:
                json_data = json.loads(data)
                masked_json = self._mask_sensitive_data(json_data)
                return json.dumps(masked_json)
            except:
                # Not JSON, return as is
                return data
        return data

    def _log_request(self, request, **kwargs):
        """Log HTTP request details."""
        method = request.method
        url = request.url

        # Log the request
        self.logger.info(f"HTTP Request: {method} {url}")

        # Log headers
        headers = dict(request.headers)
        masked_headers = self._mask_sensitive_data(headers)
        self.logger.debug(f"Request Headers: {masked_headers}")

        # Log body for POST/PUT requests
        if method in ['POST', 'PUT', 'PATCH']:
            body = None
            if hasattr(request, 'body') and request.body:
                if isinstance(request.body, bytes):
                    try:
                        body = request.body.decode('utf-8')
                    except:
                        body = f"<Binary data: {len(request.body)} bytes>"
                else:
                    body = request.body

                # Mask sensitive data
                if body:
                    masked_body = self._mask_sensitive_data(body)
                    self.logger.debug(f"Request Body: {masked_body}")

        return request

    def _log_response(self, response, **kwargs):
        """Log HTTP response details."""
        request = response.request
        method = request.method
        url = request.url
        status_code = response.status_code

        # Log the response
        self.logger.info(f"HTTP Response: {method} {url} - Status: {status_code}")

        # Log headers
        headers = dict(response.headers)
        masked_headers = self._mask_sensitive_data(headers)
        self.logger.debug(f"Response Headers: {masked_headers}")

        # Log body
        if hasattr(response, 'text') and response.text:
            # Try to parse as JSON for prettier logging
            try:
                body = json.loads(response.text)
                masked_body = self._mask_sensitive_data(body)
                self.logger.debug(f"Response Body: {json.dumps(masked_body, indent=2)}")
            except:
                # Not JSON, log as text (truncated if too long)
                text = response.text
                if len(text) > 1000:
                    text = text[:1000] + "... [truncated]"
                self.logger.debug(f"Response Body: {text}")

        return response

    def login(self) -> bool:
        """Log in to the security system.

        The login process is complex and involves multiple steps:
        1. Visit the login page to get cookies and CSRF token
        2. Submit the login form with credentials
        3. Validate the session with a timestamp
        4. Check if login was successful
        """
        try:
            # Clear any existing session
            self.session = requests.Session()

            # Step 1: Visit the login page to get cookies and CSRF token
            self.logger.debug(f"Visiting login page: {self.config.base_url}")
            self._rate_limit()  # Apply rate limiting
            response = self.session.get(self.config.base_url)
            if not response.ok:
                self.logger.error(f"Failed to access login page: {response.status_code}")
                return False

            # Step 2: Try different login approaches

            # Approach 1: Try direct login to /go/home with form data
            login_url = f"{self.config.base_url}/go/home"
            login_data = {
                "username": self.config.username,
                "password": self.config.password,
                "language": "en"
            }

            self.logger.debug(f"Trying direct login to: {login_url}")
            self._rate_limit()  # Apply rate limiting
            response = self.session.post(login_url, data=login_data, allow_redirects=True)
            self.logger.debug(f"Login response status code: {response.status_code}")

            # Check if login was successful
            if response.ok:
                html = response.text.lower()
                if "logout" in html or "sign out" in html or "panel" in html:
                    self.logger.info("Login successful (found logout/panel indicator in HTML)")
                    # Validate the session with a timestamp
                    if self._validate_session():
                        self._logged_in = True
                        return True

            # Approach 2: Try login with applicationservice endpoint
            login_url = f"{self.config.base_url}/applicationservice/applicationuser/authentication"
            login_json = {
                "username": self.config.username,
                "password": self.config.password,
                "language": "en"
            }

            self.logger.debug(f"Trying authentication endpoint: {login_url}")
            self._rate_limit()  # Apply rate limiting
            response = self.session.post(login_url, json=login_json, allow_redirects=True)
            self.logger.debug(f"Authentication response status code: {response.status_code}")

            # Check if we got a session token
            if response.ok and "x-session-token" in response.headers:
                session_token = response.headers["x-session-token"]
                self.logger.debug(f"Found session token in headers")
                # Add session token to all future requests
                self.session.headers.update({"x-session-token": session_token})
                # Validate the session with a timestamp
                if self._validate_session():
                    self._logged_in = True
                    return True

            # Approach 3: Try login with a GET request to /go/home
            login_url = f"{self.config.base_url}/go/home"
            login_params = {
                "username": self.config.username,
                "password": self.config.password,
                "language": "en"
            }

            self.logger.debug(f"Trying GET login to: {login_url}")
            self._rate_limit()  # Apply rate limiting
            response = self.session.get(login_url, params=login_params, allow_redirects=True)
            self.logger.debug(f"GET login response status code: {response.status_code}")

            # Check if login was successful
            if response.ok:
                html = response.text.lower()
                if "logout" in html or "sign out" in html or "panel" in html:
                    self.logger.info("Login successful (found logout/panel indicator in HTML)")
                    # Validate the session with a timestamp
                    if self._validate_session():
                        self._logged_in = True
                        return True

            # If we got here, all login attempts failed
            self.logger.error("All login attempts failed")
            self._logged_in = False
            return False

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Login request exception: {str(e)}")
            self._logged_in = False
            return False

    def _ensure_logged_in(self):
        """Ensure we're logged in, attempting to login if not."""
        if not self._logged_in:
            if not self.login():
                raise Exception("Failed to log in to security system")
        else:
            # Even if we're logged in, validate the session to ensure it's still valid
            if not self._validate_session():
                self.logger.warning("Session validation failed, trying to log in again")
                if not self.login():
                    raise Exception("Failed to log in to security system")

    def _rate_limit(self):
        """Enforce rate limiting to prevent spamming the server."""
        now = datetime.now()
        time_since_last_request = now - self._last_request_time

        if time_since_last_request < self._min_request_interval:
            # Calculate how much time to wait
            wait_time = (self._min_request_interval - time_since_last_request).total_seconds()
            self.logger.debug(f"Rate limiting - waiting {wait_time:.2f} seconds")
            time.sleep(wait_time)

        # Update the last request time
        self._last_request_time = datetime.now()

    def _validate_session(self) -> bool:
        """Validate the session with a timestamp.

        According to the issue description, there might be a validation step that includes
        a timestamp in the URL: https://tc20e.total-connect.eu/validate?_=1753263500655

        Also, there might be a JavaScript variable called homeSessionId that is returned
        in the pages and used in subsequent requests.

        This method sends a request to the validate endpoint with a current timestamp
        and looks for the homeSessionId variable in the response.
        """
        try:
            # First, try to get the home page to look for the homeSessionId variable
            self.logger.debug(f"Getting home page to look for homeSessionId")
            self._rate_limit()  # Apply rate limiting
            response = self.session.get(f"{self.config.base_url}/go/home")

            if response.ok:
                # Look for the homeSessionId variable in the HTML
                html = response.text
                self._extract_home_session_id(html)

            # Generate a timestamp (milliseconds since epoch)
            timestamp = int(datetime.now().timestamp() * 1000)

            # Construct the validate URL with the timestamp
            validate_url = f"{self.config.base_url}/validate?_={timestamp}"

            self.logger.debug(f"Validating session with URL: {validate_url}")
            self._rate_limit()  # Apply rate limiting

            # Add the homeSessionId as a query parameter if we have it
            home_session_id = self.session.headers.get("x-session-token")
            if home_session_id:
                validate_url += f"&homeSessionId={home_session_id}"

            response = self.session.get(validate_url)

            if response.ok:
                self.logger.debug(f"Session validation successful")

                # Check if the response contains a homeSessionId
                try:
                    data = response.json()
                    if "homeSessionId" in data:
                        home_session_id = data["homeSessionId"]
                        self.logger.debug(f"Found homeSessionId in validate response: {home_session_id}")
                        # Add the homeSessionId to the session headers
                        self.session.headers.update({"x-session-token": home_session_id})
                except:
                    # If it's not JSON, try to extract from HTML
                    self._extract_home_session_id(response.text)

                return True
            else:
                self.logger.warning(f"Session validation failed: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Session validation request exception: {str(e)}")
            return False

    def _extract_home_session_id(self, html):
        """Extract the homeSessionId from HTML content.

        This method tries various patterns to find the homeSessionId variable
        in the HTML content. If found, it adds it to the session headers.

        Args:
            html: The HTML content to search in

        Returns:
            The extracted homeSessionId, or None if not found
        """
        if not html:
            return None

        home_session_id = None

        # Try different patterns to find the homeSessionId
        patterns = [
            # Standard JavaScript variable declaration
            r"var\s+homeSessionId\s*=\s*['\"]([^'\"]+)['\"]",
            # Assignment without var
            r"homeSessionId\s*=\s*['\"]([^'\"]+)['\"]",
            # Object property
            r"homeSessionId['\"]?\s*:\s*['\"]([^'\"]+)['\"]",
            # JSON format
            r"\"homeSessionId\":\s*\"([^\"]+)\"",
            # Hidden input field
            r"<input[^>]*name=['\"]homeSessionId['\"][^>]*value=['\"]([^'\"]+)['\"]",
            # Data attribute
            r"data-home-session-id=['\"]([^'\"]+)['\"]",
            # Meta tag
            r"<meta[^>]*name=['\"]homeSessionId['\"][^>]*content=['\"]([^'\"]+)['\"]"
        ]

        import re
        for pattern in patterns:
            match = re.search(pattern, html)
            if match:
                home_session_id = match.group(1)
                self.logger.debug(f"Found homeSessionId: {home_session_id}")
                # Add the homeSessionId to the session headers as x-session-token
                self.session.headers.update({"x-session-token": home_session_id})
                # Also store it as a cookie
                self.session.cookies.set("homeSessionId", home_session_id)
                break

        if not home_session_id:
            self.logger.debug(f"Could not find homeSessionId in HTML")

        return home_session_id

    def execute_status_command(self) -> bool:
        """Execute the status command to get the current status.

        According to the issue description, we need to click the button with the following HTML:
        <div class="systemStatusIcon desktop" onclick="executeCommand(enumCommand.STATUS);">
            <div class="securityIconDefault"></div>
        </div>

        This suggests that we need to execute a JavaScript command executeCommand(enumCommand.STATUS)
        to get the status. Since we're using Python requests and not a browser, we need to find the
        equivalent HTTP request that this JavaScript function would make.

        Based on the Playwright analyzer, we know that clicking this button sends a request to get
        the current status of the system.
        """
        try:
            # First, ensure we're logged in
            self._ensure_logged_in()

            # Based on the findings from the Playwright analyzer, the status command is a GET request
            # to the home page followed by checking specific elements for status information
            self.logger.debug(f"Executing status command by getting the home page")
            self._rate_limit()  # Apply rate limiting
            response = self.session.get(f"{self.config.base_url}/go/home")

            if response.ok:
                self.logger.debug(f"Successfully got the home page")
                return True
            else:
                self.logger.warning(f"Failed to get the home page: {response.status_code}")

                # Try the original approach as a fallback
                status_command_url = f"{self.config.base_url}/applicationservice/domoweb/panel/commands/status"
                status_command_url += "?isBusy=true&checkCompletion=true"

                self.logger.debug(f"Trying fallback status command with URL: {status_command_url}")
                self._rate_limit()  # Apply rate limiting
                response = self.session.put(status_command_url, json={"key": "", "value": ""})

                if response.ok:
                    self.logger.debug(f"Fallback status command executed successfully")
                    return True
                else:
                    self.logger.warning(f"Fallback status command failed: {response.status_code}")

            return False
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Status command request exception: {str(e)}")
            return False

    def get_status(self) -> Optional[ArmStatus]:
        """Get the current arm status of the system."""
        try:
            # First, ensure we're logged in
            self._ensure_logged_in()

            # Execute the status command to get the current status
            self.logger.debug(f"Executing status command")
            self.execute_status_command()

            # Based on the Playwright analyzer, we need to look for status indicators in specific elements
            # Since we're using requests and not a browser, we'll look for these elements in the HTML

            # Try to get the status from the panel status endpoint first
            self.logger.debug(f"Getting status from panel status endpoint")
            status_url = f"{self.config.base_url}/applicationservice/domoweb/panel/status"

            # Add homeSessionId as a query parameter if we have it
            home_session_id = self.session.headers.get("x-session-token")
            if home_session_id:
                status_url += f"?homeSessionId={home_session_id}"

            self._rate_limit()  # Apply rate limiting
            response = self.session.get(status_url)

            if response.ok:
                try:
                    # Try to parse the response as JSON
                    status_data = response.json()
                    self.logger.debug(f"Status response: {status_data}")

                    # Check if the response contains status information
                    if "status" in status_data:
                        status_value = status_data["status"].lower()
                        self.logger.debug(f"Found status value: {status_value}")

                        if "disarm" in status_value:
                            return ArmStatus.DISARMED
                        elif "partial" in status_value:
                            return ArmStatus.PARTIAL_ARM
                        elif "total" in status_value or "arm" in status_value:
                            return ArmStatus.TOTAL_ARM

                    # Check if the response contains a homeSessionId
                    if "homeSessionId" in status_data:
                        home_session_id = status_data["homeSessionId"]
                        self.logger.debug(f"Found homeSessionId in status response: {home_session_id}")
                        # Add the homeSessionId to the session headers
                        self.session.headers.update({"x-session-token": home_session_id})
                except ValueError:
                    self.logger.warning(f"Failed to parse status response as JSON")

            # If we couldn't get the status from the panel status endpoint,
            # try to get it from the home page
            self.logger.debug(f"Getting status from home page")
            self._rate_limit()  # Apply rate limiting
            response = self.session.get(f"{self.config.base_url}/go/home")

            if response.ok:
                # Try to extract homeSessionId from the page
                self._extract_home_session_id(response.text)

                # Check if we got a session expiration page
                html = response.text.lower()
                if "sessionexpired" in html:
                    self.logger.warning(f"Session expired, trying to log in again")
                    # Session expired, try to log in again
                    if self.login():
                        # Try to get the status again
                        return self.get_status()
                    else:
                        self.logger.error(f"Failed to log in again")
                        return None

                # Look for status indicators in the HTML
                self.logger.debug(f"HTML length: {len(html)}")

                # Look for specific status elements based on the Playwright analyzer
                status_elements = ["div class=\"statustext\"", "div class=\"panelstatus\"", "div class=\"securitystatus\""]
                for element in status_elements:
                    if element in html:
                        self.logger.debug(f"Found status element: {element}")
                        # Try to extract the text content of this element
                        start_index = html.find(element)
                        if start_index > 0:
                            # Find the closing tag
                            end_index = html.find("</div>", start_index)
                            if end_index > start_index:
                                # Extract the text between the opening and closing tags
                                element_content = html[start_index:end_index]
                                self.logger.debug(f"Status element content: {element_content}")

                                # Check for status indicators in the element content
                                if "disarm" in element_content:
                                    self.logger.info(f"Found 'disarm' in status element")
                                    return ArmStatus.DISARMED
                                elif "partial" in element_content:
                                    self.logger.info(f"Found 'partial' in status element")
                                    return ArmStatus.PARTIAL_ARM
                                elif "total" in element_content or "arm" in element_content:
                                    self.logger.info(f"Found 'total/arm' in status element")
                                    return ArmStatus.TOTAL_ARM

                # If we couldn't find status in specific elements, look for general indicators
                if "disarmed" in html:
                    self.logger.info(f"Found 'disarmed' in HTML")
                    return ArmStatus.DISARMED
                elif "partial armed" in html or "partially armed" in html:
                    self.logger.info(f"Found 'partial armed' in HTML")
                    return ArmStatus.PARTIAL_ARM
                elif "total armed" in html or "totally armed" in html or "armed" in html:
                    self.logger.info(f"Found 'total armed' in HTML")
                    return ArmStatus.TOTAL_ARM

                # Try to find status information in the HTML
                # Look for any status-related text
                for status_text in ["status", "arm", "armed", "disarm", "panel"]:
                    if status_text in html:
                        self.logger.debug(f"Found '{status_text}' in HTML")
                        # Try to extract the context around this text
                        status_index = html.find(status_text)
                        if status_index > 0:
                            # Extract a chunk of text around the status text
                            context = html[max(0, status_index - 50):min(len(html), status_index + 50)]
                            self.logger.debug(f"'{status_text}' context: {context}")

                self.logger.warning(f"Could not determine status from HTML")
            else:
                self.logger.warning(f"Failed to get home page: {response.status_code}")

                # Check if we need to log in again
                if response.status_code == 401 or response.status_code == 403:
                    self.logger.warning(f"Unauthorized, trying to log in again")
                    if self.login():
                        # Try to get the status again
                        return self.get_status()
                    else:
                        self.logger.error(f"Failed to log in again")
                        return None

            return None
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Status request exception: {str(e)}")
            return None

    def set_status(self, command: SecurityCommand) -> bool:
        """Set the arm status of the system."""
        self._ensure_logged_in()

        try:
            # Map the command to the correct endpoint based on the Playwright analyzer findings
            if command == SecurityCommand.DISARM:
                url = f"{self.config.base_url}/applicationservice/domoweb/panel/commands/disarm"
                data = {"key": "disarmCode", "value": ""}
                button_class = "disarmButton"
            elif command == SecurityCommand.PARTIAL_ARM:
                url = f"{self.config.base_url}/applicationservice/domoweb/panel/commands/partialarm"
                data = {"key": "", "value": ""}
                button_class = "partialArmButton"
            elif command == SecurityCommand.TOTAL_ARM:
                url = f"{self.config.base_url}/applicationservice/domoweb/panel/commands/arm"
                data = {"key": "", "value": ""}
                button_class = "totalArmButton"
            else:
                self.logger.error(f"Unknown command: {command}")
                return False

            # Add query parameters
            url += "?isBusy=true&checkCompletion=true"

            # Add homeSessionId as a query parameter if we have it
            home_session_id = self.session.headers.get("x-session-token")
            if home_session_id:
                url += f"&homeSessionId={home_session_id}"

            self.logger.debug(f"Setting status with URL: {url}")
            self._rate_limit()  # Apply rate limiting

            # Add homeSessionId to the JSON data if we have it
            if home_session_id and "key" in data:
                data["homeSessionId"] = home_session_id

            response = self.session.put(url, json=data)
            self.logger.debug(f"Set status response: {response.status_code}")

            if response.ok:
                self.logger.info(f"Successfully sent command, waiting for status to update")
                # Wait a bit for the status to update
                time.sleep(2)

                # Get the updated status
                status = self.get_status()
                self.logger.info(f"New status after command: {status}")

                return True
            else:
                self.logger.warning(f"Failed to send command, status code: {response.status_code}")

                # If the PUT request failed, try to navigate to the home page and look for the button
                self.logger.debug(f"Trying alternative approach by getting the home page")
                self._rate_limit()  # Apply rate limiting
                response = self.session.get(f"{self.config.base_url}/go/home")

                if response.ok:
                    self.logger.debug(f"Successfully got the home page, looking for {button_class}")
                    html = response.text.lower()

                    # Try to extract homeSessionId from the page
                    self._extract_home_session_id(response.text)

                    # Check if the button exists in the HTML
                    if f"div class=\"{button_class.lower()}\"" in html:
                        self.logger.warning(f"Found {button_class} in HTML, but can't click it with requests")
                        self.logger.warning(f"Consider using the Playwright analyzer for this operation")

                return False

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Set status request exception: {str(e)}")
            return False

    def disarm(self) -> bool:
        """Disarm the system."""
        return self.set_status(SecurityCommand.DISARM)

    def partial_arm(self) -> bool:
        """Partially arm the system."""
        return self.set_status(SecurityCommand.PARTIAL_ARM)

    def total_arm(self) -> bool:
        """Totally arm the system."""
        return self.set_status(SecurityCommand.TOTAL_ARM)

    def close(self):
        """Close the session."""
        self.session.close()

# Example usage
def main():
    # Set up basic logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger("evosec_example")

    # Create configuration
    config = SecurityConfig(
        username="your_username",
        password="your_password"
    )

    # Initialize the security system
    system = SecuritySystem(config)

    try:
        # Get current status
        status = system.get_status()
        logger.info(f"Current status: {status}")

        # Set to total arm
        if system.total_arm():
            logger.info("Successfully set to total arm")

        # Wait a bit and check status
        status = system.get_status()
        logger.info(f"New status: {status}")

        # Set to disarm
        if system.disarm():
            logger.info("Successfully disarmed")

    finally:
        # Always close the session
        system.close()

if __name__ == "__main__":
    main()
