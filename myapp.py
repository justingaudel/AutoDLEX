from flask import Flask, request, render_template, session, redirect, url_for
from flask import request
from PIL import Image
import mysql.connector
import numpy as np
import io
import cv2
import pytesseract 

app = Flask(__name__)

# Set a secret key for the Flask application
app.secret_key = b'CTMEU/'

#  connection to the MySQL database
db_connection = mysql.connector.connect(
    host='localhost',
    user='root',
    password='',
    database='CTMEU'
)

# Check if the connection was successful
if db_connection.is_connected():
    print('Connected to MySQL database')
else:
    print('Failed to connect to MySQL database')

# Create a cursor object to execute SQL queries
cursor = db_connection.cursor()

# Path to Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def preprocess_image(img):
    # Convert the image to grayscale
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian Blur to reduce noise
    img_blur = cv2.GaussianBlur(img_gray, (5, 5), 0)

    # Apply adaptive thresholding
    img_thresh = cv2.adaptiveThreshold(img_blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

    return img_thresh

@app.route('/logout')
def logout():
    session.pop('loggedin',None)
    session.pop('username',None)
    return redirect(url_for('enforcer'))


@app.route('/logout_admin')
def logout_admin():
    session.pop('loggedin',None)
    session.pop('username',None)
    return redirect(url_for('admin_signin'))


@app.route('/')
def interface():
    return render_template('front-interface.html')



@app.route('/enforcer', methods=['GET', 'POST'])
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


@app.route('/camera')
def camera():
    return render_template('camera.html')


@app.route('/violators', methods=['GET', 'POST'])
def violators():
    if request.method == 'POST':
        # Retrieve form data
        extracted_text = request.form['extracted_text']
        image_data = request.form['image_data']
        extracted_text_split = extracted_text.split()
        # Insert data into MySQL database

        cursor.execute("INSERT INTO extracted_data (extracted_text, image_data) VALUES (%s, %s)", (extracted_text, image_data))
        db_connection.commit()
        return render_template('violators-form.html')
    

@app.route('/violators_form', methods=['GET','POST'])
def violators_form():
    if request.method == 'POST':
        violation = request.form['violation']
        time = request.form['time']
        date = request.form['date']
        barangay = request.form['barangay']
        plateNumber = request.form['plateNumber']
        vehicle = request.form['vehicle']

        cursor.execute("INSERT INTO violators_data (violation, time, date, barangay, plateNumber, vehicle) VALUES (%s, %s, %s, %s, %s, %s)", (violation, time, date, barangay, plateNumber, vehicle))

        db_connection.commit()
        msg = 'Report Submitted Succesfully!'
        return render_template('camera.html',msg=msg)
    
    
    
@app.route('/index')
def index():
    cursor.execute("SELECT * From  violators_data")
    data =  cursor.fetchall()
    return render_template('index.html',violators = data)





@app.route('/settled_reports')
def settled_reports():
    return render_template('settled-reports.html')



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


#routes for admin



#routes for Violators data view includes delete, edit, and view

#viewing of violators data all

@app.route('/violator_list')
def violator_list():
    cursor.execute("SELECT * From  violators_data")
    data =  cursor.fetchall()
    return render_template('Violator_list.html',violators = data)


#viewing of violators data all
@app.route('/view_violator')
def view_violator():
    violator_id = request.args.get('violator_id')
    query = "SELECT * FROM violators_data WHERE vd_id = %s"
    cursor.execute(query, (violator_id,))
    violator_data = cursor.fetchone()
    if violator_data:
        return render_template('violators_data/view-violators-data.html', violator_data=violator_data)
    else:
        return "Violator not found", 404
    
    
#viewing of violators data specific 
@app.route('/view_violators_data')
def view_violators_data():
    violator_id = request.args.get('violator_id')
    query = "SELECT * FROM violators_data WHERE vd_id = %s"
    cursor.execute(query, (violator_id,))
    violator_data = cursor.fetchone()
    if violator_data:
        return render_template('violators_data/edit-violators-data.html', violator_data=violator_data)
    else:
        return "Violator not found", 404
    
# Editing/Updating  violators data 
@app.route('/edit_violators_data', methods=['GET', 'POST'])  
def edit_violators_data():
    if request.method == 'POST':
        vd_id = request.form['violation_id']
        violation = request.form['violation']
        time = request.form['time']
        date = request.form['date']
        barangay = request.form['barangay']
        plateNumber = request.form['plateNumber']
        vehicle = request.form['vehicle']
        
        cursor.execute("UPDATE violators_data SET violation=%s, time=%s, date=%s, barangay=%s, plateNumber=%s, vehicle=%s WHERE vd_id = %s",
                       (violation, time, date, barangay, plateNumber, vehicle, vd_id))
        db_connection.commit() 

        return redirect(url_for('violator_list'))

   
    return render_template('edit_violators_data.html')

        
#deleting of violators data        
@app.route('/delete_violator')
def delete_violator():
    violator_id = request.args.get('violator_id')
    cursor.execute("DELETE FROM violators_data WHERE vd_id = %s", (violator_id,))
    db_connection.commit() 
    return redirect(url_for('violator_list'))
       
#routes for Violators data view includes delete, edit, and view




#routes for Enforcers includes add


@app.route('/enforcer_data')
def enforcer_data():
    return render_template('enforcer.html')

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

#upload folder for images

#routes for Enforcers includes add




#This is for processing images extracting text from images
    
@app.route('/process_image', methods=['POST'])
def process_image():
    try:
        if 'image' not in request.files:
            return "No image provided"

        # Read the image file sent from the frontend
        image_data = request.files['image'].read()

        # Convert the image bytes to PIL Image
        image = Image.open(io.BytesIO(image_data))

        # Convert the image to OpenCV format
        img_cv = np.array(image)

        # Preprocess the image
        img_processed = preprocess_image(img_cv)

        # Perform OCR
        extracted_text = pytesseract.image_to_string(img_processed)

        return extracted_text
        
    except Exception as e:
        return f"Error processing image: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)
