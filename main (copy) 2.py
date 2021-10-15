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
    name = StringField('', validators=[DataRequired()])
    submit = SubmitField('Find')

class Patient:
    def __init__(self, patient_id, name, birth_date, conditions):
        self.patient_id = patient_id
        self.name = name
        self.birth_date = birth_date
        self.conditions = conditions
        self.len_conditions = len(conditions)

class Condition:
    def __init__(self, id, name, recordedDate):
        self.id = id
        self.name = name
        self.recordedDate = recordedDate


# views

@app.route('/', methods=['GET', 'POST'])
def index():
    # names = get_names(ACTORS)
    names = ['Ken', 'Ella']
    # you must tell the variable 'form' what you named the class, above
    # 'form' is the variable name used in this template: index.html

    form = NameForm()
    body = "<br><h2>Results success!</h2><br>"
    # return body
    # return render_template('index.html', names=names, form=form, body=body)
    if form.validate_on_submit():
        name = form.name.data
        patients_template = []

        smart = client.FHIRClient(settings=smart_defaults)
        import fhirclient.models.patient as p

        search = p.Patient.where(struct={'_count': bytes('100', 'utf-8'), 'family': name})
        # search = p.Patient.where(struct={'family': name})
        patients = search.perform_resources(smart.server)
        # print(patients)
        cur_id_patient = 1
        for patient_this in patients:
            patient_id = patient_this.id.encode('ascii', 'ignore')
            import fhirclient.models.condition as condition
            search_condition = condition.Condition.where(struct={'patient': patient_id})
            # search_condition = condition.Condition.where(struct={'patient': '12724067'})
            conditions = search_condition.perform_resources(smart.server)
            print(conditions)
            conditions_template = []
            for condition_this in conditions:
                condition_id = condition_this.id.encode('ascii', 'ignore')
                recordedDate = "None"
                if condition_this.recordedDate is not None:
                    recordedDate = condition_this.recordedDate.isostring
                name = condition_this.code.text
                # print(recordedDate)
                conditions_template.append(Condition(condition_id, name, recordedDate))

            birth_date = "None"
            if patient_this.birthDate is not None:
                birth_date = patient_this.birthDate.isostring
            name = smart.human_name(patient_this.name[0])
            details = "<p>Patient details #{}<ul><li>ID: {}</li><li>Full Name: {}</li><li>Birth date: {}</li></ul>".format(
                cur_id_patient, patient_id, name, birth_date)
            print(details)
            body += details

            patients_template.append(Patient(patient_id, name, birth_date, conditions_template))
            cur_id_patient += 1

        # if name.lower() in names:
        #     # empty the form field
        #     form.name.data = ""
        #     # id = get_id(ACTORS, name)
        #     # # redirect the browser to another route and template
        #     # return redirect( url_for('actor', id=id) )
        # else:
        #     body += "That actor is not in our database."
        return render_template('index.html', names=names, form=form,
                               patients=patients_template, len_patients=len(patients_template))
    else:
        return render_template('index.html', names=names, form=form,
                               patients=[], len_patients=0)


app.run(host='0.0.0.0', port=8080)