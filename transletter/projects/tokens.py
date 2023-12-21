from django.conf import settings
import jwt

__all__ = ()


def generate_token(username, project_id):
    payload = {
        "username": username,
        "project_id": project_id,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def decode_token(token):
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    username = payload["username"]
    project_id = payload["project_id"]
    return username, project_id
