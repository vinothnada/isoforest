from flask import Flask, render_template, request, redirect, url_for, session, g
import mysql.connector
import pandas as pd
from sklearn.ensemble import IsolationForest
import xlrd
import MySQLdb
from fileinput import filename

connection = mysql.connector.connect(host='localhost',
                                     user='root',
                                     password='root',
                                     port='3306',
                                     database='isolation_forest')

cursor = connection.cursor()
app = Flask(__name__)
app.secret_key = "super secret key"


@app.route("/")
def index():
    return render_template("index.html")


@app.route('/home')
def home():
    trval = view_data()
    return render_template('home.html', username=session['username'], row=trval)


@app.post('/view')
def view():
    file = request.files['file']
    file.save(file.filename)
    data = pd.read_excel(file, engine='openpyxl')
    print(file.filename)
    if file and file.filename.endswith('.xlsx'):
        # Read Excel file into pandas DataFrame
        df = pd.read_excel(file)
        for index, row in df.iterrows():
            insert_query = f"""INSERT INTO trn (tid, alt)
                VALUES ('{row['TRNID']}', '{row['ALERT']}');
                """
            cursor.execute(insert_query)
        #connection.commit()
        #cursor.close()
        #connection.close()
    # Return HTML snippet that will render the table
    return data.to_html()


@app.route('/view_data')
def view_data():
    cursor.execute('SELECT svaccno,tramt,tccd,drcr,trdate,brch,prtp,srctr from transactions_sv ')
    row = cursor.fetchall()
    return row


@app.post('/iso_forest')
def iso_forest():
    print("here")
    cursor.execute('SELECT * from users ')
    record = cursor.fetchall()
    #connection.commit()
    #cursor.close()
    #connection.close()
    if record:
        return record
    else:
        msg = 'Not found'
        return msg


@app.route("/saving")
def saving():
    return render_template('saving.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method:
        username = request.form.get('username')
        password = request.form.get('password')
        cursor.execute('SELECT * from users WHERE username = %s AND password = %s',
                       (username, password))
        record = cursor.fetchone()
        if record:
            session['logged'] = True
            session['username'] = record[1]
            return redirect(url_for('home'))
        else:
            msg = 'Incorrect username/password.try again!'
    return render_template('index.html', msg=msg)


@app.route('/logout')
def logout():
    session.pop('logged', None)
    session.pop('username', None)
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
