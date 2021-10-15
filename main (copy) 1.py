import logging
from fhirclient import client

from flask import Flask, render_template
# from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


# app setup
smart_defaults = {
    'app_id': 'my_web_app',
    # 'api_base': 'https://fhir-open-api-dstu2.smarthealthit.org',
    # 'api_base': 'https://sb-fhir-stu3.smarthealthit.org/smartstu3/data',
    # 'api_base': 'http://test.fhir.org/r4/',
    # 'api_base': 'https://fhir-open.cerner.com/dstu2/ec2458f2-1e24-41c8-b71b-0e701af7583d',
    'api_base': 'https://fhir-open.cerner.com/r4/ec2458f2-1e24-41c8-b71b-0e701af7583d',
    # 'api_base': 'https://fhir-open.cerner.com/dstu2',
    # 'api_base': 'https://r4.smarthealthit.org',
    # 'api_base': 'https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/DSTU2',
    'redirect_uri': 'http://localhost:8000/fhir-app/',
}

app = Flask('app')

logging.basicConfig(level=logging.DEBUG)

# Flask-WTF requires an encryption key - the string can be anything
app.config['SECRET_KEY'] = 'C2HWGVoMGfNTBsrYQg8EcMrdTimkZfAb'

# Flask-Bootstrap requires this line
Bootstrap(app)


class NameForm(FlaskForm):
    name = StringField('Enter the family name of the patient to search for (max 25 results):', validators=[DataRequired()])
    submit = SubmitField('Find')

@app.route('/', methods=['GET', 'POST'])
def index():
    # names = get_names(ACTORS)
    names = ['Ken', 'Ella']
    # you must tell the variable 'form' what you named the class, above
    # 'form' is the variable name used in this template: index.html
    form = NameForm()
    body = ""
    
    smart = client.FHIRClient(settings=smart_defaults)
    import fhirclient.models.patient as p
    search = p.Patient.where(struct={'_count': '23', 'family': 'Smith'})
    # search = p.Patient.where(struct={'family': 'Smith', 'gender': 'female'})
    patients = search.perform_resources(smart.server)
    # print(patients)
    cur_id_patient = 1
    for patient_this in patients:
        patient_id = patient_this.id.encode('ascii', 'ignore')
        birth_date = "None"
        if patient_this.birthDate is not None:
            birth_date = patient_this.birthDate.isostring
        name = smart.human_name(patient_this.name[0])
        details = "<p>Patient details #{}<ul><li>ID: {}</li><li>Full Name: {}</li><li>Birth date: {}</li></ul>".format(cur_id_patient, patient_id, name, birth_date)
        print(details)
        body += details
        cur_id_patient += 1

    if form.validate_on_submit():
        name = form.name.data

        smart = client.FHIRClient(settings=smart_defaults)
        import fhirclient.models.patient as p
        search = p.Patient.where(struct={'_count': bytes('100', 'utf-8'), 'family': name})

        patients = search.perform_resources(smart.server)
        
        body = "<br><h2>Results success!</h2><br>"

        # print(patients)
        cur_id_patient = 1
        for patient_this in patients:
            patient_id = patient_this.id.encode('ascii', 'ignore')
            birth_date = "None"
            if patient_this.birthDate is not None:
                birth_date = patient_this.birthDate.isostring
            name = smart.human_name(patient_this.name[0])
            details = "<p>Patient details #{}<ul><li>ID: {}</li><li>Full Name: {}</li><li>Birth date: {}</li></ul>".format(
                cur_id_patient, patient_id, name, birth_date)
            print(details)
            body += details
            cur_id_patient += 1


    return render_template('index.html', names=names, form=form, body=body)
# def hello_world():
#   return 'Hello, World!'

app.run(host='0.0.0.0', port=8080)