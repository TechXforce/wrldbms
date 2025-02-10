
from flask import Flask, render_template, request, session, redirect, url_for, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from sqlalchemy import text
import json
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/wrldb2'
app.config['SQLALCHEMY_TRACK_NOTIFICATIONS'] = False
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["LOGBOOK_FOLDER"] = os.path.join(os.getcwd(), 'logbooks')
app.config["REPORT_FOLDER"] = os.path.join(os.getcwd(), 'reports')
app.secret_key = 'wrldb2'

db = SQLAlchemy(app)

class Vacancies(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    adtitle=db.Column(db.String(255))
    small_description=db.Column(db.String(500))
    long_description=db.Column(db.String(1000))
    image=db.Column(db.String(65535))
    status=db.Column(db.String(1))

class Logbook(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    filename = db.Column(db.String(255))
    uploaded_time = db.Column(db.String(255))
    uploaded_date = db.Column(db.String(255))

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    filename = db.Column(db.String(255))
    uploaded_time = db.Column(db.String(255))
    uploaded_date = db.Column(db.String(255))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/lb_create', methods=['GET'])
def lb_create_get():
    return render_template('lb_create.html')

@app.route('/r_create', methods=['GET'])
def r_create_get():
    return render_template('r_create.html')

@app.route('/lb_create', methods=['POST'])
def lb_create_post():
    title = request.form.get('title')
    logbook = request.files['logbook']
    filename = secure_filename(logbook.filename)
    logbook.save(os.path.join(app.config["LOGBOOK_FOLDER"], filename))
    time = request.form.get('time')
    date = request.form.get('date')
    
    new_logbook = Logbook(title=title, filename=filename, uploaded_time=time, uploaded_date=date)
    db.session.add(new_logbook)
    db.session.commit()
    
    flash('Logbook uploaded successfully!',"success")
    return redirect(url_for('logbooks'))

@app.route('/r_create', methods=['POST'])
def r_create_post():
    title = request.form.get('title')
    report = request.files['report']
    filename = secure_filename(report.filename)
    report.save(os.path.join(app.config["REPORT_FOLDER"], filename))
    time = request.form.get('time')
    date = request.form.get('date')
    
    new_report = Report(title=title, filename=filename, uploaded_time=time, uploaded_date=date)
    db.session.add(new_report)
    db.session.commit()
    
    flash('Report uploaded successfully!',"success")
    return redirect(url_for('reports'))

@app.route('/logbooks')
def logbooks():
    logbooks = Logbook.query.all()
    return render_template('logbooks.html', logbooks=logbooks)

@app.route('/reports')
def reports():
    reports = Report.query.all()
    return render_template('reports.html', reports=reports)

@app.route('/get_logbook/<filename>')
def get_logbook(filename):
    return send_from_directory(app.config["LOGBOOK_FOLDER"], filename, as_attachment=True)

@app.route('/get_report/<filename>')
def get_report(filename):
    report_path = os.path.join(app.config["REPORT_FOLDER"], filename)
    if os.path.exists(report_path):
        return send_from_directory(app.config["REPORT_FOLDER"], filename, as_attachment=True)
    else:
        flash('Report not found', 'error')
        return redirect(url_for('reports'))

@app.route('/report')
def report():
    return render_template('report.html')

@app.route('/vacancies',methods=['GET'])
def vacancies():
    adverts = Vacancies.query.all()
    return render_template('vacancies.html', adverts=adverts)

@app.route('/v_create', methods=['GET', 'POST'])
def v_create():
    if request.method == 'POST':
        # Handle form submission here
        adtitle = request.form.get('adtitle')
        small_description = request.form.get('small_description')
        long_description = request.form.get('long_description')
        image = request.files.get('image')
        status = request.form.get('status', '0')


        # Check if image is not None
        if image is not None:
            # Save image to uploads folder
            image.save(os.path.join(app.config["UPLOAD_FOLDER"], image.filename))

            # Save data to database
            query = text("INSERT INTO vacancies (adtitle, small_description, long_description, image, status) VALUES (:adtitle, :small_description, :long_description, :image, :status)")
            db.session.execute(query, {"adtitle": adtitle, "small_description": small_description, "long_description": long_description, "image": image.filename, "status": status})
        else:
            # Save data to database without image
            query = text("INSERT INTO vacancies (adtitle, small_description, long_description, status) VALUES (:adtitle, :small_description, :long_description, :status)")
            db.session.execute(query, {"adtitle": adtitle, "small_description": small_description, "long_description": long_description, "status": status})

        db.session.commit()

        flash("Advert Added Successfully", "success")
        return redirect(url_for('vacancies'))

    return render_template('v_create.html')

@app.route('/v_edit/<int:id>', methods=['GET', 'POST'])
def v_edit(id):
    advert = Vacancies.query.get(id)
    if advert is None:
        flash('Advert not found', 'danger')
        return redirect(url_for('vacancies'))

    if request.method == 'POST':
        advert.adtitle = request.form.get('adtitle')
        advert.small_description = request.form.get('small_description')
        advert.long_description = request.form.get('long_description')
        advert.status = request.form.get('status')

        # Handle image upload
        image = request.files.get('image')
        if image:
            # Save image to uploads folder
            image.save(os.path.join(app.config["UPLOAD_FOLDER"], image.filename))
            advert.image = image.filename

        db.session.commit()
        flash('Advert updated successfully', 'success')
        return redirect(url_for('vacancies'))

    return render_template('v_edit.html', advert=advert)

@app.route('/v_delete/<int:id>', methods=['POST'])
def v_delete(id):
    advert = Vacancies.query.get(id)
    if advert is None:
        flash('Advert not found', 'danger')
        return redirect(url_for('vacancies'))

    # Delete the advert
    db.session.delete(advert)
    db.session.commit()

    # Delete the associated image file
    if advert.image:
        image_path = os.path.join(app.config["UPLOAD_FOLDER"], advert.image)
        if os.path.exists(image_path):
            os.remove(image_path)

    flash('Advert deleted successfully', 'success')
    return redirect(url_for('vacancies'))


app.run(debug=True)
#username=current_user.username