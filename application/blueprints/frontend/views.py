import datetime
import pandas as pd

from flask import (
    Blueprint,
    render_template,
    request,
    json)

from application.blueprints.frontend.forms import UploadForm

from resource_generator.check_data_page import url_for_harmonised, url_for_converted, url_for_issues, fetch_csv, bounding_box, increase_bounding_box
from resource_generator.data_analyser import DataAnalyser
from resource_generator.collection import CollectionIndex
from resource_generator.issue_mapper import formatIssuesForView, extractIssueData

frontend = Blueprint('frontend', __name__, template_folder='templates')

@frontend.route('/')
def index():
    return render_template('index.html')


def tmp_func_to_be_replaced_with_pipeline():
    tmp_res = "e74aa67d877102504e1598111692480f8078944b8e542b46343d38e38027506c"
    data = fetch_csv(url_for_harmonised(tmp_res))
    issues = pd.read_csv(url_for_issues(tmp_res), sep=",")
    return data, issues


@frontend.route('/check', methods=['GET', 'POST'])
def check():
    form = UploadForm()
    if form.validate_on_submit():
        try:
            # TODO: check file and process
            # TODO: run through the pipeline

            # TO REPLACE ======
            # this bit needs replacing with uploaded file being run through pipeline
            # temporarily get data and issues from a default resource
            data, issues_data = tmp_func_to_be_replaced_with_pipeline()
            # =================
            
            json_data = json.loads(data.to_json(orient='records'))
            issues_json = json.loads(issues_data.to_json(orient='records'))

            # analyse data
            analyser = DataAnalyser(json_data)

            # get the formatted issues
            formatted_issues = formatIssuesForView(extractIssueData(issues_json))

            return render_template('view-data-page.html',
                data=json_data,
                summary=analyser.summary(),
                issues=formatted_issues,
                bbox=increase_bounding_box(bounding_box(data), 1),
                today=datetime.datetime.today().date().strftime('%Y-%m-%d'))
        except FileTypeException as e:
            flash(f'{e}', category='error')
    return render_template('upload.html', form=form)


# set the assetPath variable for use in 
# jinja templates
@frontend.context_processor
def asset_path_context_processor():
    return {'assetPath': '/static/govuk-frontend/assets'}

@frontend.context_processor
def static_path_context_processor():
    return {'static_folder': '/static'}