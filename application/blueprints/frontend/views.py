import datetime
import os
from pathlib import Path
import pandas as pd
import secrets
from werkzeug.utils import secure_filename
from flask import (
    request,
    current_app,
    Blueprint,
    render_template,
    json,
    send_from_directory,
)

from application.pipeline.tasks import delay_remove_files_thread

from application.blueprints.frontend.forms import UploadForm
from application.pipeline.data_analyser import DataAnalyser
from application.pipeline.issue_formatter import IssueFormatter
from application.pipeline.brownfield_pipeline import pipeline
from application.pipeline.utils import read_and_strip_data

frontend = Blueprint("frontend", __name__, template_folder="templates")


@frontend.route("/")
def index():
    return render_template("index.html")


@frontend.route("/check", methods=["GET", "POST"])
def check():
    form = UploadForm()
    if form.validate_on_submit():
        file = request.files["upload"]
        filename = Path(secure_filename(file.filename))
        token = secrets.token_urlsafe(16)
        tokened_filename = filename.with_name(filename.stem + "_" + token + filename.suffix)
        file_path = Path(current_app.config["TEMP_DIR"]) / tokened_filename
        harmonised_file_path = file_path.with_name(file_path.stem + "_harmonised.csv")
        issue_file_path = file_path.with_name(file_path.stem + "_issues.csv")
        try:
            file.save(file_path)
            pipeline.process(file_path, harmonised_file_path, issue_file_path)
            issues_data = pd.read_csv(issue_file_path, sep=",")
            data = read_and_strip_data(harmonised_file_path)

            json_data = json.loads(data.to_json(orient="records"))
            issues_json = json.loads(issues_data.to_json(orient="records"))

            # analyse data
            analyser = DataAnalyser(json_data)

            # get the formatted issues
            issue_data = IssueFormatter.extract_issue_data(issues_json)
            formatted_issues = IssueFormatter.format_issues_for_view(issue_data)

            if current_app.config["FILE_TIME_LIMIT"]:
                delay_remove_files_thread(
                    [file_path, harmonised_file_path, issue_file_path],
                    int(current_app.config["FILE_TIME_LIMIT"]),
                )
        except Exception as e:
            if file_path.exists():
                os.remove(file_path)
            if harmonised_file_path.exists():
                os.remove(harmonised_file_path)
            if issue_file_path.exists():
                os.remove(issue_file_path)
            raise type(e)(
                str(e) + ". Failed to process file uploaded by user"
            ).with_traceback(e.__traceback__)

        return render_template(
            "view-data-page.html",
            processed_file=harmonised_file_path.name,
            data=json_data,
            summary=analyser.summary(),
            issues=formatted_issues,
            bbox={},  # increase_bounding_box(bounding_box(data), 1),
            today=datetime.datetime.today().date().strftime("%Y-%m-%d"),
        )

    return render_template("upload.html", form=form)


@frontend.route("/processed/<filename>")
def upload(filename):
    return send_from_directory(current_app.config["TEMP_DIR"], filename)


# set the assetPath variable for use in
# jinja templates
@frontend.context_processor
def asset_path_context_processor():
    return {"assetPath": "/static/govuk-frontend/assets"}


@frontend.context_processor
def static_path_context_processor():
    return {"static_folder": "/static"}
