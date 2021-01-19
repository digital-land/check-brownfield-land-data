import requests
import os

SLACK_URL = os.environ.get("SLACK_WEBHOOK_URL")


def smoke_test(url, test_text):
    resp = requests.get(url).text
    if test_text in resp.lower():
        requests.post(SLACK_URL, json={"text":"{} appears to be up!".format(url)})


if __name__ == "__main__":
    smoke_test("https://brownfield-sites-validator.herokuapp.com/", "brownfield land")

