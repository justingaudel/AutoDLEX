from flask import Blueprint, render_template,request,session,url_for,redirect
from db_utils import get_db_connection 


db_connection = get_db_connection()
cursor = db_connection.cursor()


enforcer_bp = Blueprint("enforcer",__name__,template_folder="templates")

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