# Import Necessary Files
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Flask, redirect, render_template, session, url_for, request
import json
import smtplib
import random
import datetime
import time
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import requests
import credentials
import msal
import mysql.connector
from routes.users import users_bp
from routes.dashboard import dashboard_bp
from dotenv import load_dotenv


# Load environment variables and configuration
load_dotenv()
secret_key = os.environ.get("SECRET_KEY")
db_password = os.environ.get("DB_PASSWORD")
mail_username_to_verify = os.environ.get("MAIL_USERNAME_TO_VERIFY")
mail_password_to_verify = os.environ.get("MAIL_PASSWORD_TO_VERIFY")


# Initialize Flask App
app = Flask(__name__, static_url_path="/static")
app.secret_key = secret_key
app.config["SECRET_KEY"] = app.secret_key
app.config["SESSION_TYPE"] = "filesystem"


# Database Configuration
db = mysql.connector.connect(
    host="localhost", user="root", password=db_password, database="mailer"
)
app.config["db"] = db


# Flask-Mail Configuration
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = mail_username_to_verify
app.config["MAIL_PASSWORD"] = mail_password_to_verify
app.config["MAIL_DEFAULT_SENDER"] = mail_username_to_verify


# Register blueprints
app.register_blueprint(users_bp, url_prefix="/users")
app.register_blueprint(dashboard_bp, url_prefix="/dashboard")


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/gmail.readonly",
]

SMTP_SERVER = ["smtp.gmail.com", "smtp.office365.com"]
SMTP_PORT = 587
SENDER_NAME = ["Deepak Kumar", "Dave Thomas"]
SMTP_USERNAME = ["deepak.kumar@2020technologies.in", "dave.t@vidorrallc.com"]
SMTP_PASSWORD = ["fkeqdljfuyskhpgm", "20CoolD@@p20"]
SENDER_EMAIL = ["deepak.kumar@2020technologies.in", "dave.t@vidorrallc.com"]

# Define your app's credentials and settings
client_id = credentials.app_id
client_secret = credentials.client_secret
tenant_id = credentials.tenant_id
# Replace with your desired redirect URI
redirect_uri = "http://localhost:8178/callback"
scopes = ["https://graph.microsoft.com/Mail.Read"]


app_instance = msal.ConfidentialClientApplication(
    client_id=client_id,
    client_credential=client_secret,
    authority=f"https://login.microsoftonline.com/{tenant_id}",
)


# Function to store the access token in a file
def store_access_token(access_token):
    token_data = {"access_token": access_token}
    with open("access_token.json", "w") as file:
        json.dump(token_data, file)


# Function to load the access token from the file
def load_access_token():
    try:
        with open("access_token.json", "r") as file:
            token_data = json.load(file)
            return token_data["access_token"]
    except FileNotFoundError:
        return None


# Generate the authorization URL for the one-time consent flow
auth_url = app_instance.get_authorization_request_url(
    scopes=scopes, redirect_uri=redirect_uri
)


with open("data.json", "r") as f:
    mail_data = json.load(f)


# sheets_credentials = None
# if os.path.exists('sheets_token.json'):
#     sheets_credentials = Credentials.from_authorized_user_file(
#         'sheets_token.json', SCOPES)

# if not sheets_credentials or not sheets_credentials.valid:
#     if sheets_credentials and sheets_credentials.expired and sheets_credentials.refresh_token:
#         sheets_credentials.refresh(Request())
#     else:
#         flow = InstalledAppFlow.from_client_secrets_file(
#             '../secrets.json', SCOPES)
#         sheets_credentials = flow.run_local_server(port=8178, scopes=SCOPES)
#     with open('sheets_token.json', 'w') as token:
#         token.write(sheets_credentials.to_json())

# try:
#     sheets_service = build('sheets', 'v4', credentials=sheets_credentials)
#     sheets = sheets_service.spreadsheets()
#     sheet1 = sheets.get(spreadsheetId=SPREADSHEET_ID).execute()
#     sheet2 = sheets.get(spreadsheetId=SPREADSHEET_ID2).execute()
#     # Perform operations on Google Sheets
#     # ...
# except HttpError as error:
#     print(error)

# gmail_credentials = None
# if os.path.exists('gmail_token.json'):
#     gmail_credentials = Credentials.from_authorized_user_file(
#         'gmail_token.json', SCOPES)

