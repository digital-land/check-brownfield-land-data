import datetime
import pandas as pd
import os
from flask import (
    current_app,
    Blueprint,
    render_template,
    json)

from application.blueprints.frontend.forms import UploadForm
from application.utils.data_analyser import DataAnalyser
from application.utils.issue_formatter import IssueFormatter

frontend = Blueprint('frontend', __name__, template_folder='templates')

@frontend.route('/')
def index():
    return render_template('index.html')


def tmp_func_to_be_replaced_with_pipeline():
    tmp_res = "e74aa67d877102504e1598111692480f8078944b8e542b46343d38e38027506c.csv"
    harmonised_file = os.path.join(os.path.dirname(current_app.instance_path), 'temp', 'harmonised', tmp_res)
    issue_file = os.path.join(os.path.dirname(current_app.instance_path), 'temp', 'issue', tmp_res)

    data = pd.read_csv(harmonised_file, sep=",")
    # strip spaces introduced to values
    data_frame_trimmed = data.apply(
        lambda x: x.str.strip() if x.dtype == "object" else x
    )
    # strip spaces introduced to column headers
    data_frame_trimmed = data_frame_trimmed.rename(columns=lambda x: x.strip())

    issues = pd.read_csv(issue_file, sep=",")
    return data_frame_trimmed, issues


@frontend.route('/check', methods=['GET', 'POST'])
def check():
    form = UploadForm()
    if form.validate_on_submit():
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
            issue_data = IssueFormatter.extract_issue_data(issues_json)
            formatted_issues = IssueFormatter.format_issues_for_view(issue_data)

            return render_template('view-data-page.html',
                data=json_data,
                summary=analyser.summary(),
                issues=formatted_issues,
                bbox={}, #increase_bounding_box(bounding_box(data), 1),
                today=datetime.datetime.today().date().strftime('%Y-%m-%d'))

    return render_template('upload.html', form=form)


# set the assetPath variable for use in 
# jinja templates
@frontend.context_processor
def asset_path_context_processor():
    return {'assetPath': '/static/govuk-frontend/assets'}

@frontend.context_processor
def static_path_context_processor():
    return {'static_folder': '/static'}