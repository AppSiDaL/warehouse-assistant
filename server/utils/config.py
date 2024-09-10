import os
from dotenv import load_dotenv

load_dotenv()


ENV = os.getenv('ENV', 'development')

if ENV == 'development':
    DB_URL = os.getenv('DB_URL_DEV')
elif ENV == 'testing':
    DB_URL = os.getenv('DB_URL_TEST')

    
SECRET_KEY = os.environ.get("SECRET_KEY")
ACCESS_TOKEN_EXPIRE_MINUTES = os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES")