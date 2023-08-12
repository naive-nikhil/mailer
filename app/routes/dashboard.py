# Import necessary libraries
from flask import (
    Blueprint,
    render_template,
    request,
    url_for,
    current_app as app,
    flash,
    redirect,
    session,
)
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message, Mail
from functools import wraps

# Import necessary libraries
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import msal
import requests
import json
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
import smtplib
from email.mime.text import MIMEText

CLIENT_SECRETS_FILE = "../credentials.json"

SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
]


# Make Users Blueprint
dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("", methods=["GET", "POST"])
def dashboard():
    # del session["state"]
    # Connect to the database
    db = app.config["db"]
    email = session.get("email")

    # Refresh the database connection
    db.reconnect()

    # Fetch data from the campaigns table
    cursor = db.cursor()
    cursor.execute(f"SELECT * FROM mailer_campaigns WHERE email='{email}'")
    campaigns = cursor.fetchall()
    cursor.close()

    cursor = db.cursor()
    cursor.execute(f"SELECT * FROM mailer_user_mail_accounts WHERE email='{email}'")
    mail_accounts = cursor.fetchall()
    cursor.close()

    return render_template(
        "dashboard.html",
        campaigns=campaigns,
        mail_accounts=mail_accounts,
    )


@dashboard_bp.route("/gmail_oauth")
def gmail_oauth():
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES
    )
    flow.redirect_uri = url_for("dashboard.oauth2callback", _external=True)

    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
    )

    session["state"] = state

    return redirect(authorization_url)


@dashboard_bp.route("/oauth2callback")
def oauth2callback():
    db = app.config["db"]
    state = session["state"]

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, state=state
    )
    flow.redirect_uri = url_for("dashboard.oauth2callback", _external=True)

    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials

    user_info_service = googleapiclient.discovery.build(
        "oauth2", "v2", credentials=credentials
    )

    user_info = user_info_service.userinfo().get().execute()
    selected_email = user_info["email"]
    email = session.get("email")
    credentials = json.dumps(credentials_to_dict(credentials))

    cursor = db.cursor()
    cursor.execute(
        f"select * from mailer_user_mail_accounts where email = '{email}' and user_email = '{selected_email}'"
    )
    mail_accounts = cursor.fetchone()

    if mail_accounts:
        flash("Email already exists in the database.")
    else:
        cursor.execute(
            "insert into mailer_user_mail_accounts (email, user_email, email_provider, credentials_data) values (%s, %s, %s, %s)",
            (email, selected_email, "Google", credentials),
        )
        db.commit()
        flash("New mail account added successfully.")
    cursor.close()

    return redirect(url_for("dashboard.dashboard"))


def credentials_to_dict(credentials):
    return {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes,
    }


@dashboard_bp.route("/revoke")
def revoke():
    db = app.config["db"]
    email = session["email"]
    selected_email = request.args.get("email")

    cursor = db.cursor()
    cursor.execute(
        f"SELECT * FROM mailer_user_mail_accounts WHERE email = '{email}' and user_email = '{selected_email}'"
    )
    account = cursor.fetchone()

    credentials_dict = json.loads(account[3])
    credentials = google.oauth2.credentials.Credentials(**credentials_dict)

    requests.post(
        "https://oauth2.googleapis.com/revoke",
        params={"token": credentials.token},
        headers={"content-type": "application/x-www-form-urlencoded"},
    )

    cursor.execute(
        f"DELETE FROM mailer_user_mail_accounts WHERE email = '{email}' and user_email = '{selected_email}'"
    )
    db.commit()

    cursor.close()

    flash("Email deleted successfully.")

    return redirect(url_for("dashboard.dashboard"))


@dashboard_bp.route("/send_mail")
def send_mail():
    print("code reached here")
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_name = "Deepak Kumar"
    smtp_username = "deepak.kumar@2020technologies.in"
    smtp_password = "fkeqdljfuyskhpgm"
    sender_email = "deepak.kumar@2020technologies.in"
    receiver_email = "dv9818904751@gmail.com"
    subject = "Test Email"
    body = "This is a test mail sent from Python!"

    message = MIMEText(body)
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = receiver_email

    smtp = smtplib.SMTP(smtp_server, smtp_port)
    smtp.starttls()
    smtp.login(smtp_username, smtp_password)

    smtp.sendmail(sender_email, [receiver_email], message.as_string())

    smtp.quit()

    print(message)

    return "Mail Sent Successfully"


@dashboard_bp.route("/campaign")
def campaign():
    return render_template("campaign.html")


# # Your application's credentials and scopes
# client_id = "f072a500-1414-4813-ab3d-8d37015372d3"
# client_secret = "FYF8Q~oqowQgF.5zsx8U-7nxe59JHxJ5ENQ2ebWq"
# scopes = ["User.Read", "Mail.Read"]
# redirect_uri = "http://localhost:8178/dashboard/ms_test"

# Microsoft Graph API endpoints
GRAPH_API_BASE_URL = "https://graph.microsoft.com/v1.0/"
GRAPH_API_SCOPES = ["Mail.Read"]  # Add other required scopes here

# Azure AD Application settings
CLIENT_ID = "ea497f8f-843f-43a4-9a8d-7f16a5aed08b"
CLIENT_SECRET = "-Rj8Q~VPBe-.4-FeUg9~56YJcJiHHb6AdTz7kb4q"  # Use None if using Authorization Code Grant without client secret
REDIRECT_URI = "http://localhost:8178/dashboard/ms_callback"  # Must match the Redirect URI set in Azure AD


@dashboard_bp.route("/ms_test")
def ms_test():
    auth_url = f"https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": " ".join(GRAPH_API_SCOPES),
    }
    return redirect(
        auth_url + "?" + "&".join([f"{key}={value}" for key, value in params.items()])
    )


@dashboard_bp.route("/ms_callback")
def ms_callback():
    auth_code = request.args.get("code")
    token_url = f"https://login.microsoftonline.com/common/oauth2/v2.0/token"
    data = {
        "client_id": CLIENT_ID,
        "scope": " ".join(GRAPH_API_SCOPES),
        "code": auth_code,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    if CLIENT_SECRET:
        data["client_secret"] = CLIENT_SECRET

    response = requests.post(token_url, data=data)

    if response.status_code == 200:
        access_token = response.json().get("access_token")
        print(access_token)
        return "Authentication successful! You can now access your emails."
    else:
        return f"Authentication failed. Status code: {response.status_code}"
