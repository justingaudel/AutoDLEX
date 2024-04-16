from flask import Blueprint, redirect,render_template,request,url_for
from db_utils import get_db_connection 


db_connection = get_db_connection()
cursor = db_connection.cursor()

violator_bp = Blueprint("violators", __name__, template_folder="templates")

@violator_bp.route('/violator_list')
def violator_list():
    cursor.execute("SELECT * From  violators_data")
    data =  cursor.fetchall()
    return render_template('Violator_list.html',violators = data)

@violator_bp.route('/view_violator')
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
@violator_bp.route('/view_violators_data')
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
@violator_bp.route('/edit_violators_data', methods=['GET', 'POST'])  
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
@violator_bp.route('/delete_violator')
def delete_violator():
    violator_id = request.args.get('violator_id')
    cursor.execute("DELETE FROM violators_data WHERE vd_id = %s", (violator_id,))
    db_connection.commit() 
    return redirect(url_for('violator_list'))
       
#routes for Violators data view includes delete, edit, and view