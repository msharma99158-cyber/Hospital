from dbm import sqlite3

from flask import Flask, render_template, request, flash, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
app = Flask(__name__)
app.secret_key = "hospital_secret_key"

# ---------------- DATABASE CONFIG ----------------
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///hospital.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ---------------- MODELS ----------------

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(20), nullable=False)
    bed_type = db.Column(db.String(50), nullable=False)
    admission_date = db.Column(db.Date, nullable=False)
    days = db.Column(db.Integer, nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default="user")  # Default role is user

class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    subject = db.Column(db.String(200))
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

class AmbulanceRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_name = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(20), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    emergency_type = db.Column(db.String(100), nullable=False)
    request_time = db.Column(db.DateTime, default=db.func.current_timestamp())
    status = db.Column(db.String(50), default="Pending")


class EmergencyRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # Patient Verification
    patient_id = db.Column(db.String(50), nullable=False)

    # Patient Information
    patient_name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    blood_group = db.Column(db.String(10), nullable=True)
    medical_history = db.Column(db.Text, nullable=False)

    # Guardian Information
    guardian_name = db.Column(db.String(100), nullable=False)
    relation = db.Column(db.String(50), nullable=False)
    contact_number = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text, nullable=False)

    # Insurance
    insurance_provider = db.Column(db.String(100), nullable=True)
    policy_number = db.Column(db.String(100), nullable=True)

    # Reason
    reason = db.Column(db.String(100), nullable=False)

    status = db.Column(db.String(20), default="Pending")
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    patient_name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    contact = db.Column(db.String(20), nullable=False)

   # department = db.Column(db.String(100), nullable=False)
   # doctor = db.Column(db.String(100), nullable=False)

    appointment_date = db.Column(db.Date, nullable=False)
    time_slot = db.Column(db.String(20), nullable=False)

    status = db.Column(db.String(20), default="Pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Support(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    payment_method = db.Column(db.String(50))   # ✅ ADD THIS
    message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
# ---------------- CREATE TABLES + DEFAULT ADMIN ----------------

with app.app_context():
    db.create_all()

    # Create default admin if not exists
    if not User.query.filter_by(username="admin").first():
        admin = User(username="admin", password=generate_password_hash("123"), role="admin")
        db.session.add(admin)
        db.session.commit()

# ---------------- LOGIN REQUIRED DECORATOR ----------------

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in first!", "login_error")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ---------------- ROUTES ----------------

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        subject = request.form['subject']
        message = request.form['message']

        # Save contact message to database
        new_message = ContactMessage(
            name=name,
            email=email,
            phone=phone,
            subject=subject,
            message=message
        )
        db.session.add(new_message)
        db.session.commit()

        flash("Your message has been sent successfully!")
        return redirect(url_for('contact'))

    return render_template('contact.html')

@app.route('/services')
def services():
    return render_template('services.html')

# ---------------- BED BOOKING (LOGIN REQUIRED) ----------------

@app.route('/bedbooking', methods=['GET', 'POST'])
@login_required
def bedbooking():
    if request.method == 'POST':
        patient_name = request.form['patient_name']
        contact = request.form['contact']
        bed_type = request.form['bed_type']
        admission_date_str= request.form['admission_date']
        admission_date = datetime.strptime(admission_date_str, '%Y-%m-%d').date()

        days = int(request.form['days'])

        new_patient = Patient(
            name=patient_name,
            contact=contact,
            bed_type=bed_type,
            admission_date=admission_date,
            days=days
        )

        db.session.add(new_patient)
        db.session.commit()

        flash("Bed booked successfully!","form_success")
        return redirect(url_for('bedbooking'))

    return render_template('bedbooking.html')

@app.route("/appointment", methods=["GET", "POST"])
@login_required
def appointment():

   

    if request.method == "POST":

        
        # If final booking submitted
        if request.form.get("book") == "yes":

            patient_name = request.form.get("patient_name")
            age = request.form.get("age")
            gender = request.form.get("gender")
            contact = request.form.get("contact")
           
            date_str = request.form.get("appointment_date")
            time_slot = request.form.get("time_slot")

            appointment_date = datetime.strptime(date_str, "%Y-%m-%d").date()

            new_appointment = Appointment(
                patient_name=patient_name,
                age=age,
                gender=gender,
                contact=contact,
               
                appointment_date=appointment_date,
                time_slot=time_slot
            )

            db.session.add(new_appointment)
            db.session.commit()

            flash("Appointment booked successfully!","form_success")
            return redirect('/appointment')

    return render_template(
        'appointment.html')
       
# ---------------- EMERGENCY REQUEST ----------------

@app.route('/emergency', methods=['GET', 'POST'])
def emergency():
    if request.method == 'POST':

        dob_str = request.form['dob']
        dob = datetime.strptime(dob_str, "%Y-%m-%d").date()

        new_request = EmergencyRequest(
            patient_id=request.form['patient_id'],
            patient_name=request.form['patient_name'],
            dob=dob,
            blood_group=request.form['blood_group'],
            medical_history=request.form['medical_history'],

            guardian_name=request.form['guardian_name'],
            relation=request.form['relation'],
            contact_number=request.form['contact_number'],
            email=request.form['email'],
            address=request.form['address'],

            insurance_provider=request.form.get('insurance_provider'),
            policy_number=request.form.get('policy_number'),

            reason=request.form['reason']
        )

        db.session.add(new_request)
        db.session.commit()

        flash("Patient details submitted successfully!","form_success")
        return redirect(url_for('emergency'))

    return render_template('emergency.html')
# ---------------- AMBULANCE ----------------

@app.route("/ambulance", methods=['GET', 'POST'])
def ambulance():
    if request.method == 'POST':

        patient_name = request.form.get('patient_name')
        contact_number = request.form.get('contact_number')  # Make sure HTML name matches this
        pickup_location = request.form.get('pickup_location')
        emergency_type = request.form.get('emergency_type')

        new_request = AmbulanceRequest(
            patient_name=patient_name,
            contact=contact_number,
            location=pickup_location,
            emergency_type=emergency_type
        )

        db.session.add(new_request)
        db.session.commit()

        flash("Ambulance requested successfully!","form_success")
        return redirect(url_for('ambulance'))

    return render_template("ambulance.html")

# ---------------- REGISTER ----------------

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists!")
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please log in.","register_success")
        return redirect(url_for('login'))

    return render_template("register.html")

# ---------------- LOGIN ----------------

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        # ❌ User Not Found
        if not user:
            flash("User not found! Please register first.", "login_error")
            return redirect(url_for('home'))

        # ✅ Correct Password
        if check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role

            flash("Logged in successfully!", "login_success")

            if user.role == "admin":
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('home'))

        # ❌ Wrong Password
        else:
            flash("Invalid Username or Password", "login_error")
            return redirect(url_for('login'))

    return render_template("login.html")

