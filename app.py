from flask import Flask
from flask_restful import Resource, Api
from flask import request, jsonify
from auth_middleware import token_required
from models import User, Templates
import os, sys, json


app = Flask(__name__)
api = Api(app)
os.environ['SECRET_KEY'] = 'ayowumi33'
SECRET_KEY = os.environ['SECRET_KEY']
app.config['SECRET_KEY'] = SECRET_KEY

def validate_email_and_password(email, password):
    if "@" not in email and "." not in email:
        return {"email": "invalid"}
    if len(password) < 6:
        return {"password": "invalid"}
    return True


@app.route('/register', methods=['POST', 'GET'])
def register():
    try:
        print(request.method)
        try:
            data = request.json
            print(data)
        except Exception as e:
            return jsonify({'message': 'error', 'error': str(e)}), 500
        
        if not data:
            return jsonify({
                'message': 'Please provide user details', 
                'data': None,
                'error': 'bad request'}), 400
                
        is_valid = validate_email_and_password(data["email"], data["password"])
        
        if type(is_valid) == dict:

            return jsonify({
                "message": "Invalid sign-up details",
                "data": None,
                "error": is_vaild}
                ), 400
            
        new_user = User().register(data)
        if not new_user:
            return jsonify(
                {
                'message': 'User already exists!',
                'data': None,
                'error': 'bad request'
                }), 400
        return jsonify(
                {'message': 'Registered Successfully!', 'data': new_user}
            ), 201
    except Exception as e:
        return jsonify(
            {
            'message': 'Internal server error!',
            'data': None,
            'error': str(e)
            }), 500

@app.route('/login', methods=['POST', 'GET'])
def login():
    try:
        credentials = request.json
        if not credentials:
            return jsonify({
                'message': 'Please provide user details', 
                'data': None,
                'error': 'bad request'}), 400
        logged = User().login(
            credentials["email"],
            credentials["password"])
        
        if not logged:
            return jsonify({"message": "Invalid login!"}), 401
        
        return jsonify({"message": "Successfully fetched auth token!", "data": logged})
    except Exception as e:
        return jsonify(
            {
            'message': 'Internal server error!',
            'data': None,
            'error': str(e)
            }), 500

@app.route('/template/<string:template_id>',  methods=['POST', 'GET', 'PUT', 'DELETE'])
@token_required
def template(template_id):
    if request.method == 'GET':
        try:
            if template_id == 'all':
                # Get all templates
                templates = Templates().get_all()
                return jsonify(
                    {
                    "message": 'Retieved all templates successfully', 
                    'data': templates}
                    ), 201
            else:
                # Get a single template
                template = Templates().get_by_id(template_id)
                if not template:
                    return jsonify(
                        {
                        "message": "Template does not exists!",
                        "data": None,
                        "error": "bad request"
                        }), 400
                        
                return jsonify(
                    {'message': 'Template retrieved!', 'data': template})
        except Exception as e:
            return jsonify(
                {
                'message': 'Internal server error!',
                'data': None,
                'error': str(e)
                }), 500
    elif request.method == 'POST':
        try:
            data = request.json
            new_template = Templates().create_new(data)
            if not new_template:
                return jsonify(
                    {
                    "message": "Invalid template format!",
                    "data": None,
                    "error": "bad request"
                    }), 400

            return jsonify({'message': "Successfully created new template!", 'data': new_template})
        except Exception as e:
            return jsonify(
                {
                'message': 'Internal server error!',
                'data': None,
                'error': str(e)
                }), 500
    elif request.method == 'PUT':
        try:
            old_template = Templates().update(data)
            if not old_template:
                return jsonify(
                    {
                        "message": "Template does not exists!",
                        "data": None,
                        "error": "Not found"
                    }), 404

            return jsonify(
                {
                    "message": "Successfully updated template!",
                    "data": old_template
                }), 201

        except Exception as e:
            return jsonify(
                {
                'message': 'Internal server error!',
                'data': None,
                'error': str(e)
                }), 500
    elif request.method == 'DELETE':
        try:
            template = Templates().delete(template_id)
            if not template:
                return jsonify(
                    {
                        "message": "Template does not exists!",
                        "data": None,
                        "error": "Not found"
                    }), 404

            return jsonify(
                {
                    "message": "Successfully deleted template!",
                    "data": template
                }), 201
        except Exception as e:
            return jsonify(
                {
                'message': 'Internal server error!',
                'data': None,
                'error': str(e)
                }), 500

