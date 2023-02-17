import random
import re
import string

from fastapi.datastructures import Headers

from app.core import exceptions


TOKEN_CHARACTERS: str = string.ascii_letters + string.digits
TOKEN_RE_PATTERN: str = r"^\w*$"
TOKEN_MIN_LENGTH: int = 24 # Forbids the access to system dbs (admin, local, config) and protects against brute-force
TOKEN_MAX_LENGTH: int = 63 # https://www.mongodb.com/docs/manual/reference/limits/#mongodb-limit-Length-of-Database-Names


def extract(headers: Headers):
    token = None
    
    if "authorization" in headers:
        authorization = headers["authorization"]
        
        if authorization.startswith("Bearer "):
            token = authorization[7:]

        elif authorization.startswith("Token "):
            token = authorization[6:]
    
    elif "x-token" in headers:
        token = headers["x-token"]

    elif "x-app-id" in headers:
        token = headers["x-app-id"]

    elif "x-api-key" in headers:
        token = headers["x-api-key"]

    elif "host" in headers:
        host = headers["host"]
        
        if "." in host:
            stop = host.index(".")
            token = host[:stop]

    validate(token, raise_error=True)

    return token


def validate(token: str, raise_error: bool = True) -> bool:
    if not isinstance(token, str):
        raise exceptions.Unauthorized("Invalid Token: not provided")
    
    token_len = len(token)

    if token_len < TOKEN_MIN_LENGTH:
        if not raise_error: return False
        raise exceptions.Unauthorized(f"Invalid Token: minimum length is {TOKEN_MIN_LENGTH} characters")

    if token_len > TOKEN_MAX_LENGTH:
        if not raise_error: return False
        raise exceptions.Unauthorized(f"Invalid Token: maximum length is {TOKEN_MAX_LENGTH} characters")

    if not re.match(TOKEN_RE_PATTERN, token):
        if not raise_error: return False
        raise exceptions.Unauthorized("Invalid Token: only alphanumeric characters are allowed")

    return True


def generate(length: int) -> str:
    return "".join(random.choice(TOKEN_CHARACTERS) for _ in range(length))
