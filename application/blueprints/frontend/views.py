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
    session,
    redirect,
    render_template,
    json,
    send_from_directory,
    url_for,
)

from application.pipeline.tasks import delay_remove_files_thread

from application.blueprints.frontend.forms import UploadForm
from application.pipeline.data_analyser import DataAnalyser
from application.pipeline.issue_formatter import IssueFormatter
from application.pipeline.brownfield_pipeline import pipeline
from application.pipeline.utils import read_and_strip_data, is_data_empty
from application.pipeline.bbox import bounding_box, increase_bounding_box

frontend = Blueprint("frontend", __name__, template_folder="templates")


@frontend.route("/")
def index():
    return render_template("index.html")


@frontend.route("/upload", methods=["GET", "POST"])
def check():
    form = UploadForm()
    if form.validate_on_submit():
        file = request.files["upload"]
        filename = Path(secure_filename(file.filename))
        token = secrets.token_urlsafe(16)
        tokened_filename = filename.with_name(
            filename.stem + "_" + token + filename.suffix
        )
        session["filename"] = file.filename
        session["tokened_filename"] = tokened_filename.name
        file_path = Path(current_app.config["TEMP_DIR"]) / tokened_filename
        harmonised_file_path = file_path.with_name(file_path.stem + "_harmonised.csv")
        issue_file_path = file_path.with_name(file_path.stem + "_issues.csv")
        try:
            file.save(file_path)
            pipeline.process(file_path, harmonised_file_path, issue_file_path)
            session["harmonised_file_name"] = harmonised_file_path.name

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

        return redirect(url_for("frontend.view_data", filename=tokened_filename))

    return render_template("upload.html", form=form)


@frontend.route("/viewdata/<filename>")
def view_data(filename):
    file_path = Path(current_app.config["TEMP_DIR"]) / filename
    harmonised_file_path = file_path.with_name(file_path.stem + "_harmonised.csv")
    issue_file_path = file_path.with_name(file_path.stem + "_issues.csv")
    issues_data = pd.read_csv(issue_file_path, sep=",")
    data = read_and_strip_data(harmonised_file_path)

    # Check if data is empty/valid
    if is_data_empty(data):
        return render_template("process-failed.html")

    json_data = json.loads(data.to_json(orient="records"))
    issues_json = json.loads(issues_data.to_json(orient="records"))

    # analyse data
    analyser = DataAnalyser(json_data)
    session["data_summary"] = analyser.summary()

    # get the formatted issues
    issue_data = IssueFormatter.extract_issue_data(issues_json)
    formatted_issues = IssueFormatter.format_issues_for_view(issue_data)

    return render_template(
        "view-data-page.html",
        includesMap=True,
        filename=session["filename"],
        processed_file=harmonised_file_path.name,
        data=json_data,
        summary=session["data_summary"],
        issues=formatted_issues,
        bbox=increase_bounding_box(bounding_box(data), 1),
        today=datetime.datetime.today().date().strftime("%Y-%m-%d"),
    )


@frontend.route("/next")
def next():
    # only render page if a harmonised file exists
    if "harmonised_file_name" in session:
        return render_template(
            "whats-next.html",
            processed_file=session["harmonised_file_name"],
            tokened_filename=session["tokened_filename"],
            summary=session["data_summary"],
            filename=session["filename"],
        )
    return redirect("/")


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
