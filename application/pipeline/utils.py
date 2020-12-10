import pandas as pd


def read_and_strip_data(file_path):
    data = pd.read_csv(file_path, sep=",")
    # strip spaces introduced to values
    data_frame_trimmed = data.apply(
        lambda x: x.str.strip() if x.dtype == "object" else x
    )
    # strip spaces introduced to column headers
    data_frame_trimmed = data_frame_trimmed.rename(columns=lambda x: x.strip())

    return data_frame_trimmed
