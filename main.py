from flask import Flask, render_template,request,flash,redirect,url_for

app = Flask(__name__)
app.secret_key="hospital_secret_key"

@app.route('/')
def home():
    return render_template('home.html')
    

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET','POST'])
def contact():
    if request.method=='POST':
        name=request.form['name']
        email=request.form['email']
        phone=request.form['phone']
        subject=request.form['subject']
        message=request.form['message']
        print(name,email,phone,subject,message)
        flash("your message has been sent successfully")
        return redirect(url_for('contact'))
    return render_template('contact.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/bedbooking', methods=['GET', 'POST'])
def bedbooking():
    if request.method == 'POST':
        patient_name = request.form['patient_name']
        contact = request.form['contact']
        bed_type = request.form['bed_type']
        admission_date = request.form['admission_date']
        days = request.form['days']
        print (patient_name, contact, bed_type, admission_date, days)
        flash("Your form has been sent successfully")
        return redirect(url_for('bedbooking'))
    return render_template('bedbooking.html')

@app.route("/appointment")
def appointment():
    return render_template("appointment.html")

@app.route("/emergency")
def emergency():
    return render_template("emergency.html")

@app.route("/ambulance")
def ambulance():      
    return render_template("ambulance.html")

if __name__ == '__main__':
    app.run(debug=True)
