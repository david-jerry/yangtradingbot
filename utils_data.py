import pickle
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Final
import requests
import os
import django

from asgiref.sync import sync_to_async
from apps.accounts.models import CustomUser, CopyTradeAddresses

from logger import LOGGER

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yangbot.settings')
django.setup()

@sync_to_async
def save_user_data(user_data):
    LOGGER.info(user_data)
    # Save user data to pickle file
    user = CustomUser.objects.create(
        **user_data
    )
    LOGGER.info(user)
    return user

@sync_to_async
def save_copy_trade_address(user_id, name, address, chain, on):
    user = CustomUser.objects.get(user_id=user_id)
    trade = CopyTradeAddresses.objects.create(user=user, name=name, contract_address=address, chain=chain, on=on)
    return trade

@sync_to_async
def load_user_data(user_id):
    try:
        LOGGER.info("Loading user data")
        LOGGER.info(user_id)
        user_data = CustomUser.objects.filter(user_id=user_id).first()
        LOGGER.info(user_data)
        return user_data
    except FileNotFoundError:
        user_data = None
        return user_data

@sync_to_async
def load_copy_trade_addresses(user_id, chain):
    user = CustomUser.objects.get(user_id=user_id)
    trades = CopyTradeAddresses.objects.filter(user=user, chain=chain) or None
    return trades


@sync_to_async
def update_user_data(user_id: str, updated_data):
    try:
        user_data = CustomUser.objects.get(user_id=user_id)
        
        # Update user_data fields based on updated_data dictionary
        for key, value in updated_data.items():
            setattr(user_data, key, value)
        
        user_data.save()  # Save the changes to the database
    except CustomUser.DoesNotExist:
        LOGGER.info("User not found")


@sync_to_async
def update_copy_trade_addresses(user_id, name, chain, updated_data):
    try:
        user = CustomUser.objects.get(user_id=user_id)
        trades = CopyTradeAddresses.objects.get(user=user, name=name, chain=chain)
        # Update user_data fields based on updated_data dictionary
        for key, value in updated_data.items():
            setattr(trades, key, value)
        
        trades.save()  # Save the changes to the database
    except CustomUser.DoesNotExist:
        LOGGER.info("Copy trade not found")
        
@sync_to_async
def delete_copy_trade_addresses(user_id, name, chain):
    try:
        user = CustomUser.objects.get(user_id=user_id)
        CopyTradeAddresses.objects.get(user=user, name=name, chain=chain).delete()
        trades = CopyTradeAddresses.objects.filter(user=user, chain=chain) or None
        return trades
    except CustomUser.DoesNotExist:
        LOGGER.info("Copy trade not found")