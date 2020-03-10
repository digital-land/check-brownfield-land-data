import datetime

from flask import (
    Blueprint,
    render_template,
    request,
    json)

from application.blueprints.frontend.forms import UploadForm

frontend = Blueprint('frontend', __name__, template_folder='templates')

@frontend.route('/')
def index():
    return render_template('index.html')


@frontend.route('/check', methods=['GET', 'POST'])
def check():
    form = UploadForm()
    if form.validate_on_submit():
        try:
            # TODO: check file and process
            # TODO: run through the pipeline
            return render_template('upload.html', form=form)
        except FileTypeException as e:
            flash(f'{e}', category='error')
    return render_template('upload.html', form=form)
