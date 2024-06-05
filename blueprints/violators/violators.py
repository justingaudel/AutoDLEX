from flask import Blueprint, redirect,render_template,request,url_for,make_response
from db_utils import get_db_connection
from openpyxl import Workbook




db_connection = get_db_connection()
cursor = db_connection.cursor()

violator_bp = Blueprint("violators", __name__, template_folder="templates")

@violator_bp.route('/violator_list')
def violator_list():
    cursor.execute("SELECT * FROM violators_data WHERE status = 'unsettled'")
    data =  cursor.fetchall()
    return render_template('Violator_list.html',violators = data)

@violator_bp.route('/view_violator')
def view_violator():
    violator_id = request.args.get('violator_id')
    query = "SELECT * FROM violators_data WHERE violators_id = %s"
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
    query = "SELECT * FROM violators_data WHERE violators_id  = %s"
    cursor.execute(query, (violator_id,))
    violator_data = cursor.fetchone()
    
    #getting the tct number of the violator
    tct_number = " Select tct_number from violators_data where violators_id = %s"
    cursor.execute(tct_number, (violator_id,))
    tct_number = cursor.fetchone()
    
    tct_number = tct_number[0]
    
    extracted_data = "Select * from extracted_data where tct_number = %s"
    cursor.execute(extracted_data, (tct_number,))
    extracted_data = cursor.fetchone()
    
    return render_template('violators_data/view-violators-data.html',extracted_data = extracted_data , violator_data = violator_data)

    
# Editing/Updating  violators data 
from flask import render_template, request

@violator_bp.route('/edit_violators_data', methods=['GET', 'POST'])  
def edit_violators_data():
    
    violator_id = request.args.get('violator_id')
    # Assuming you have a function to get violator data from the database
    query = "SELECT * FROM violators_data WHERE violators_id  = %s"
    cursor.execute(query, (violator_id,))
    violator_data = cursor.fetchone()
    
    if request.method == 'POST':
        violator_id = request.form['violators_id']
        violation = request.form['violation']
        time = request.form['time']
        date = request.form['date']
        barangay = request.form['barangay']
        plateNumber = request.form['plateNumber']
        vehicle = request.form['vehicle']
        status = request.form['status']
       
        
        cursor.execute("UPDATE violators_data SET violation=%s, time=%s, date=%s, barangay=%s, plateNumber=%s, vehicle=%s ,status=%s WHERE violators_id  = %s",
                       (violation, time, date, barangay, plateNumber, vehicle, status,violator_id))
        db_connection.commit() 

        return redirect(url_for('violators.violator_list'))

    # Assuming violator_id is passed as a query parameter

   
    return render_template('violators_data/edit-violators-data.html', violator_data=violator_data)


        
#deleting of violators data        
@violator_bp.route('/delete_violator')
def delete_violator():
    violators_id = request.args.get('violator_id').split(',')
    for violator in violators_id:
        cursor.execute("DELETE FROM violators_data WHERE violators_id = %s", (violator,))
        db_connection.commit() 
    return redirect(url_for('settled_reports'))



@violator_bp.route('/excellReports')
def excellReports():
    violator_ids = request.args.get('violator_ids').split(',')
    all_data = []

    for violator_id in violator_ids:
        cursor.execute("SELECT * FROM violators_data WHERE violators_id = %s", (violator_id,))
        data = cursor.fetchall()
        all_data.extend(data)
    
    wb = Workbook()
    sheet = wb.active
    
    sheet['G2'] = 'Settled Reports Of Violators'
    sheet['A3'] = 'Violator_id'
    sheet['B3'] = 'Enforcer_id'
    sheet['C3'] = 'Extracted_id'
    sheet['D3'] = 'Ticket Number'
    sheet['E3'] = 'Violation'
    sheet['F3'] = 'Time'
    sheet['G3'] = 'Date'
    sheet['H3'] = 'Barangay'
    sheet['I3'] = 'Plate Number'
    sheet['J3'] = 'Vehicle'
    sheet['K3'] = 'Status'
    
    
    for row_index, row_data in enumerate(all_data, start=4):  # Start from row 4 for data population
        sheet.cell(row=row_index, column=1).value = row_data[0]  # Violator_id
        sheet.cell(row=row_index, column=2).value = row_data[1]  # Violation
        sheet.cell(row=row_index, column=3).value = row_data[2]  # Time
        sheet.cell(row=row_index, column=4).value = row_data[3]  # Date
        sheet.cell(row=row_index, column=5).value = row_data[4]  # Barangay
        sheet.cell(row=row_index, column=6).value = row_data[5]  # Plate Number
        sheet.cell(row=row_index, column=7).value = row_data[6]  # Vehicle
        sheet.cell(row=row_index, column=8).value = row_data[7]
        sheet.cell(row=row_index, column=9).value = row_data[8]
        sheet.cell(row=row_index, column=10).value = row_data[9]
        sheet.cell(row=row_index, column=11).value = row_data[10]
        
    file_path = 'temp.xlsx'
    wb.save(file_path)

    # Close database connection
    

    # Serve the file as a response
    response = make_response(open(file_path, 'rb').read())
    response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response.headers['Content-Disposition'] = 'attachment; filename=Settled_Reports.xlsx'

    return response


       
#routes for Violators data view includes delete, edit, and view