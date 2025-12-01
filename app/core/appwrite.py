from appwrite.client import Client
from appwrite.services.account import Account
from appwrite.services.databases import Databases
from appwrite.services.storage import Storage
from appwrite.services.tablesdb import TablesDB
from appwrite.services.users import Users
from app.config import settings

# Initialize Appwrite Client
client = Client()
client.set_endpoint(settings.APPWRITE_ENDPOINT)
client.set_project(settings.APPWRITE_PROJECT_ID)
client.set_key(settings.APPWRITE_API_KEY)

# Initialize Services
account = Account(client)
users = Users(client)
databases = Databases(client)
tablesdb = TablesDB(client)
storage = Storage(client)


def get_appwrite_client():
    """Get Appwrite client instance"""
    return client


def get_users():
    """Get Appwrite users instance"""
    return users


def get_databases():
    """Get Appwrite databases instance"""
    return databases


def get_tablesdb():
    """Get Appwrite table instance"""
    return tablesdb


def get_account():
    """Get Appwrite account instance"""
    return account


def get_storage():
    """Get Appwrite storage instance"""
    return storage
