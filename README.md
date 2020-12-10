# Check brownfield land data

## Getting started

Make a virtualenv for the project and install python dependencies

    make

Start the application

    flask run

## Integrate pipeline

Next step is to incorporate the pipeline. Currently it works by using a default resource (in this case one from Harrogate). It pulls the resource and the associated issues files from github and renders the page.

We need to strip that out and make it work with the pipeline which should; take an uploaded file (ideally .csv but maybe .xlsx), run through pipeline and pass the processed data and the outputted issues file to the rendering part.
