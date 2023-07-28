# Import necessary libraries
from flask import Blueprint, render_template, request, url_for, current_app as app, flash, redirect, session
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message, Mail

# Make Users Blueprint
users_bp = Blueprint('users', __name__)

# Route to Handle User Registration
@users_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        db = app.config['db']
        cursor = db.cursor()

        full_name = request.form['full_name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']

        # Check if user already exists
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash('User already exists. Please log in.')
        else:
            # Generate email verification link
            serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
            token = serializer.dumps(email, salt='email-verification')
            verification_link = url_for(
                'users.verify_email', token=token, _external=True)

            # Send verification email
            send_email_verification(email, verification_link)

            # Insert user details into the database
            cursor.execute(
                'INSERT INTO users (full_name, email, phone, password) VALUES (%s, %s, %s, %s)',
                (full_name, email, phone, password)
            )

            campaign_table_name = email.replace('@', '_at_').replace('.', '_dot_') + '_campaigns'

            cursor.execute(
                f'create table {campaign_table_name} (id int auto_increment primary key, campaign_name varchar(100) not null, steps int not null, active_step varchar(100) not null, prospects int not null, finished int not null, status varchar(50) not null)'
            )

            mail_accounts_table_name = email.replace('@', '_at_').replace('.', '_dot_') + "_mail_accounts"

            cursor.execute(
                f'create table {mail_accounts_table_name} (id int auto_increment primary key, email varchar(100) not null, token_data JSON)'
            )

            db.commit()

            flash(
                f'User registered successfully! A verification link has been sent to {email}. Please verify before login.')

            return redirect(url_for('users.login'))

    return render_template('users/register.html')

# Route to Handle User Verification
@users_bp.route('/verify-email/<token>')
def verify_email(token):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token, salt='email-verification', max_age=86400)
        # Mark the user as verified in the database
        db = app.config['db']
        cursor = db.cursor()
        cursor.execute(
            'UPDATE users SET is_verified = true WHERE email = %s', (email,))
        db.commit()
        flash('Verification Successful! Login')
        return render_template('users/login.html')
    except:
        return 'Invalid or expired token.'


def send_email_verification(email, verification_link):
    mail = Mail(app)

    msg = Message(
        'Email Verification',
        recipients=[email],
        html=f'<p>Click the following link to verify your email:</p><p><a href="{verification_link}">{verification_link}</a></p>'
    )
    mail.send(msg)

# Route to Handle User Login
@users_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        db = app.config['db']
        cursor = db.cursor()

        email = request.form['email']
        password = request.form['password']
        cursor.execute(
            'SELECT * FROM users WHERE email = %s AND password = %s', (email, password))
        user = cursor.fetchone()

        if user and password == user[4]:
            print(user[5])
            if user[5] == 0:
                flash('You have not verified your Email yet. Kindly verify then login again.')
            else:
                # Store the email in the session
                session['email'] = email
                session['full_name'] = user[1]
                session['logged_in'] = True
                session['user_id'] = user[0]
                return redirect(url_for('dashboard.dashboard'))
        else:
            flash('Invalid Credentials')
            return redirect(url_for('users.login'))

    return render_template('users/login.html')


@users_bp.route('/forgot', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        db = app.config['db']
        cursor = db.cursor()
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        user = cursor.fetchone()

        if user:
            # Generate password reset link
            serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
            token = serializer.dumps(email, salt='password-reset')
            reset_link = url_for('users.reset_password',
                                 token=token, _external=True)

            # Send password reset email
            send_password_reset_email(email, reset_link)

            flash('Password reset link sent to your email address.')
            return redirect(url_for('users.login'))
        else:
            flash('No user found with the provided email address.')
            return redirect(url_for('users.forgot_password'))

    return render_template('users/forgot.html')


@users_bp.route('/reset/<token>', methods=['GET', 'POST'])
def reset_password(token):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

    try:
        email = serializer.loads(token, salt='password-reset', max_age=86400)
    except:
        flash('Invalid or expired password reset link.')
        return redirect(url_for('users.login'))

    if request.method == 'POST':
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        if new_password == confirm_password:
            db = app.config['db']
            cursor = db.cursor()
            cursor.execute(
                'UPDATE users SET password = %s WHERE email = %s', (new_password, email))
            db.commit()

            flash('Password reset successfully!')
            return redirect(url_for('users.login'))
        else:
            flash('Passwords do not match.')

    return render_template('users/reset.html', token=token)


def send_password_reset_email(email, reset_link):
    mail = Mail(app)

    msg = Message(
        'Password Reset',
        recipients=[email],
        html=f'<p>Click the following link to reset your password:</p><p><a href="{reset_link}">{reset_link}</a></p>'
    )
    mail.send(msg)

@users_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('users.login'))