# if not gmail_credentials or not gmail_credentials.valid:
#     if gmail_credentials and gmail_credentials.expired and gmail_credentials.refresh_token:
#         gmail_credentials.refresh(Request())
#     else:
#         flow = InstalledAppFlow.from_client_secrets_file(
#             '../secrets.json', SCOPES)
#         gmail_credentials = flow.run_local_server(port=8178, scopes=SCOPES)
#     with open('gmail_token.json', 'w') as token:
#         token.write(gmail_credentials.to_json())

# gmail_service = build('gmail', 'v1', credentials=gmail_credentials)


def send_email(
    smtp_server,
    smtp_port,
    sender_name,
    sender_email,
    password,
    recipient,
    subject,
    message,
    user=None,
):
    msg = MIMEMultipart()
    msg["From"] = "{} <{}>".format(sender_name, sender_email)
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.attach(MIMEText(message, "html"))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, password)
        server.send_message(msg)
        server.quit()
        print(f"Email sent to {recipient}")

        if user == "deepak":
            messages = (
                gmail_service.users()
                .messages()
                .list(userId="me", q=f"to:{recipient}", maxResults=1)
                .execute()
            )
            message_id_gmail = messages.get("messages", [])[0].get("id")
            return message_id_gmail

        elif user == "deepanshu":
            print("code reached here")

            graph_endpoint = "https://graph.microsoft.com/v1.0/me/mailFolders/sentItems/messages?$select=internetMessageId&$top=1"
            access_token = load_access_token()
            headers = {
                "Authorization": "Bearer " + access_token,
                "Content-Type": "application/json",
            }
            response = requests.get(graph_endpoint, headers=headers)
            print(access_token)
            print(response.status_code)

            # Process the API response
            if response.status_code == 200:
                conversationID = response.json()["value"]
                print(conversationID)
                message_id_outlook = conversationID[0]["internetMessageId"]
                print(message_id_outlook)
            return message_id_outlook

    except Exception as e:
        print(f"Failed to send email to {recipient}. Error: {str(e)}")


def reply_email(
    smtp_server,
    smtp_port,
    sender_name,
    sender_email,
    password,
    recipient,
    subject,
    message,
    message_id,
):
    msg = MIMEMultipart()
    msg["From"] = "{} <{}>".format(sender_name, sender_email)
    msg["To"] = recipient
    msg.attach(MIMEText(message, "html"))
    msg["Subject"] = subject
    msg["In-Reply-To"] = message_id
    msg["References"] = message_id

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, password)
        server.send_message(msg)
        server.quit()
        print(f"Email sent to {recipient}")

    except Exception as e:
        print(f"Failed to send email to {recipient}. Error: {str(e)}")


@app.route("/")
def home():
    access_token = load_access_token()
    session["access_token"] = access_token
    if access_token:
        return render_template("index.html")
    else:
        # Token does not exist, initiate the consent flow
        return redirect(auth_url)


@app.route("/callback")
def callback():
    authorization_code = request.args.get("code")

    # Acquire an access token for the target user using the authorization code
    token_response = app_instance.acquire_token_by_authorization_code(
        authorization_code, scopes=scopes, redirect_uri=redirect_uri
    )

    access_token = token_response["access_token"]
    store_access_token(access_token)

    return redirect("/")


