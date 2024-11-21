> [!IMPORTANT]
> This application is deprecated

# Application replacment

This application has been replaced by [Submit and update your planning data](https://submit.planning.data.gov.uk/)

The original application running in Heroku [Check your brownfield land data](https://brownfield-sites-validator.herokuapp.com/) redirects
to the new application.

The redirection is handled in the [application/factory.py](application/factory.py) file using a "before_request" decorator to intercept all requests.

Automatic deploys of this code to Heroku has been disabled

## Check brownfield land data

## Getting started

Make a virtualenv for the project and install python dependencies

    make

Start the application

    flask run

## Integrate pipeline

Next step is to incorporate the pipeline. Currently it works by using a default resource (in this case one from Harrogate). It pulls the resource and the associated issues files from github and renders the page.

We need to strip that out and make it work with the pipeline which should; take an uploaded file (ideally .csv but maybe .xlsx), run through pipeline and pass the processed data and the outputted issues file to the rendering part.
