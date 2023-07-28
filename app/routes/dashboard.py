# Import necessary libraries
from flask import Blueprint, render_template, request, url_for, current_app as app, flash, redirect, session
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message, Mail
from functools import wraps
# Import necessary libraries
import os
from flask import Blueprint, render_template, request, url_for, current_app as app, flash, redirect, session
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Make Users Blueprint
dashboard_bp = Blueprint('dashboard', __name__)


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.')
            return redirect(url_for('users.login'))
        return view(*args, **kwargs)
    return wrapped_view


@dashboard_bp.route('', methods=['GET', 'POST'])
@login_required
def dashboard():

    # Connect to the database
    db = app.config['db']

    email = session.get('email')
    full_name = session.get('full_name')

    # Refresh the database connection
    db.reconnect()

    # Fetch data from the campaigns table
    cursor = db.cursor()
    campaign_table_name = email.replace(
        '@', '_at_').replace('.', '_dot_') + '_campaigns'
    cursor.execute(f"SELECT * FROM {campaign_table_name}")
    campaigns = cursor.fetchall()
    cursor.close()

    cursor = db.cursor()
    mail_accounts_table_name = email.replace(
        '@', '_at_').replace('.', '_dot_') + "_mail_accounts"
    cursor.execute(f"SELECT * FROM {mail_accounts_table_name}")
    mail_accounts = cursor.fetchall()
    cursor.close()

    flash('Login Successful!')
    return render_template('dashboard.html', campaigns=campaigns, full_name=full_name, mail_accounts=mail_accounts)


@dashboard_bp.route('/gmail_oauth')
@login_required
def gmail_oauth():
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=request.url_root + "auth_callback",
    )
    authorization_url, state = flow.authorization_url(
        access_type="offline", include_granted_scopes="true"
    )
    # Save the 'state' in the session for use in the callback for security
    session["oauth_state"] = state
    # Redirect the user to 'authorization_url' for them to sign in and grant access
    return redirect(authorization_url)