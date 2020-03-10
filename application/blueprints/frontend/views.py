import datetime

from flask import (
    Blueprint,
    render_template,
    request,
    json)

frontend = Blueprint('frontend', __name__, template_folder='templates')

@frontend.route('/')
def index():
    return render_template('index.html')


@frontend.route('/upload')
def upload():
    return render_template('upload.html')
