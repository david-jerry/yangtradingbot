import pickle
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Final
import requests
import os
import django

from asgiref.sync import sync_to_async
from apps.accounts.models import CustomUser

from logger import LOGGER

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yangbot.settings')
django.setup()


def save_user_data(user_data):
    # Save user data to pickle file
    user = CustomUser.objects.get_or_create(
        user_data
    )
    return user


def load_user_data(user_id):
    global user_data
    try:
        user_data = CustomUser.objects.get(user_id=user_id)
        return user_data
    except FileNotFoundError:
        user_data = None
        return user_data


def update_user_data(user_id: str, updated_data):
    user_data = load_user_data(user_id)
    if user_data != None:
        CustomUser.objects.filter(user_id=user_id).update(updated_data)
    else:
        LOGGER.info("User not found")
        pass
