# Author: Isaac Robert

from flask import Flask
from flask import request, jsonify
from auth_middleware import token_required
from models import User, Templates
import os, sys, json


app = Flask(__name__)

SECRET_KEY = "robertix"
app.config['SECRET_KEY'] = SECRET_KEY
app.config['DEBUG'] = True

def validate_email_and_password(email, password):
    if "@" not in email and "." not in email:
        return {"email": "invalid"}
    if len(password) < 6:
        return {"password": "invalid"}
    return True


@app.route('/register', methods=['POST', 'GET'])
def register():
    try:
       
        try:
            data = request.json
    
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
                "error": is_valid}
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

@app.route('/login', methods=['POST'])
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

        return jsonify({"message": "Successfully fetched auth token!", "data": str(logged)})
    except Exception as e:
        return jsonify(
            {
            'message': 'Internal server error!',
            'data': None,
            'error': str(e)
            }), 500


@app.route("/template", methods=["POST", "GET"])
@token_required
def insert_template(*args, **kwargs):
    token = request.headers["Authorization"].split(" ")[1]
    if request.method == 'GET':
        try:
            # Get all templates
            templates = Templates().get_all(token)
            if not templates:
                return jsonify(
                    {
                    "message": "No templates available!",
                    "data": templates,
                    }), 404
            return jsonify(
                {
                "message": 'Retieved all templates successfully',
                'data': templates}
                ), 201

        except Exception as e:
            return jsonify(
                {
                'message': 'Internal server error!',
                'data': None,
                'error': str(e)
                }), 500
    elif request.method == 'POST':
        # Create New
        try:
            data = request.json

            if not data:
                return jsonify({
                'message': 'Please provide user details',
                'data': None,
                'error': 'bad request'}), 400

            new_template = Templates().create_new(data, token)
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

@app.route('/template/<string:template_id>',  methods=['POST', 'GET', 'PUT', 'DELETE'])
@token_required
def template(template_id):
    print(template_id)
    token = request.headers["Authorization"].split(" ")[1]
    if request.method == 'GET':
        try:

            # Get a single template
            template = Templates().get_by_id(template_id, token)
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

    elif request.method == 'PUT':
        # Update template
        try:
            data = request.json

            data["_id"] = template_id
            old_template = Templates().update(data, token)
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

    elif request.method == "DELETE":
        try:
            template = Templates().delete(template_id, token)
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
                    "data": None
                }), 201
        except Exception as e:
            return jsonify(
                {
                'message': 'Internal server error!',
                'data': None,
                'error': str(e)
                }), 500

if __name__ == '__main__':
     app.run()




