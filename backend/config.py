import os
from datetime import timedelta
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "ecommerce.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "dev-secret-key"

    JWT_SECRET_KEY = "jwt-secret-key"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