@app.route("/send-initial", methods=["POST"])
def send_initial():
    user = request.form.get("user")
    if user == "deepak":
        last_row = sheet1["sheets"][0]["properties"]["gridProperties"]["rowCount"]
        last_column = sheet1["sheets"][0]["properties"]["gridProperties"]["columnCount"]
        data_range = f"Sheet1!A2:{chr(64 + last_column)}{last_row}"
        result = (
            sheets.values()
            .get(spreadsheetId=SPREADSHEET_ID, range=data_range)
            .execute()
        )
    elif user == "deepanshu":
        last_row = sheet2["sheets"][0]["properties"]["gridProperties"]["rowCount"]
        last_column = sheet2["sheets"][0]["properties"]["gridProperties"]["columnCount"]
        data_range = f"Sheet1!A2:{chr(64 + last_column)}{last_row}"
        result = (
            sheets.values()
            .get(spreadsheetId=SPREADSHEET_ID2, range=data_range)
            .execute()
        )

    # Retrieve the values from the specified range
    values = result.get("values", [])
    filtered_values = [data for data in values if len(data) < 5 or not data[4]]
    first_row_index = values.index(filtered_values[0]) + 2
    for index, data in enumerate(filtered_values, start=first_row_index):
        recipient = data[2]
        name = data[0]
        company = data[3]
        random_sub = random.choice(mail_data["subjects"])
        SUBJECT = random_sub.format(name=name)

        if user == "deepak":
            MESSAGE = mail_data["followups"][0].format(name=name, company=company)
            # Send email from Deepak Mail Account
            message_id = send_email(
                SMTP_SERVER[0],
                SMTP_PORT,
                SENDER_NAME[0],
                SMTP_USERNAME[0],
                SMTP_PASSWORD[0],
                recipient,
                SUBJECT,
                MESSAGE,
                user,
            )
            update_range = f"Sheet1!E{index}:I{index}"
            update_values = [
                [
                    "Done",
                    f"Date: {datetime.datetime.today().strftime('%d-%m-%y')}\nTime: {datetime.datetime.now().strftime('%H:%M')}",
                    "Sent",
                    f"{message_id}",
                    f"{SUBJECT}",
                ]
            ]
            update_body = {"values": update_values}
            sheets.values().update(
                spreadsheetId=SPREADSHEET_ID,
                range=update_range,
                valueInputOption="RAW",
                body=update_body,
            ).execute()
        elif user == "deepanshu":
            MESSAGE = mail_data["followups"][1].format(name=name, company=company)
            # Send email from Deepanshu Mail Account
            message_id = send_email(
                SMTP_SERVER[1],
                SMTP_PORT,
                SENDER_NAME[1],
                SMTP_USERNAME[1],
                SMTP_PASSWORD[1],
                recipient,
                SUBJECT,
                MESSAGE,
                user,
            )
            update_range = f"Sheet1!E{index}:I{index}"
            update_values = [
                [
                    "Done",
                    f"Date: {datetime.datetime.today().strftime('%d-%m-%y')}\nTime: {datetime.datetime.now().strftime('%H:%M')}",
                    "Sent",
                    f"{message_id}",
                    f"{SUBJECT}",
                ]
            ]
            update_body = {"values": update_values}
            sheets.values().update(
                spreadsheetId=SPREADSHEET_ID2,
                range=update_range,
                valueInputOption="RAW",
                body=update_body,
            ).execute()
        else:
            print("Invalid User")

        if index < first_row_index + len(filtered_values) - 1:
            time.sleep(90)

    return redirect(url_for("home"))


@app.route("/send-followup", methods=["POST"])
def send_followup():
    user = request.form.get("user")
    if user == "deepak":
        last_row = sheet1["sheets"][0]["properties"]["gridProperties"]["rowCount"]
        last_column = sheet1["sheets"][0]["properties"]["gridProperties"]["columnCount"]
        data_range = f"Sheet1!A2:{chr(64 + last_column)}{last_row}"
        result = (
            sheets.values()
            .get(spreadsheetId=SPREADSHEET_ID, range=data_range)
            .execute()
        )
    elif user == "deepanshu":
        last_row = sheet2["sheets"][0]["properties"]["gridProperties"]["rowCount"]
        last_column = sheet2["sheets"][0]["properties"]["gridProperties"]["columnCount"]
        data_range = f"Sheet1!A2:{chr(64 + last_column)}{last_row}"
        result = (
            sheets.values()
            .get(spreadsheetId=SPREADSHEET_ID2, range=data_range)
            .execute()
        )

    # Retrieve the values from the specified range
    values = result.get("values", [])
    filtered_values = [
        data
        for data in values
        if len(data) >= 5
        and data[4].strip() == "Done"
        and (len(data) < 13 or not data[12].strip())
    ]
    first_row_index = values.index(filtered_values[0]) + 2

    for index, data in enumerate(filtered_values, start=first_row_index):
        original_index = values.index(data) + 2
        recipient = data[2]
        name = data[0]
        company = data[3]
        SUBJECT = "Re: " + data[8] if len(data) > 8 else ""
        message_id = data[7] if len(data) > 7 else ""
        followup_1_status = data[9] if len(data) > 9 else ""
        followup_2_status = data[10] if len(data) > 10 else ""
        followup_3_status = data[11] if len(data) > 11 else ""

        if user == "deepak":
            if (
                followup_1_status != "Sent"
                or followup_2_status != "Sent"
                or followup_3_status != "Sent"
            ):
                # Send email from Deepak Mail Account
                if followup_1_status != "Sent":
                    MESSAGE = mail_data["followups"][2].format(
                        name=name, company=company
                    )
                    reply_email(
                        SMTP_SERVER[0],
                        SMTP_PORT,
                        SENDER_NAME[0],
                        SMTP_USERNAME[0],
                        SMTP_PASSWORD[0],
                        recipient,
                        SUBJECT,
                        MESSAGE,
                        message_id,
                    )
                    sheets.values().update(
                        spreadsheetId=SPREADSHEET_ID,
                        range=f"Sheet1!J{original_index}",
                        valueInputOption="RAW",
                        body={"values": [["Sent"]]},
                    ).execute()

                elif followup_2_status != "Sent":
                    MESSAGE = mail_data["followups"][4].format(
                        name=name, company=company
                    )
                    reply_email(
                        SMTP_SERVER[0],
                        SMTP_PORT,
                        SENDER_NAME[0],
                        SMTP_USERNAME[0],
                        SMTP_PASSWORD[0],
                        recipient,
                        SUBJECT,
                        MESSAGE,
                        message_id,
                    )
                    sheets.values().update(
                        spreadsheetId=SPREADSHEET_ID,
                        range=f"Sheet1!K{original_index}",
                        valueInputOption="RAW",
                        body={"values": [["Sent"]]},
                    ).execute()

                elif followup_3_status != "Sent":
                    MESSAGE = mail_data["followups"][6].format(
                        name=name, company=company
                    )
                    reply_email(
                        SMTP_SERVER[0],
                        SMTP_PORT,
                        SENDER_NAME[0],
                        SMTP_USERNAME[0],
                        SMTP_PASSWORD[0],
                        recipient,
                        SUBJECT,
                        MESSAGE,
                        message_id,
                    )
                    sheets.values().update(
                        spreadsheetId=SPREADSHEET_ID,
                        range=f"Sheet1!L{original_index}",
                        valueInputOption="RAW",
                        body={"values": [["Sent"]]},
                    ).execute()

        elif user == "deepanshu":
            if followup_1_status != "Sent":
                MESSAGE = mail_data["followups"][3].format(name=name, company=company)
                reply_email(
                    SMTP_SERVER[1],
                    SMTP_PORT,
                    SENDER_NAME[1],
                    SMTP_USERNAME[1],
                    SMTP_PASSWORD[1],
                    recipient,
                    SUBJECT,
                    MESSAGE,
                    message_id,
                )
                sheets.values().update(
                    spreadsheetId=SPREADSHEET_ID2,
                    range=f"Sheet1!J{original_index}",
                    valueInputOption="RAW",
                    body={"values": [["Sent"]]},
                ).execute()
            elif followup_2_status != "Sent":
                MESSAGE = mail_data["followups"][5].format(name=name, company=company)
                reply_email(
                    SMTP_SERVER[1],
                    SMTP_PORT,
                    SENDER_NAME[1],
                    SMTP_USERNAME[1],
                    SMTP_PASSWORD[1],
                    recipient,
                    SUBJECT,
                    MESSAGE,
                    message_id,
                )
                sheets.values().update(
                    spreadsheetId=SPREADSHEET_ID2,
                    range=f"Sheet1!K{original_index}",
                    valueInputOption="RAW",
                    body={"values": [["Sent"]]},
                ).execute()

            elif followup_3_status != "Sent":
                MESSAGE = mail_data["followups"][7].format(name=name, company=company)
                reply_email(
                    SMTP_SERVER[1],
                    SMTP_PORT,
                    SENDER_NAME[1],
                    SMTP_USERNAME[1],
                    SMTP_PASSWORD[1],
                    recipient,
                    SUBJECT,
                    MESSAGE,
                    message_id,
                )
                sheets.values().update(
                    spreadsheetId=SPREADSHEET_ID2,
                    range=f"Sheet1!L{original_index}",
                    valueInputOption="RAW",
                    body={"values": [["Sent"]]},
                ).execute()

        else:
            print("Invalid User")
        if index < first_row_index + len(filtered_values) - 1:
            time.sleep(61)

    return redirect(url_for("home"))
