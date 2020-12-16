from math import cos, radians
import pandas as pd

# roughly increase the size of the bounding box
# considers global to be perfect sphere
# see: https://stackoverflow.com/questions/4000886/gps-coordinates-1km-square-around-a-point
def increase_bounding_box(bbox, kms):
    earth_circumf_km = 40075
    # calculate the latitude difference
    lat_diff = kms * (360 / earth_circumf_km)
    # calculate the longitude difference
    lat_in_rads = radians(bbox[2])
    line_of_long = cos(lat_in_rads) * earth_circumf_km
    long_diff = kms * (360 / line_of_long)
    return (
        (bbox[0] - long_diff),
        (bbox[1] + long_diff),
        (bbox[2] - lat_diff),
        (bbox[3] + lat_diff),
    )


def bounding_box_from_dataframe(df):
    min_lng = df.GeoX.min()
    max_lng = df.GeoX.max()
    min_lat = df.GeoY.min()
    max_lat = df.GeoY.max()
    return (min_lng, max_lng, min_lat, max_lat)


def bounding_box(d):
    df = d
    if isinstance(d, dict):
        df = pd.DataFrame(d)
    return bounding_box_from_dataframe(df)