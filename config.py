import os
from dotenv import load_dotenv

load_dotenv()

CHANNEL_ACCESS_TOKEN = os.environ.get("CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET = os.environ.get("CHANNEL_SECRET")

LIFF_TASK_TOOL = "https://liff.line.me/1660700459-XZKAApq7"
LIFF_REFLECT_TASK = "https://liff.line.me/1660700459-Dgw33JG5"
LIFF_REFLECT_HW = "https://liff.line.me/1660700459-lWN44Az0"

DB_USERNAME = os.environ.get("DB_USERNAME")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_NAME = os.environ.get("DB_NAME")

MONGODB_URL=f"mongodb+srv://{DB_USERNAME}:{DB_PASSWORD}@cluster.hv4wqvd.mongodb.net/?retryWrites=true&w=majority"

header = {"content-type": "application/json; charset=UTF-8","Access-Control-Allow-Origin":"*","Access-Control-Allow-Methods":"*","Access-Control-Allow-Credentials":"true","Access-Control-Allow-Header":"*"}