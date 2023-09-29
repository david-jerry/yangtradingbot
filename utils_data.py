import pickle
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Final
import requests
import os
import django

from asgiref.sync import sync_to_async
from apps.accounts.models import CustomUser, CopyTradeAddresses, Sniper

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
def save_sniper(user_id, address, chain):
    user = CustomUser.objects.get(user_id=user_id)
    snipe = Sniper.objects.create(user=user, contract_address=address, chain=chain)
    return snipe


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
def load_sniper_data(user_data):
    try:
        LOGGER.info("Loading sniper data")
        if user_data.snipes != None:
            sniper = Sniper.objects.filter(user=user_data, contract_address__iexact=user_data.snipes.first().contract_address).first()
            LOGGER.info(sniper)
            return sniper
        return None
    except FileNotFoundError:
        sniper = None
        return sniper

@sync_to_async
def load_next_sniper_data(sniper_id):
    try:
        LOGGER.info("Loading sniper data")
        if sniper_id != None:
            next_sniper = Sniper.objects.filter(id__gt=sniper_id).order_by('id').first()
            LOGGER.info(next_sniper)
            return next_sniper
        return None
    except FileNotFoundError:
        next_sniper = None
        return next_sniper
    
@sync_to_async
def load_previous_sniper_data(sniper_id):
    try:
        LOGGER.info("Loading sniper data")
        if sniper_id != None:
            previous_sniper = Sniper.objects.filter(id__lt=sniper_id).order_by('id').first()
            LOGGER.info(previous_sniper)
            return previous_sniper
        return None
    except FileNotFoundError:
        previous_sniper = None
        return previous_sniper    

@sync_to_async
def remove_sniper(user_data, sniper_id):
    try:
        Sniper.objects.filter(id=sniper_id).delete()
        return Sniper.objects.filter(user=user_data).first()
    except Sniper.DoesNotExist:
        LOGGER.info("Snipers not found")
        return None
    
    
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
        
        
@sync_to_async
def update_snipes(user_id, address, updated_data):
    try:
        user = CustomUser.objects.get(user_id=user_id)
        
        try:
            trades = Sniper.objects.get(user=user, contract_address=address)
            # Update user_data fields based on updated_data dictionary
            for key, value in updated_data.items():
                setattr(trades, key, value)
            
            trades.save()  # Save the changes to the database
        except Exception as e:
            LOGGER.info(e)
    except CustomUser.DoesNotExist:
        LOGGER.info("Snipper account empty")

        
# @sync_to_async
# def delete_snipes(user_id, chain):
#     try:
#         user = CustomUser.objects.get(user_id=user_id)
#         Sniper.objects.get(user=user, chain=chain).delete()
#         trades = Sniper.objects.filter(user=user, chain=chain) or None
#         return trades
#     except CustomUser.DoesNotExist:
#         LOGGER.info("Copy trade not found")        