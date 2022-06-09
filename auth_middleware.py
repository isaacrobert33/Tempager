from functools import wraps
import jwt
from flask import request, abort
from flask import current_app
from models import User

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            token = None
            if "Authorization" in request.headers:
                token = request.headers["Authorization"].split(" ")[1]
                print(token)
            if not token:
                return {
                    "message": "Authentication Token is missing!",
                    "data": None,
                    "error": "Unauthorized"
                }, 401
            try:
                data = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
                current_user = User().get_by_id(data["user_id"], token)
                if current_user is None:
                    return {
                    "message": "Invalid Authentication token!",
                    "data": None,
                    "error": "Unauthorized"
                }, 401
                if not current_user["active"]:
                    abort(403)
            except Exception as e:
                return {
                    "message": "Something went wrong",
                    "data": None,
                    "error": str(e)
                }, 500

            return f(**kwargs)
        except Exception as e:
            return {
                    "message": "Error in token Authentication!",
                    "data": None,
                    "error": str(e)
                }, 500

    return decorated