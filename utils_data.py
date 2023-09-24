import pickle
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Final
import requests
import os
import django

from asgiref.sync import sync_to_async
from apps.accounts.models import CustomUser, CopyTradeAddresses, Sniper, Txhash, copytradetxhash

from logger import LOGGER

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yangbot.settings')
django.setup()





def save_txhash_copy_data(user_data):
    temp = copytradetxhash.objects.create(
        **user_data
    )
    LOGGER.info(temp)
    return temp
def Load_txhash_copy_data():
    data = copytradetxhash.objects.filter()
    return data
# @sync_to_async
def save_txhash_data(user_data):
    txhash = Txhash.objects.create(
        **user_data
    )
    LOGGER.info()
    return txhash

# @sync_to_async
def load_txhash_data(Txhash1):
    try:
        LOGGER.info("Loading user data")
        LOGGER.info(Txhash)
        user_data = Txhash.objects.filter(Txhash=Txhash1).first()
        LOGGER.info(user_data)
        return user_data
    except FileNotFoundError:
        user_data = None
        return user_data

def load_copy_trade_addresses_copy(address):
    try:
        LOGGER.info("Loading user data")
        LOGGER.info(CopyTradeAddresses)
        print(address)
        trade = CopyTradeAddresses.objects.filter(contract_address=address).first()
        LOGGER.info(trade)
        return trade
    except FileNotFoundError:
        trade = None
        return trade

def address_to_id(contract_address1):
    user_data = CopyTradeAddresses.objects.filter(contract_address =contract_address1)
    data =[]
    if user_data:
        for i in user_data:
            data.append(i.user_id)
    else:
        return None
    return data

def load_user_data_id(user_id):
    try:
        LOGGER.info("Loading user data")
        LOGGER.info(user_id)
        user_data = CustomUser.objects.filter(id=user_id).first()
        LOGGER.info(user_data)
        return user_data
    except FileNotFoundError:
        user_data = None
        return user_data

def load_copytrade_address_user_data_id(address, id):
    try:
        LOGGER.info("Loading copy trade data")
        LOGGER.info(address)
        LOGGER.info(id)
        trade = CopyTradeAddresses.objects.filter(user_id=id, contract_address=address).first()
        LOGGER.info(trade)
        return trade
    except FileNotFoundError:
        trade = None
        return trade

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
def load_copy_trade_address_all(user_id1):
    user = CustomUser.objects.get(user_id=user_id1)
    user_data = CopyTradeAddresses.objects.filter(user=user)
    if user_data:
        temp =[]
        for i in user_data:
            temp.append(i.contract_address)
        return temp
    else:
        return None  
@sync_to_async
def load_copy_trade_all(user_id1):
    user = CustomUser.objects.get(user_id=user_id1)
    user_data = CopyTradeAddresses.objects.filter(user=user)
    if user_data:
        temp =[]
        for i in user_data:
            temp.append(i.name)
        return temp
    else:
        return None
@sync_to_async
def load_copy_trade_addresses_chain(chain1):
    user_data = CopyTradeAddresses.objects.filter(chain =chain1)
    if user_data:
        return user_data
    else:
        return None


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
def update_copy_trade_addresses_ammout(id1, ammount,name1):
    my_object = CopyTradeAddresses.objects.get(user_id=id1, name=name1)
    my_object.amount =Decimal(ammount)
    my_object.save()
    return my_object

@sync_to_async
def update_copy_trade_addresses_slippage(id1, slippage1,name1):
    my_object = CopyTradeAddresses.objects.get(user_id=id1,name=name1)
    my_object.slippage =Decimal(slippage1)
    my_object.save()
    return my_object


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
        trades = Sniper.objects.get(user=user, contract_address=address)
        # Update user_data fields based on updated_data dictionary
        for key, value in updated_data.items():
            setattr(trades, key, value)
        
        trades.save()  # Save the changes to the database
    except CustomUser.DoesNotExist:
        LOGGER.info("Copy trade not found")

        
# @sync_to_async
# def delete_snipes(user_id, chain):
#     try:
#         user = CustomUser.objects.get(user_id=user_id)
#         Sniper.objects.get(user=user, chain=chain).delete()
#         trades = Sniper.objects.filter(user=user, chain=chain) or None
#         return trades
#     except CustomUser.DoesNotExist:
#         LOGGER.info("Copy trade not found")        