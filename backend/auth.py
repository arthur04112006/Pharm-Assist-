from flask import request, jsonify

def require_auth(fn):
    def wrapper(*args, **kwargs):
        if request.method == "OPTIONS":
            return ("", 204)
        if request.headers.get("Authorization", "").startswith("Bearer "):
            return fn(*args, **kwargs)
        return jsonify({"error": "unauthorized"}), 401
    wrapper.__name__ = fn.__name__
    return wrapper
