import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DB_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevConf(Config):
    SECRET_KEY = "SECRET"

class ProdConf(Config):
    SECRET_KEY = os.getenv("SECRET_KEY")