# ---------------- ADMIN DASHBOARD ----------------

# ---------------- ADMIN DASHBOARD ----------------

@app.route('/admin')
@login_required
def admin_dashboard():
    if session.get("role") != "admin":
        flash("Access denied! Admins only.")
        return redirect(url_for('home'))

    # 🏥 Hospital Capacity (Change if needed)
    TOTAL_BEDS = 50  

    # 📊 Dashboard Statistics
    total_users = User.query.count()
    total_bed_bookings = Patient.query.count()
    available_beds = TOTAL_BEDS - total_bed_bookings

    total_appointments = Appointment.query.count()
    total_emergencies = EmergencyRequest.query.count()
    total_ambulances = AmbulanceRequest.query.count()

    total_support = Support.query.count()
    total_support_amount = db.session.query(db.func.sum(Support.amount)).scalar() or 0

    # 👥 Users list
    users = User.query.all()

    # 💛 Support donations list
    support_data = Support.query.order_by(Support.created_at.desc()).all()

    return render_template(
        "admin_dashboard.html",
        total_users=total_users,
        total_bed_bookings=total_bed_bookings,
        available_beds=available_beds,
        total_appointments=total_appointments,
        total_emergencies=total_emergencies,
        total_ambulances=total_ambulances,
        total_support=total_support,
        total_support_amount=total_support_amount,
        users=users,
        support_data=support_data
    )

# ---------------- VIEW CONTACT MESSAGES ----------------

@app.route('/admin/messages')
@login_required
def view_messages():
    if session.get("role") != "admin":
        flash("Access denied! Admins only.")
        return redirect(url_for('home'))

    messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    return render_template("admin_messages.html", messages=messages)

# ---------------- LOGOUT ----------------

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully!")
    return redirect(url_for('home'))

@app.route("/support", methods=["GET", "POST"])
@login_required
def support():

    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        amount = request.form.get("amount")
        message = request.form.get("message")
        payment_method = request.form.get("payment_method")

        new_support = Support(
            name=name,
            email=email,
            amount=amount,
            payment_method=payment_method,
            message=message
        )

        db.session.add(new_support)
        db.session.commit()

        flash("Thank you for supporting us ❤️","form_success")
        return redirect(url_for("support"))

    return render_template("support.html")

# ---------------- RUN APP ----------------

if __name__ == '__main__':
    app.run(debug=True)