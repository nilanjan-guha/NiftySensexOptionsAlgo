





# import os
# import re
# import subprocess
# import webbrowser
# from urllib.parse import urlparse, parse_qs

# from dotenv import load_dotenv
# from kiteconnect import KiteConnect


# # =========================================================
# # CONFIG
# # =========================================================

# load_dotenv()

# API_KEY = os.getenv("KITE_API_KEY")
# API_SECRET = os.getenv("KITE_API_SECRET")

# if not API_KEY:
#     print("ERROR: KITE_API_KEY not found in .env")
#     raise SystemExit(1)

# if not API_SECRET:
#     print("ERROR: KITE_API_SECRET not found in .env")
#     raise SystemExit(1)


# # =========================================================
# # GITHUB CONFIG
# # =========================================================

# GITHUB_CLI = r"C:\Program Files\GitHub CLI\gh.exe"

# GITHUB_REPO = "nilanjan-guha/NiftySensexOptionsAlgo"

# GITHUB_SECRET_NAME = "KITE_ACCESS_TOKEN"


# # =========================================================
# # ZERODHA LOGIN
# # =========================================================

# kite = KiteConnect(
#     api_key=API_KEY
# )

# login_url = kite.login_url()


# print()
# print("==========================================")
# print("          ZERODHA KITE LOGIN")
# print("==========================================")
# print()

# print("Opening Zerodha login page...")
# print(login_url)

# webbrowser.open(login_url)

# print()
# print("Complete the Zerodha login in the browser.")
# print()
# print("After successful login, Zerodha will redirect")
# print("you to your configured callback URL.")
# print()
# print("You can paste EITHER:")
# print()
# print("1. The COMPLETE callback URL")
# print("   OR")
# print()
# print("2. ONLY the request_token value")
# print()
# print("Example callback:")
# print()
# print("https://nifty-zerodha-login.nilanjanguha8.workers.dev/")
# print("callback?type=login&status=success&request_token=XXXXX&action=login")
# print()
# print("Paste the callback URL or request_token below.")
# print()


# # =========================================================
# # GET REQUEST TOKEN
# # =========================================================

# user_input = input(
#     "Paste callback URL / request_token: "
# ).strip()


# if not user_input:

#     print()
#     print("ERROR: Nothing was entered.")
#     raise SystemExit(1)


# def extract_request_token(value):
#     """
#     Accept either:
#       - Full callback URL
#       - request_token value directly
#     """

#     value = value.strip()

#     # -----------------------------------------------------
#     # Case 1: Full URL
#     # -----------------------------------------------------

#     if value.startswith("http://") or value.startswith("https://"):

#         try:

#             parsed = urlparse(value)

#             query = parse_qs(
#                 parsed.query
#             )

#             token = query.get(
#                 "request_token",
#                 [None]
#             )[0]

#             if token:
#                 return token.strip()

#         except Exception:
#             pass

#     # -----------------------------------------------------
#     # Case 2: User pasted something containing
#     # request_token=...
#     # -----------------------------------------------------

#     match = re.search(
#         r"request_token=([^&\s]+)",
#         value
#     )

#     if match:

#         return match.group(1).strip()


#     # -----------------------------------------------------
#     # Case 3: Assume the entire input is the token
#     # -----------------------------------------------------

#     return value


# request_token = extract_request_token(
#     user_input
# )


# if not request_token:

#     print()
#     print("ERROR: Could not extract request_token.")
#     raise SystemExit(1)


# print()
# print("Request token received successfully.")


# # =========================================================
# # GENERATE ACCESS TOKEN
# # =========================================================

# print()
# print("Generating Zerodha access token...")


# try:

#     session_data = kite.generate_session(
#         request_token,
#         api_secret=API_SECRET
#     )

#     access_token = session_data.get(
#         "access_token"
#     )

# except Exception as exc:

