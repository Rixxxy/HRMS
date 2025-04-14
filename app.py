from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

# Initialize Flask app and database
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

# MySQL Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:mysql@localhost/hrms'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Admin Table with more fields
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    address = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Employee Table with more fields
class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    department = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Timesheet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    hours_worked = db.Column(db.Integer, nullable=False)
    task_description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    employee = db.relationship('Employee', backref=db.backref('timesheets', lazy=True))

# Route for the home page
@app.route('/')
def home():
    return render_template('home.html')

# Route for handling login
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    user_type = request.form.get('userType')

    if user_type == 'admin':
        user = Admin.query.filter_by(username=username).first()
    else:
        user = Employee.query.filter_by(username=username).first()

    if user and user.password == password:
        session['user'] = username
        session['role'] = user_type
        if user_type == 'admin':
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('emp_dashboard'))

    flash("Invalid Credentials! Try Again.", "danger")
    return redirect(url_for('home'))


@app.route('/attendance')
def attendance():
    return render_template('attendance.html')

# Route for the admin dashboard
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user' in session and session['role'] == 'admin':
        return render_template('admin_dashboard.html')
    return redirect(url_for('home'))

# Route for the employee dashboard
@app.route('/employee_dashboard')
def emp_dashboard():
    if 'user' in session and session['role'] == 'employee':
        return render_template('emp_dashboard.html')
    return redirect(url_for('home'))

# Route for the employees list (only for admin)
@app.route('/employees')
def employees():
    if 'user' in session and session['role'] == 'admin':
        employees = Employee.query.all()
        return render_template('employees.html', employees=employees)
    return redirect(url_for('home'))

# Route for the timesheet approval (only for admin)
@app.route('/timesheet_approval')
def timesheet_approval():
    if 'user' in session and session['role'] == 'admin':
        return render_template('timesheet_approval.html')
    return redirect(url_for('home'))

# Route for the reports (only for admin)
@app.route('/reports')
def reports():
    if 'user' in session and session['role'] == 'admin':
        return render_template('reports.html')
    return redirect(url_for('home'))

# Route for the settings (only for admin)
@app.route('/settings')
def settings():
    if 'user' in session and session['role'] == 'admin':
        return render_template('settings.html')
    return redirect(url_for('home'))

# Route for logging out
@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('role', None)
    
    response = redirect(url_for('home'))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'

    return response

# Route for the signup page
@app.route('/signup')
def signup():
    return render_template('signup.html')

# Route for handling the sign-up process
@app.route('/signup', methods=['POST'])
def signup_post():
    username = request.form['username']
    password = request.form['password']
    full_name = request.form['full_name']
    email = request.form['email']
    phone = request.form['phone']
    date_of_birth = request.form['date_of_birth']
    role = request.form['role']
    department = request.form['department']  # For employees only

    if role == 'admin':
        user = Admin(username=username, password=password, full_name=full_name, email=email,
                     phone=phone, date_of_birth=date_of_birth)
        db.session.add(user)
        db.session.commit()
        flash("Admin account created successfully!", "success")
    elif role == 'employee':
        user = Employee(username=username, password=password, full_name=full_name, email=email,
                        phone=phone, date_of_birth=date_of_birth, role=role, department=department)
        db.session.add(user)
        db.session.commit()
        flash("Employee account created successfully!", "success")

    return redirect(url_for('home'))

@app.route('/notifications')
def notifications():
    return render_template('notifications.html')

@app.route('/helpdesk')
def helpdesk():
    return render_template('helpdesk.html')

@app.route('/timesheet')
def timesheet():
    return render_template('timesheet.html')

@app.route('/settings_emp')
def settings_emp():
    return render_template('settings_emp.html')

@app.route('/update_settings', methods=['POST'])
def update_settings():
    # Update settings logic
    return redirect(url_for('settings_emp'))



# Run the app
if __name__ == '__main__':
    app.run(debug=True)
