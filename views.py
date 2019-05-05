from flask import Blueprint, request, jsonify

main = Blueprint('main', __name__)

@main.route('/about')
def index():
	return "Solomo API!"

@main.route('/api/v1.0/interror')
def internal_error():
    abort(500)

def format_response(payload):
    if payload == "[]": 
        return respond({ValueError("No match found"), 204})
    else:
        return respond(None, payload)

def respond(err, res):
    response = {
        'statusCode': err["status"] if err else '200',
        'data': err["message"] if err else res,
        'headers': {
            'Content-Type': 'application/json',
        },
    }

    return jsonify(response)
