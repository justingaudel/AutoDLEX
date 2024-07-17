from flask import Blueprint, render_template, request, session, url_for, redirect,flash
from db_utils import get_db_connection 
import os
from werkzeug.utils import secure_filename
import datetime



db_connection = get_db_connection()


enforcer_bp = Blueprint("enforcer", __name__, template_folder="templates")

@enforcer_bp.route('/enforcer', methods=['GET', 'POST'])
def enforcer():
    db_connection = get_db_connection()
    cursor = db_connection.cursor()
    if 'loggedins' in session:
        return redirect(url_for('camera'))
    msg = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor.execute('SELECT * FROM enforcer_accounts WHERE username=%s AND password=%s', (username, password,))
        record = cursor.fetchone()
        cursor.close()
        if record:
            session['loggedins'] = True
            return redirect(url_for('selection_mode'))
        else:
            msg = 'Incorrect Password or Username!'
    return render_template('enforcer-login.html', msg=msg)


@enforcer_bp.route('/add_enforcer', methods=['POST', 'GET'])
def add_enforcer():
    db_connection = get_db_connection()
    cursor = db_connection.cursor()
    cursor.execute("SELECT MAX(enforcer_id) from enforcer_accounts")
    largest_id = cursor.fetchone()[0]  # Get the latest extracted_id

    if largest_id is None:
        new_id = 1
    else:
        cursor.execute("SELECT username FROM enforcer_accounts WHERE enforcer_id = %s", (largest_id,))
        result = cursor.fetchone()[0]
        new_id = int(result.split('Enforcer')[1])
        new_id = new_id + 1

    generated_username = 'Enforcer' + str(new_id).zfill(1)
    msg = ''  # Initialize msg here
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        phone_number = request.form['phone_number']
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
        
        # Check if username already exists
        cursor.execute("SELECT * FROM enforcer_accounts WHERE username = %s", (username,))
        existing_user = cursor.fetchone()
        if existing_user:
            return render_template('new-enforcer.html', msg="Username already exists. Please choose another one.")
        
        if password != confirm_password:
            return render_template('new-enforcer.html', msg="Passwords do not match!")
        else:
            sql = "INSERT INTO enforcer_accounts (username, password, phone_number, first_name, last_name, assigned_location, profile_image) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            val = (username, password, phone_number, first_name, last_name, assigned_location, filename)  # Save filename instead of file object
            cursor.execute(sql, val)
            db_connection.commit()
            
            # Adding data to the activity logs
            current_date_time = datetime.datetime.now()
            date = current_date_time.strftime('%A, %B %d, %Y')
            time = current_date_time.strftime('%I:%M %p')
            action = f"Enforcer {first_name} {last_name} was added to the system."
            cursor.execute("INSERT INTO activity_logs (date, time, action) VALUES (%s, %s, %s)", (date, time, action))
            
            cursor.close()
            flash('Enforcer added successfully!', 'success')
            return redirect(url_for('enforcer.enforcer_data'))
        
    return render_template('new-enforcer.html',generated_username = generated_username)


@enforcer_bp.route('/enforcer_data')
def enforcer_data():
    db_connection = get_db_connection()
    cursor = db_connection.cursor()
    cursor.execute("SELECT * From  enforcer_accounts")
    enforcer_data = cursor.fetchall()
    cursor.close()
    return render_template('enforcer.html',enforcer_data = enforcer_data)



@enforcer_bp.route('/view_enforcer')
def view_enforcer():
    cursor = db_connection.cursor()
    enforcer_id = request.args.get('enforcer_id')
    query = "SELECT * FROM enforcer_accounts WHERE enforcer_id=%s"
    cursor.execute(query, (enforcer_id,))
    enforcer_data = cursor.fetchone()
    cursor.close()
    if enforcer_data:
        return render_template('Enforcers_Information.html', enforcer_data=enforcer_data)
    else:
        return "Enforcer not found", 404
    
    
@enforcer_bp.route('/edit_enforcer', methods=['POST', 'GET'])
def edit_enforcer():
    db_connection = get_db_connection()
    cursor = db_connection.cursor()
    enforcer_id = request.args.get('enforcer_id')
    query = "SELECT * FROM enforcer_accounts WHERE enforcer_id=%s"
    cursor.execute(query, (enforcer_id,))
    enforcer_data = cursor.fetchone()
    if request.method == 'POST':
        password = request.form['password']
        phone_number = request.form['phone_number']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        assigned_location = request.form['assigned_location']

    cursor.execute("UPDATE enforcer_accounts SET password=%s, phone_number=%s, first_name=%s, last_name=%s, assigned_location=%s WHERE enforcer_id=%s",
                   (password, phone_number, first_name, last_name, assigned_location, enforcer_id))
    
  # Adding data to the activity logs
    current_date_time = datetime.datetime.now()
    date = current_date_time.strftime('%A, %B %d, %Y')
    time = current_date_time.strftime('%I:%M %p')
    action = f"Enforcer {first_name} {last_name} information was updated."
    cursor.execute("INSERT INTO activity_logs (date, time, action) VALUES (%s, %s, %s)", (date, time, action))
    db_connection.commit()
    cursor.close()
        
    flash('Enforcer information updated successfully!', 'success')
    return redirect(url_for('enforcer.enforcer_data'))
    