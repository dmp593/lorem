import random
import string

from fastapi import Body, Header


TOKEN_CHARACTERS: str = string.ascii_letters + string.digits
TOKEN_MIN_LENGTH: int = 24 # Forbids the access to system dbs (admin, local, config) and protects against brute-force
TOKEN_MAX_LENGTH: int = 63 # https://www.mongodb.com/docs/manual/reference/limits/#mongodb-limit-Length-of-Database-Names


TokenLengthBody = Body(
    embed=True,
    ge=TOKEN_MIN_LENGTH,
    le=TOKEN_MAX_LENGTH,
    default=32
)


TokenHeader = Header(
    min_length=TOKEN_MIN_LENGTH, 
    max_length=TOKEN_MAX_LENGTH, 
    # https://www.mongodb.com/docs/manual/reference/limits/#mongodb-limit-Restrictions-on-Database-Names-for-Unix-and-Linux-Systems
    regex=r'^\w*$',
    title="Authorization Token to access your private database."
)


def generate(length) -> str:
    return ''.join(random.choice(TOKEN_CHARACTERS) for _ in range(length))
