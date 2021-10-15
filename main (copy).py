
from flask import Flask, render_template
# from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

app = Flask('app')

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
    body = "<br><h2>Results success!</h2><br>"
    if form.validate_on_submit():
        name = form.name.data

        smart = client.FHIRClient(settings=smart_defaults)

    return render_template('index.html', names=names, form=form, body=body)
# def hello_world():
#   return 'Hello, World!'

app.run(host='0.0.0.0', port=8080)