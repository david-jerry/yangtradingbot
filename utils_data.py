import pickle
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Final
import requests

from asgiref.sync import sync_to_async

from logger import LOGGER


def save_user_data(user_data):
    # Save user data to pickle file
    with open('user_data.pkl', 'wb') as file:
        pickle.dump(user_data, file)
        

def load_user_data():
    global user_data
    try:
        with open('user_data.pkl', 'rb') as file:
            user_data = pickle.load(file)
            return user_data
    except FileNotFoundError:
        user_data = {}
        return user_data

def update_user_data(user_id:str, db_key:str, db_value):
    load_user_data()
    if user_id in user_data:
        user_data[str(user_id)][db_key] = db_value
        # Save the updated user data back to pickle file
        save_user_data(user_data)
        load_user_data()
    else:
        LOGGER.info("User not found")
        pass

