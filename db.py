from dotenv import load_dotenv
from psycopg2 import connect
import os

load_dotenv()

def get_connection():
    return connect(os.getenv("DATABASE_URL"))
