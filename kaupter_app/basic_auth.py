from functools import wraps
from flask import request, current_app as app


def require_appkey(view_function):
    @wraps(view_function)
    # the new, post-decoration function. Note *args and **kwargs here.
    def decorated_function(*args, **kwargs):
        if request.headers.get('x-api-key') == app.config['TOKEN']:
            return view_function(*args, **kwargs)
        else:
   		    return 'not authorized to use this service', 401
    return decorated_function