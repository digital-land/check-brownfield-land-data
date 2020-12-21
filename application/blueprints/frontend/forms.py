from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed


class UploadForm(FlaskForm):

    upload = FileField(
        "file",
        validators=[
            FileRequired(),
            FileAllowed(
                ["csv", "xlsx", "xlsm"],
                message="You should upload a file with the extension .csv, .xlsx or .xlsm",
            ),
        ],
    )