#     print()
#     print("ERROR generating access token:")
#     print(type(exc).__name__)
#     print(str(exc))
#     print()
#     print("The request_token may be expired or already used.")
#     print("Perform a fresh Zerodha login and try again.")

#     raise SystemExit(1)


# if not access_token:

#     print()
#     print(
#         "ERROR: Zerodha returned an empty access token."
#     )

#     raise SystemExit(1)


# print()
# print("Zerodha access token generated successfully.")


# # =========================================================
# # SAVE ACCESS TOKEN LOCALLY
# # =========================================================

# script_dir = os.path.dirname(
#     os.path.abspath(__file__)
# )

# token_file = os.path.join(
#     script_dir,
#     "access_token.txt"
# )

# try:

#     with open(
#         token_file,
#         "w",
#         encoding="utf-8"
#     ) as file:

#         file.write(access_token)

# except Exception as exc:

#     print()
#     print("ERROR saving access_token.txt:")
#     print(type(exc).__name__)
#     print(str(exc))

#     raise SystemExit(1)


# print()
# print("Local access token saved successfully.")


# # =========================================================
# # UPDATE GITHUB SECRET
# # =========================================================

# print()
# print(
#     "Updating GitHub KITE_ACCESS_TOKEN secret..."
# )


# if not os.path.exists(GITHUB_CLI):

#     print()
#     print(
#         "ERROR: GitHub CLI was not found at:"
#     )

#     print(GITHUB_CLI)

#     raise SystemExit(1)


# try:

#     result = subprocess.run(
#         [
#             GITHUB_CLI,
#             "secret",
#             "set",
#             GITHUB_SECRET_NAME,
#             "--repo",
#             GITHUB_REPO,
#             "--body",
#             access_token
#         ],
#         capture_output=True,
#         text=True,
#         check=False
#     )

# except Exception as exc:

#     print()
#     print("ERROR running GitHub CLI:")
#     print(type(exc).__name__)
#     print(str(exc))

#     raise SystemExit(1)


# # =========================================================
# # CHECK GITHUB UPDATE
# # =========================================================

# if result.returncode != 0:

#     print()
#     print(
#         "ERROR: Could not update GitHub secret."
#     )

#     if result.stderr:

#         print()
#         print(result.stderr.strip())

#     raise SystemExit(1)


# # =========================================================
# # FINAL SUCCESS
# # =========================================================

# print()
# print("==========================================")
# print("             LOGIN SUCCESS")
# print("==========================================")
# print()

# print("Zerodha access token generated.")
# print("Local access_token.txt updated.")
# print("GitHub KITE_ACCESS_TOKEN updated.")

# print()
# print("Your GitHub trading bot is ready")
# print("to use the new access token.")
# print()







import webbrowser

from dotenv import load_dotenv
from kiteconnect import KiteConnect


# =========================================================
# CONFIG
# =========================================================

load_dotenv()

import os

API_KEY = os.getenv("KITE_API_KEY")

if not API_KEY:
    print("ERROR: KITE_API_KEY not found in .env")
    raise SystemExit(1)


# =========================================================
# CLOUDFLARE LOGIN
# =========================================================

CLOUDFLARE_LOGIN_URL = (
    "https://nifty-zerodha-login.nilanjanguha8.workers.dev/"
)


print()
print("==========================================")
print("       ZERODHA KITE LOGIN")
print("==========================================")
print()

print("Opening Zerodha login...")
print()

webbrowser.open(CLOUDFLARE_LOGIN_URL)

print("Complete the Zerodha login in the browser.")
print()
print("After successful login, Cloudflare will:")
print()
print("1. Receive the request_token")
print("2. Generate the Zerodha access token")
print("3. Save the access token to Cloudflare KV")
print("4. Trigger the GitHub trading workflow")
print()
print("You do NOT need to paste the request_token")
print("into this terminal.")
print()
print("==========================================")
print("       LOGIN FLOW STARTED")
print("==========================================")
print()