"""Module for generating, hashing, and managing passwords.
Includes utils such as generate_hash, hash_password, etc"""
import secrets
import string

import bcrypt

def hash_password(password: str) -> tuple[str,str]:
    """From a given password, hash it and return the hash and a salt"""
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8'), salt.decode('utf-8')


def verify_password(hashed_password: str, salt: str, input_password: str):
    """Check if a password with salt matches the hash"""
    input_password_hash = bcrypt.hashpw(input_password.encode('utf-8'), salt.encode('utf-8'))
    return input_password_hash == hashed_password.encode('utf-8')

def generate_hash(length=16):
    """Generate a random string safely"""
    alphabet = string.ascii_letters + string.digits
    secure_string = ''.join(secrets.choice(alphabet) for _ in range(length))
    return secure_string
