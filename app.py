from flask import Flask, request, render_template, session, redirect, url_for
from blueprints.enforcer.enforcer import enforcer_bp
from blueprints.violators.violators import violator_bp
from blueprints.extracted_data.svm import svm_bp
from blueprints.image_processing.text_extraction import text_extraction_bp
from db_utils import get_db_connection





app = Flask(__name__)


app.register_blueprint(enforcer_bp) #blueprint for the enforcer pages
app.register_blueprint(violator_bp) #blueprint for violators page
app.register_blueprint(svm_bp) #blueprint for the svm alghorithm
app.register_blueprint(text_extraction_bp) #blueprint for text extraction
# Set a secret key for the Flask application
app.secret_key = b'CTMEU/'

#  connection to the MySQL database
db_connection = get_db_connection()
cursor = db_connection.cursor()

# Create a cursor object to execute SQL queries


# Path to Tesseract executable




@app.route('/logout')
def logout():
    session.pop('loggedins',None)
    session.pop('username',None)
    return redirect(url_for('enforcer.enforcer'))


@app.route('/logout_admin')
def logout_admin():
    session.pop('loggedin',None)
    session.pop('username',None)
    return redirect(url_for('admin_signin'))


@app.route('/')
def interface():
    if 'loggedins' in session:
        return redirect(url_for('camera'))
    elif 'loggedin' in session:
        return redirect(url_for('index'))
    
    # Call loggedin() or loggedins() function here if needed
    # Example: loggedins('index')
    # Example: loggedin('camera')

    return render_template('front-interface.html')



@app.route('/camera')
def camera():
    username = request.args.get('username')
    return render_template('camera.html')


@app.route('/violators_form', methods=['GET','POST'])
def violators_form():
    msg = ''  # Initialize msg here
    if request.method == 'POST':
        violation = request.form['violation']
        time = request.form['time']
        date = request.form['date']
        barangay = request.form['barangay']
        plateNumber = request.form['plateNumber']
        vehicle = request.form['vehicle']
        status = request.form['status']

        cursor.execute("INSERT INTO violators_data (violation, time, date, barangay, plateNumber, vehicle, status) VALUES (%s, %s, %s, %s, %s, %s, %s)", (violation, time, date, barangay, plateNumber, vehicle, status))

        db_connection.commit()
        msg = 'Report Submitted Successfully!'

    return render_template('camera.html', msg=msg)

    
    
    
@app.route('/index')
def index():
    try:
        # Fetch counts
        cursor.execute("SELECT COUNT(*) FROM enforcer_accounts")
        enforcers_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM violators_data")
        violators_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM violators_data WHERE status = 'unsettled'")
        unsettled_reports_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM violators_data WHERE status = 'settled'")
        settled_reports_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT * FROM violators_data")
        violators = cursor.fetchall()
        
        # Pass counts and data to template
        return render_template('index.html', enforcers_count=enforcers_count, violators_count=violators_count,
                               unsettled_reports_count=unsettled_reports_count, settled_reports_count=settled_reports_count,
                               violators=violators)
    except Exception as e:
        # Handle any exceptions gracefully
        return render_template('error.html', error=str(e))





@app.route('/settled_reports')
def settled_reports():
    cursor.execute("SELECT * FROM violators_data WHERE status = 'settled'")
    data =  cursor.fetchall()
    return render_template('settled-reports.html',reports = data)



#routes for admin
@app.route('/admin_signin', methods=['GET','POST'])
def admin_signin():
    if 'loggedin' in session:
        return redirect(url_for('index'))
    msg = ''
    if request.method == 'POST':  
        email = request.form['email']
        password = request.form['password']
        cursor.execute("SELECT * FROM admin_accounts WHERE email = %s AND password = %s", (email, password))  # Corrected the SQL query
        record = cursor.fetchone()
        if record:
            session['loggedin'] = True
            session['email'] = record[1]
            return redirect(url_for('index'))  
        else:
            msg = "Incorrect password or email!"
    return render_template('admin-login.html', msg=msg)


@app.route('/add_enforcer', methods=['POST', 'GET'])
def add_enforcer():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirmPassword']
        
        if password != confirm_password:
            # Passwords don't match, return a message
            return render_template('new-enforcer.html', msg="Passwords do not match!")
        else:
            # Insert data into the database
            sql = "INSERT INTO enforcer_accounts (username, password) VALUES (%s, %s)"
            val = (username, password)
            cursor.execute(sql, val)
            db_connection.commit()  # Commit changes to the database

            # Redirect to a success page or another route
            return redirect(url_for('enforcer_data'))
    
    # If it's a GET request or if password matches, render the template without a message
    return render_template('new-enforcer.html')


if __name__ == '__main__':
    app.run(debug=True)