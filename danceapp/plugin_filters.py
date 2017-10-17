from flask import Markup
from danceapp import app
from danceapp.plugins import dispatch


@app.template_filter('html_dispatch')
def html_dispatch(storyline, function):
    values = dispatch(function, storyline)
    return Markup(''.join(values))
