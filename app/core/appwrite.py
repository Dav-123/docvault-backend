from appwrite.client import Client
from appwrite.services.account import Account
from appwrite.services.databases import Databases
from appwrite.services.storage import Storage
from app.config import settings

# Initialize Appwrite Client
client = Client()
client.set_endpoint(settings.APPWRITE_ENDPOINT)
client.set_project(settings.APPWRITE_PROJECT_ID)
client.set_key(settings.APPWRITE_API_KEY)

# Initialize Services
account = Account(client)
databases = Databases(client)
storage = Storage(client)


def get_appwrite_client():
    """Get Appwrite client instance"""
    return client


def get_databases():
    """Get Appwrite databases instance"""
    return databases


def get_account():
    """Get Appwrite account instance"""
    return account
