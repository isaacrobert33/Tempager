from pymongo import MongoClient
from flask import current_app as app
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import os
import sys, bson


try:
    import dns
except ImportError:
    print(os.system("pip install dnspython==2.2.1"))
    import dns
client = MongoClient("mongodb+srv://isaacrobert:ayowumi33@cluster0.z1j5f.mongodb.net/?retryWrites=true&w=majority")

db = client.db
print("[*] connection to mongodb established successfully...")



def validate_template(data):
    kwd = ["template_name", "subject", "body"]
    for i in kwd:
        if i not in data.keys():
            return False

    return True

class Templates:
    def __init__(self):
        pass

    def create_new(self, template_data):
        is_valid = validate_template(template_data)
        if not is_valid:
            return
        new_template = db.templates.insert_one(template_data)
        return self.get_by_id(new_template.inserted_id)

    def get_all(self):
        templates = db.templates.find({})
        return [{**template, "_id": str(template['_id'])} for template in templates]

    def get_by_id(self, template_id):
        template = db.templates.find_one({'_id': bson.ObjectId(template_id)})
        if not template:
            return
        template['_id'] = str(template['_id'])
        return template

    def get_by_name(self, template_name):
        template = db.templates.find_one({'template_name': template_name})
        if not template:
            return
        template['_id'] = str(template['_id'])
        return template

    def update(self, data):
        if not self.get_by_id(data['_id']):
            return
        template = db.templates.update_one(
            {'template_name': data['template_name']},
            {'$set': data}
        )
        return self.get_by_id(data['_id'])

    def delete(self, template_id):
        if not self.get_by_id(template_id):
            return
        template = db.templates.delete_one({'_id': bson.ObjectId(template_id)})
        return template




class User:
    def __init__(self) -> None:
        self.current_users = []

    def register(self, data: dict):
        if self.get_by_email(data["email"]):
            return

        data["active"] = True
        data["password"] = self.encrypt_password(data["password"])
        new_user = db.users.insert_one(data)
        self.set_account_status(new_user.inserted_id, True)
        return self.get_by_id(new_user.inserted_id).pop("password")

    def login(self, email: str, password: str):
        user = self.get_by_email(email)
        if not user or not check_password_hash(user["password"], password):
            return
        user.pop("password")
        user["token"] = str(jwt.encode(
                    {"user_id": user["_id"]},
                    app.config['SECRET_KEY'],
                    algorithm="HS256"
                    ))
        self.set_account_status(user['_id'], True)

        return user

    def logout(self, email):
        user = self.get_by_email(email)
        if not user:
            return
        self.set_account_status(str(user['_id']), False)
        return self.get_by_email(email).pop("password")

    def set_account_status(self, user_id, status):
        user = db.users.update_one(
            {"_id": bson.ObjectId(user_id)},
            {"$set": {"active": status}}
            )
        return self.get_by_id(user_id).pop("password")

    def encrypt_password(self, password: str):
        return generate_password_hash(password)

    def get_by_email(self, email: str):
        user = db.users.find_one({'email': email})
        if not user:
            return
        user['_id'] = str(user['_id'])
        return user

    def get_by_id(self, user_id):
        user = db.users.find_one({'_id': bson.ObjectId(user_id)})
        if not user:
            return
        user['_id'] = str(user['_id'])
        return user




