import os
from dotenv import load_dotenv
import requests
from flask import Flask, request, redirect
import webbrowser
import logging

#Configure logging
logging.basicConfig(level=logging.INFO,
format="%(asctime)s - %(levelname)s - %(message)s",
handlers= [
    logging.FileHandler("app.log"), #Log to the file
    logging.StreamHandler() #Log to the console
])

logger = logging.getLogger(__name__)

logger.debug("This is a debug message.")
logger.info("This is an info message.")
logger.warning("This is a warning.")
logger.error("This is an error.")
logger.critical("This is critical.")

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
SCOPES = os.getenv("SCOPES")
AUTH_URL = os.getenv("AUTH_URL")
TOKEN_URL = os.getenv("TOKEN_URL")


# https://webexapis.com/v1/authorize?client_id=C237ef2c88c77190cad80ce194cfba1d8618e5476b0ce048aee449d78ad5fedc8&response_type=code&redirect_uri=http://127.0.0.1&scope=spark-admin:telephony_config_read spark-admin:telephony_config_write&state=123499999


app=Flask(__name__)
auth_code = None

@app.route("/")
def home():
    auth_url = (
        f"{AUTH_URL}?client_id={CLIENT_ID}&response_type=code"
        f"&redirect_uri={REDIRECT_URI}&scope={SCOPES}&state=1236664"
    )
    logger.info(f"Authorization URL: {auth_url}")
    return redirect(auth_url)

@app.route("/callback")
def callback():
    global auth_code
    auth_code = request.args.get("code")
    if auth_code:
        try:
            logger.info(f"Authorization code received: {auth_code}")
            logger.info("Exchangin authorization code for access token....")
            access_token = get_access_token()
            logger.info(f"Access token: {access_token}") 
            return f"Authorization code received :{auth_code}.\n Access token: {access_token}.\n You can close this window now."
        except Exception as e:
            logger.error(f"Error exchanging auth code for token: {e}")
            return f"Error exchanging auth code for token: {e}"
    logger.error("No authorization code received.")
    return "No authorization code received."

def get_access_token():
    data = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": auth_code,
        "redirect_uri": REDIRECT_URI,
    }
    response = requests.post(TOKEN_URL, data=data)
    response_data = response.json()

    if response.status_code==200 and "access_token" in response_data:
        logger.info("Access token obtained successfully.")
        return response_data["access_token"]
    else:
        logger.error(f"Failed to obtain access token. {response_data}")
        raise Exception(f"Failed to obtain access token. {response_data}")



if __name__ == "__main__":
    webbrowser.open("http://127.0.0.1:5000")
    logger.info("OAuth flow initiated. Waiting fro use authorization....")
    
    app.run(port=5000, debug=False)

