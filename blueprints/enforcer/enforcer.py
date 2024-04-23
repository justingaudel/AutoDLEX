from flask import Blueprint, render_template, request, session, url_for, redirect
from db_utils import get_db_connection 
import os
from werkzeug.utils import secure_filename



db_connection = get_db_connection()
cursor = db_connection.cursor()

enforcer_bp = Blueprint("enforcer", __name__, template_folder="templates")

@enforcer_bp.route('/enforcer', methods=['GET', 'POST'])
def enforcer():
    if 'loggedin' in session:
        return redirect(url_for('camera'))
    msg = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor.execute('SELECT * FROM enforcer_accounts WHERE username=%s AND password=%s', (username, password,))
        record = cursor.fetchone()
        if record:
            session['loggedin'] = True
            session['username'] = record[1]
            return redirect(url_for('camera'))
        else:
            msg = 'Incorrect Password or Username!'
    return render_template('enforcer-login.html', msg=msg)


@enforcer_bp.route('/add_enforcer', methods=['POST', 'GET'])
def add_enforcer():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        assigned_location = request.form['assigned_location']
        confirm_password = request.form['confirm_password']
        profile_image = request.files['profile_image'] 
        
        if profile_image:  # Check if an image was uploaded
            filename = secure_filename(profile_image.filename)  # Sanitize the filename
            uploads_folder = 'static/enforcer_profiles'  # Adjust the path to your uploads folder
            filepath = os.path.join(uploads_folder, filename)
            profile_image.save(filepath) 
        
        if password != confirm_password:
            return render_template('new-enforcer.html', msg="Passwords do not match!")
        else:
            sql = "INSERT INTO enforcer_accounts (username, password, email, first_name, last_name, assigned_location, profile_image) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            val = (username, password, email, first_name, last_name, assigned_location,filename)  # Save filename instead of file object
            cursor.execute(sql, val)
            db_connection.commit()
            return redirect(url_for('enforcer.enforcer_data'))
    
    return render_template('new-enforcer.html')

@enforcer_bp.route('/enforcer_data')
def enforcer_data():
    cursor.execute("SELECT * From  enforcer_accounts")
    enforcer_data = cursor.fetchall()
    return render_template('enforcer.html',enforcer_data = enforcer_data)
