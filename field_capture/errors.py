from flask import (
        render_template
)

def page_not_found(e):
    return render_template('errors/404.html', message='Page not found'), 404

def my_custom_error(template, message=''):
    return render_template(template, message=message)


