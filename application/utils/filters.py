import validators

# takes a string, chars to strip off, chars to add, the count
def pluralise(str, str_off, str_on, count):
    strip_count = -1*len(str_off) if len(str_off) > 0 else len(str)
    if count > 1 or count == 0:
        return str[:strip_count]+str_on
    else:
        return str


def check_for_multiple(str):
    if "¦" in str:
        return str.split("¦")
    elif "|" in str:
        return str.split("|")
    return str


def is_valid_uri(uri):
    if validators.url(uri):
        return True
    return False