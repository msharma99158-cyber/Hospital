from flask import Flask, render_template, request, flash, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

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
    role=db.Column(db.String(20), default="user")  # Default role is user

# ---------------- CREATE TABLES + DEFAULT ADMIN ----------------

with app.app_context():
    db.create_all()

    # Create default admin if not exists
    if not User.query.filter_by(username="admin").first():
        admin = User(username="admin", password=generate_password_hash("123"), role="ADMIN")
        db.session.add(admin)
        db.session.commit()

# ---------------- LOGIN REQUIRED DECORATOR ----------------

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
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
        print(name, email, phone, subject, message)
        flash("Your message has been sent successfully")
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
        admission_date = request.form['admission_date']
        days = request.form['days']

        new_patient = Patient(
            name=patient_name,
            contact=contact,
            bed_type=bed_type,
            admission_date=admission_date,
            days=days
        )

        db.session.add(new_patient)
        db.session.commit()

        flash("Bed booked successfully!")
        return redirect(url_for('bedbooking'))

    return render_template('bedbooking.html')


@app.route("/appointment")
@login_required
def appointment():
    return render_template("appointment.html")


@app.route("/emergency")
def emergency():
    return render_template("emergency.html")


# ---------------- AMBULANCE ( No LOGIN REQUIRED) ----------------

@app.route("/ambulance", methods=['GET', 'POST'])
def ambulance():
    return render_template("ambulance.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists!")
            return redirect(url_for('register'))
        hashed_password = generate_password_hash(password)
        
        # Create new user
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful!")
        return redirect(url_for('login'))

    return render_template("register.html")


# ---------------- LOGIN ----------------

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
       # db.session.add(user)
       # db.session.commit()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            if user.role=="admin":
                return redirect(url_for('admin_dashboard'))
            flash("Logged in successfully!")
            return redirect(url_for('services'))
        else:
            flash("Invalid Username or Password")
            return redirect(url_for('login'))

    return render_template("login.html")

@app.route('/admin')
def admin_dashboard():
    if "role" not in session or session["role"] != "admin":
        user =user.query.all()
        return render_template("admin_dashboard.html", user=user)
    else:
        flash("Access denied! Admins only.")
        return redirect(url_for('login'))


# ---------------- LOGOUT ----------------

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/users')
def users():
    all_users = User.query.all()
    return str(all_users)
   

# ---------------- RUN APP ----------------

if __name__ == '__main__':
    app.run(debug=True)
